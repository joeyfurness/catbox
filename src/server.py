"""
server.py — Telnet TUI server for Schrödinger's Catbox

Accepts multiple simultaneous telnet connections.  All connections share
ONE CatBox instance — one cat, many observers.

Each client gets:
  - A fixed-position 80x24 TUI (content stays in place, no scrolling)
  - A background render thread that drives idle animations and live stats
  - NAWS negotiation to detect the client's terminal size

Python 3 stdlib only.  No external dependencies.
"""

import socket
import socketserver
import subprocess
import threading
import random
import time
import sys
import os

# ---------------------------------------------------------------------------
# Path setup — allow running from repo root or src/ directly
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import art
import tui
from cat_state import CatBox, State

# ---------------------------------------------------------------------------
# Telnet protocol constants
# ---------------------------------------------------------------------------

IAC  = bytes([255])   # Interpret As Command
SB   = bytes([250])   # Subnegotiation Begin
SE   = bytes([240])   # Subnegotiation End
DONT = bytes([254])
DO   = bytes([253])
WONT = bytes([252])
WILL = bytes([251])

OPT_ECHO        = bytes([1])
OPT_SUPPRESS_GA = bytes([3])
OPT_NAWS        = bytes([31])
OPT_LINEMODE    = bytes([34])

TELNET_INIT = (
    IAC + WILL + OPT_ECHO +
    IAC + WILL + OPT_SUPPRESS_GA +
    IAC + DONT + OPT_LINEMODE +
    IAC + DO   + OPT_NAWS
)

# Render thread tick interval (seconds).
RENDER_TICK = 0.5

# ---------------------------------------------------------------------------
# Shared state (module-level singleton)
# ---------------------------------------------------------------------------

_catbox: CatBox = CatBox()
_catbox_lock = threading.Lock()


def set_catbox(box: CatBox) -> None:
    """Replace the shared CatBox instance (call before starting server)."""
    global _catbox
    with _catbox_lock:
        _catbox = box


def get_catbox() -> CatBox:
    with _catbox_lock:
        return _catbox


# ---------------------------------------------------------------------------
# Client handler
# ---------------------------------------------------------------------------

class CatboxHandler(socketserver.BaseRequestHandler):
    """One handler per connected telnet client."""

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def setup(self) -> None:
        self._box = get_catbox()
        self._conn: socket.socket = self.request
        self._buf = b""

        # Terminal dimensions (updated by NAWS)
        self._cols = 80
        self._rows = 24

        # Render thread state
        self._render_lock = threading.Lock()
        self._render_alive = True
        self._render_paused = False    # True → render thread skips all ticks
        self._frame_idx = 0
        self._last_render_state: State | None = None
        self._flavor = ""
        self._echo_buf = b""

        # Send telnet negotiation
        self._send_raw(TELNET_INIT)

        # Brief wait for NAWS response
        self._negotiate_naws()

    def handle(self) -> None:
        self._show_welcome()
        self._start_render_thread()
        try:
            self._prompt_loop()
        finally:
            self._render_alive = False

    def finish(self) -> None:
        self._render_alive = False
        try:
            self._conn.settimeout(None)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # NAWS negotiation
    # ------------------------------------------------------------------

    def _negotiate_naws(self) -> None:
        """Wait briefly for NAWS subnegotiation to learn terminal size."""
        self._conn.settimeout(0.5)
        try:
            data = self._conn.recv(512)
            if data:
                naws = self._parse_naws(data)
                if naws:
                    self._cols, self._rows = naws
                self._buf = self._strip_telnet(data)
        except socket.timeout:
            pass
        except OSError:
            pass
        finally:
            self._conn.settimeout(None)

    def _parse_naws(self, data: bytes) -> tuple[int, int] | None:
        """Extract window size from IAC SB NAWS payload."""
        marker = IAC + SB + OPT_NAWS
        idx = data.find(marker)
        if idx == -1:
            return None
        start = idx + len(marker)
        if start + 4 > len(data):
            return None
        w = data[start] * 256 + data[start + 1]
        h = data[start + 2] * 256 + data[start + 3]
        if w > 0 and h > 0:
            return (w, h)
        return None

    # ------------------------------------------------------------------
    # Low-level I/O
    # ------------------------------------------------------------------

    def _send_raw(self, data: bytes) -> None:
        """Send raw bytes, ignoring broken-pipe errors."""
        try:
            self._conn.sendall(data)
        except OSError:
            pass

    def _send(self, text: str) -> None:
        """Encode and send a string."""
        self._send_raw(text.encode("utf-8", errors="replace"))

    # ------------------------------------------------------------------
    # Render thread
    # ------------------------------------------------------------------

    def _start_render_thread(self) -> None:
        t = threading.Thread(
            target=self._render_loop,
            name="tui-render",
            daemon=True,
        )
        t.start()

    def _render_loop(self) -> None:
        """Background loop: advances idle animation and updates the screen."""
        while self._render_alive:
            time.sleep(RENDER_TICK)
            if not self._render_alive:
                return

            # Skip if paused (help overlay, transition, etc.)
            if self._render_paused:
                continue

            # Non-blocking acquire — skip tick if main thread is drawing
            if not self._render_lock.acquire(timeout=0):
                continue
            try:
                self._render_tick()
            finally:
                self._render_lock.release()

    def _render_tick(self) -> None:
        """One tick of the render loop (called under _render_lock)."""
        box = self._box
        state = box.get_state()

        # Detect mid-superposition death
        if (self._last_render_state == State.SUPERPOSITION
                and state == State.DEAD):
            self._do_death_reveal()
            return

        # If state changed externally, skip — main thread will redraw
        if state != self._last_render_state:
            return

        # Advance idle animation
        frames, schedule = tui.get_idle_data(state)
        if not frames or not schedule:
            return

        frame_i = schedule[self._frame_idx % len(schedule)]
        frame = frames[frame_i]
        self._frame_idx += 1

        # Build and send the partial update (art + stats)
        update = tui.build_art_update(box, frame, self._cols)
        self._send_raw(update.encode("utf-8", errors="replace"))

    def _do_death_reveal(self) -> None:
        """Cat died during superposition — play death animation inline."""
        self._render_paused = True
        for frame in art.INLINE_DEATH:
            anim = tui.build_inline_anim_frame(
                frame, self._cols, color=tui.RED,
                state_text="!! QUANTUM EVENT DETECTED !!",
                state_color=tui.RED)
            self._send_raw(anim.encode("utf-8", errors="replace"))
            time.sleep(1.0)

        # Full redraw in DEAD state
        self._do_full_redraw()
        self._render_paused = False

    # ------------------------------------------------------------------
    # Full-screen draws (called under render_lock from main thread)
    # ------------------------------------------------------------------

    def _do_full_redraw(self) -> None:
        """Clear and redraw the entire TUI.  Must hold _render_lock."""
        state = self._box.get_state()
        self._last_render_state = state
        self._frame_idx = 0
        self._flavor = tui.get_flavor(state)

        frames, schedule = tui.get_idle_data(state)
        frame = frames[schedule[0]] if frames and schedule else [""] * 7

        screen = tui.build_full_screen(
            self._box, self._cols, self._rows, frame, self._flavor
        )
        self._send_raw(screen.encode("utf-8", errors="replace"))

    # ------------------------------------------------------------------
    # Welcome screen — auto-plays intro, no Enter required
    # ------------------------------------------------------------------

    def _show_welcome(self) -> None:
        # Show the banner
        welcome = tui.build_welcome(self._cols)
        self._send_raw(welcome.encode("utf-8", errors="replace"))

        # Brief pause for dramatic effect, then auto-continue
        time.sleep(2.5)

        # Initial full draw
        with self._render_lock:
            self._do_full_redraw()

    # ------------------------------------------------------------------
    # Telnet input
    # ------------------------------------------------------------------

    def _recv_line(self) -> str | None:
        """
        Read bytes until a complete line.  Strips IAC sequences and
        echoes printable characters.  Returns None on disconnect.
        """
        self._echo_buf = b""
        while True:
            for terminator in (b"\r\n", b"\r\0", b"\n", b"\r"):
                idx = self._buf.find(terminator)
                if idx != -1:
                    line = self._buf[:idx]
                    self._buf = self._buf[idx + len(terminator):]
                    self._send_raw(b"\r\n")
                    cleaned = self._strip_telnet(line).replace(b"\x00", b"")
                    self._echo_buf = b""
                    return cleaned.decode("utf-8", errors="replace").strip()

            try:
                chunk = self._conn.recv(256)
            except socket.timeout:
                continue
            except OSError:
                return None
            if not chunk:
                return None

            # Check for NAWS updates mid-session
            naws = self._parse_naws(chunk)
            if naws:
                self._cols, self._rows = naws
                with self._render_lock:
                    self._do_full_redraw()

            # Echo printable characters
            clean = self._strip_telnet(chunk)
            for byte in clean:
                if byte == 0x7f or byte == 0x08:
                    if self._echo_buf:
                        self._echo_buf = self._echo_buf[:-1]
                        if self._buf:
                            self._buf = self._buf[:-1]
                        self._send_raw(b"\x08 \x08")
                    continue
                elif byte in (0x0d, 0x0a):
                    pass
                elif 0x20 <= byte < 0x7f:
                    self._send_raw(bytes([byte]))
                    self._echo_buf += bytes([byte])

            self._buf += chunk

    def _strip_telnet(self, data: bytes) -> bytes:
        """Remove IAC option negotiation sequences from a byte string."""
        out = bytearray()
        i = 0
        while i < len(data):
            if data[i:i+1] == b"\xff":
                if i + 1 < len(data) and data[i+1:i+2] == b"\xfa":
                    end = data.find(b"\xff\xf0", i + 2)
                    if end != -1:
                        i = end + 2
                    else:
                        i = len(data)
                elif i + 2 < len(data):
                    i += 3
                else:
                    i += 1
            else:
                out.append(data[i])
                i += 1
        return bytes(out)

    # ------------------------------------------------------------------
    # Command loop
    # ------------------------------------------------------------------

    def _prompt_loop(self) -> None:
        """Main REPL loop for a single client connection."""
        while True:
            # Draw input line
            input_line = tui.build_input_line()
            self._send_raw(input_line.encode("utf-8"))

            self._conn.settimeout(None)
            line = self._recv_line()
            if line is None:
                return

            cmd = line.strip().lower()
            if not cmd:
                continue

            if cmd in ("quit", "exit", "q", "bye"):
                self._do_quit()
                return

            elif cmd in ("help", "h", "?"):
                self._do_help()

            elif cmd in ("close the box", "close"):
                self._do_close()

            elif cmd in ("open the box", "open"):
                self._do_open()

            elif cmd in ("pet the cat", "pet"):
                self._do_pet()

            elif cmd in ("status", "state", "s"):
                with self._render_lock:
                    self._do_full_redraw()

            elif cmd in ("reboot", "restart"):
                self._do_reboot()

            else:
                self._show_inline_message(
                    "The cat does not recognize that command.",
                    "Type HELP to see available commands.",
                    color=tui.YELLOW)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _do_quit(self) -> None:
        self._render_paused = True
        with self._render_lock:
            frame = tui.build_transition_frame(
                "Farewell. The cat remains. (For now.)",
                self._cols, color=tui.DIM)
            self._send_raw(frame.encode("utf-8"))
        time.sleep(1.5)

    def _do_help(self) -> None:
        # Pause render thread so it doesn't overwrite the help overlay
        self._render_paused = True
        with self._render_lock:
            overlay = tui.build_help_overlay(self._cols)
            self._send_raw(overlay.encode("utf-8"))

        # Wait for ENTER to dismiss
        self._conn.settimeout(None)
        self._recv_line()

        with self._render_lock:
            self._do_full_redraw()
        self._render_paused = False

    def _do_close(self) -> None:
        box = self._box
        result = box.close_box()
        if result:
            self._render_paused = True
            with self._render_lock:
                self._play_inline_anim(
                    art.INLINE_CLOSE, delay=0.7, color=tui.MAGENTA,
                    state_text="[ CLOSING THE BOX... ]",
                    state_color=tui.YELLOW)
                self._do_full_redraw()
            self._render_paused = False
        else:
            state = box.get_state()
            if state == State.DEAD:
                self._show_inline_message(
                    "The cat is dead. It can't be put in a box.",
                    "Type REBOOT to restart.",
                    color=tui.RED)
            else:
                self._show_inline_message(
                    "The box is already closed!",
                    "The experiment is underway.",
                    color=tui.YELLOW)

    def _do_open(self) -> None:
        box = self._box
        state_before = box.get_state()

        if state_before == State.ALIVE:
            self._show_inline_message(
                "The box is already open.",
                "The cat can see you. It blinks slowly.",
                color=tui.YELLOW)
            return

        if state_before == State.DEAD:
            self._show_inline_message(
                "The box is open. The cat is dead.",
                "Type REBOOT to try again.",
                color=tui.RED)
            return

        # SUPERPOSITION → collapse
        resolved = box.open_box()
        self._render_paused = True
        with self._render_lock:
            if resolved == State.ALIVE:
                self._play_inline_anim(
                    art.INLINE_OPEN_ALIVE, delay=0.8, color=tui.GREEN,
                    state_text="[ OPENING THE BOX... ]",
                    state_color=tui.YELLOW)
            else:
                self._play_inline_anim(
                    art.INLINE_OPEN_DEAD, delay=1.0, color=tui.RED,
                    state_text="[ OPENING THE BOX... ]",
                    state_color=tui.YELLOW)
            self._do_full_redraw()
        self._render_paused = False

    def _do_pet(self) -> None:
        state = self._box.get_state()
        if state == State.ALIVE:
            frames = art.INLINE_PET_ALIVE
            color = tui.GREEN
            status = "Purring detected."
        elif state == State.SUPERPOSITION:
            frames = art.INLINE_PET_SUPER
            color = tui.MAGENTA
            status = "The box remains sealed."
        else:
            frames = art.INLINE_PET_DEAD
            color = tui.RED
            status = "..."

        self._render_paused = True
        with self._render_lock:
            self._play_inline_anim(
                frames, delay=1.2, color=color,
                status_text=status)
            # Brief hold on the last frame
            time.sleep(0.8)
            self._do_full_redraw()
        self._render_paused = False

    def _do_reboot(self) -> None:
        self._render_paused = True
        with self._render_lock:
            self._play_inline_anim(
                art.INLINE_REBOOT, delay=1.2, color=tui.YELLOW,
                state_text="[ REBOOTING... ]",
                state_color=tui.YELLOW,
                status_text="Collapsing all wave functions...")

        msg = tui.build_transition_frame(
            "Connection will be lost. Goodbye.",
            self._cols, color=tui.DIM)
        self._send_raw(msg.encode("utf-8"))
        time.sleep(1.0)

        try:
            subprocess.Popen(["sudo", "reboot"])
        except OSError as e:
            self._render_paused = False
            self._show_inline_message(
                f"Reboot failed: {e}",
                "(Are you running on the Pi with sudo access?)",
                color=tui.RED)

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _play_inline_anim(self, frames: list, delay: float = 0.6,
                          color: str = tui.MAGENTA,
                          state_text: str = "",
                          state_color: str = "",
                          status_text: str = "") -> None:
        """
        Play animation frames inside the TUI art region.
        Must hold _render_lock.  Keeps header/footer/rules intact.
        """
        for frame in frames:
            anim = tui.build_inline_anim_frame(
                frame, self._cols, color=color,
                state_text=state_text,
                state_color=state_color,
                status_text=status_text)
            self._send_raw(anim.encode("utf-8", errors="replace"))
            time.sleep(delay)

    def _show_inline_message(self, line1: str, line2: str = "",
                             color: str = "", duration: float = 2.0) -> None:
        """
        Show a brief message inside the art region, then redraw.
        Keeps the TUI chrome intact.
        """
        # Build a simple 7-line frame with the message centered
        lines = [""] * 7
        lines[2] = "  " + line1
        if line2:
            lines[3] = "  " + line2
        padded = [l.ljust(72) for l in lines]

        self._render_paused = True
        with self._render_lock:
            anim = tui.build_inline_anim_frame(
                padded, self._cols, color=color)
            self._send_raw(anim.encode("utf-8", errors="replace"))

        time.sleep(duration)

        with self._render_lock:
            self._do_full_redraw()
        self._render_paused = False


# ---------------------------------------------------------------------------
# Threaded server
# ---------------------------------------------------------------------------

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """TCP server that spawns a new thread per connection."""

    allow_reuse_address = True
    daemon_threads = True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_server(host: str = "0.0.0.0", port: int = 1701) -> ThreadedTCPServer:
    """Create (but do not start) the telnet server."""
    server = ThreadedTCPServer((host, port), CatboxHandler)
    return server


def main(port: int = 1701, half_life: float = 30.0) -> None:
    """Start the Catbox telnet server and block until interrupted."""
    import signal

    box = CatBox(half_life=half_life)
    set_catbox(box)

    server = create_server(port=port)

    def _shutdown(sig, frame):
        print("\nShutting down catbox server...", flush=True)
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, _shutdown)
    try:
        signal.signal(signal.SIGTERM, _shutdown)
    except (OSError, AttributeError):
        pass

    print(f"[catbox] Listening on port {port}  (half-life={half_life}s)", flush=True)
    print(f"[catbox] telnet localhost {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Schrödinger's Catbox telnet server")
    parser.add_argument("--port", type=int, default=1701,
                        help="TCP port (default 1701)")
    parser.add_argument("--half-life", type=float, default=30.0,
                        help="Decay half-life in seconds (default 30)")
    args = parser.parse_args()

    main(port=args.port, half_life=args.half_life)
