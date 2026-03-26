"""
server.py — Telnet server for Schrödinger's Catbox

Accepts multiple simultaneous telnet connections. All connections share ONE
CatBox instance — one cat, many observers. The server listens on a
configurable port (default 1701).

Python 3 stdlib only. No external dependencies.
"""

import socketserver
import threading
import random
import sys
import os

# ---------------------------------------------------------------------------
# Path setup — allow running from repo root or src/ directly
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import art
from cat_state import CatBox, State

# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------

CLEAR_SCREEN = "\033[2J\033[H"   # clear + move cursor to top-left
RESET        = "\033[0m"
BOLD         = "\033[1m"
DIM          = "\033[2m"
GREEN        = "\033[32m"
RED          = "\033[31m"
YELLOW       = "\033[33m"
CYAN         = "\033[36m"
MAGENTA      = "\033[35m"

# ---------------------------------------------------------------------------
# Telnet protocol constants
# ---------------------------------------------------------------------------

IAC  = bytes([255])   # Interpret As Command
DONT = bytes([254])
DO   = bytes([253])
WONT = bytes([252])
WILL = bytes([251])

# Telnet option codes
OPT_ECHO          = bytes([1])
OPT_SUPPRESS_GA   = bytes([3])
OPT_LINEMODE      = bytes([34])

# We send these to configure the terminal into a usable state:
#   WILL ECHO          — server handles echo
#   WILL SUPPRESS-GA   — suppress go-ahead (full-duplex mode)
#   DONT LINEMODE      — we handle line assembly ourselves
TELNET_INIT = (
    IAC + WILL + OPT_ECHO +
    IAC + WILL + OPT_SUPPRESS_GA +
    IAC + DONT + OPT_LINEMODE
)

# ---------------------------------------------------------------------------
# Shared state (module-level singleton)
# ---------------------------------------------------------------------------

# Created once; replaced by the server on startup if a custom half_life
# is configured.  Use set_catbox() before starting the server.
_catbox: CatBox = CatBox()

# Lock protecting _catbox replacement (rare, but thread-safe is correct).
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
        self._conn = self.request          # raw socket
        self._buf = b""                    # receive buffer
        self._send_raw(TELNET_INIT)

    def handle(self) -> None:
        self._show_welcome()
        self._prompt_loop()

    def finish(self) -> None:
        # Socket is closed by the framework after handle() returns.
        pass

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _send_raw(self, data: bytes) -> None:
        """Send raw bytes, ignoring broken-pipe errors."""
        try:
            self._conn.sendall(data)
        except OSError:
            pass

    def _send(self, text: str) -> None:
        """Send text with telnet-style \r\n line endings."""
        encoded = text.replace("\n", "\r\n").encode("utf-8", errors="replace")
        self._send_raw(encoded)

    def _clear(self) -> None:
        self._send(CLEAR_SCREEN)

    def _show_welcome(self) -> None:
        self._clear()
        self._send(CYAN + art.WELCOME_BANNER + RESET)
        self._send(art.FOOTER)
        self._send("\r\n")
        self._show_current_state()

    def _show_current_state(self, transition_msg: str = "") -> None:
        """Render the current cat state with optional transition narrative."""
        box = self._box
        state = box.get_state()

        self._send("\r\n")

        if transition_msg:
            self._send(DIM + transition_msg + RESET)
            self._send("\r\n")

        if state == State.ALIVE:
            self._send(GREEN + art.MSG_ALIVE_HEADER + RESET)
            self._send(GREEN + art.CAT_ALIVE_FULL + RESET)
            self._send(art.MSG_ALIVE_DESCRIPTION)
            self._send(DIM + random.choice(art.FLAVOR_TEXTS_ALIVE) + RESET)
            self._send("\r\n")
            self._send(YELLOW + art.PROMPT_OPEN_BOX + RESET)

        elif state == State.SUPERPOSITION:
            elapsed = box.time_in_box() or 0.0
            prob = box.decay_probability()
            self._send(MAGENTA + art.MSG_SUPERPOSITION_HEADER + RESET)
            self._send(MAGENTA + art.CAT_SUPERPOSITION + RESET)
            self._send(art.MSG_SUPERPOSITION_DESCRIPTION)
            self._send(DIM + random.choice(art.FLAVOR_TEXTS_CLOSED) + RESET)
            self._send(
                f"\r\n  [Box sealed for {elapsed:.1f}s"
                f" | decay probability: {prob*100:.1f}%]"
            )
            self._send("\r\n")
            self._send(YELLOW + art.PROMPT_CLOSED_BOX + RESET)

        else:  # DEAD
            self._send(RED + art.MSG_DEAD_HEADER + RESET)
            self._send(RED + art.CAT_DEAD_FULL + RESET)
            self._send(art.MSG_DEAD_DESCRIPTION)
            self._send(DIM + random.choice(art.FLAVOR_TEXTS_DEAD) + RESET)
            self._send("\r\n")
            self._send(RED + art.PROMPT_DEAD_BOX + RESET)

    def _show_prompt(self) -> None:
        self._send(BOLD + "\r\n> " + RESET)

    # ------------------------------------------------------------------
    # Telnet input
    # ------------------------------------------------------------------

    def _recv_line(self) -> str | None:
        """
        Read bytes from the socket until we get a complete line (\\r\\n or
        \\n).  Strips IAC sequences.  Returns None on disconnect.
        """
        while True:
            # Check buffer for a complete line.
            for terminator in (b"\r\n", b"\n", b"\r"):
                idx = self._buf.find(terminator)
                if idx != -1:
                    line = self._buf[:idx]
                    self._buf = self._buf[idx + len(terminator):]
                    return self._strip_telnet(line).decode("utf-8", errors="replace").strip()

            try:
                chunk = self._conn.recv(256)
            except OSError:
                return None
            if not chunk:
                return None
            self._buf += chunk

    def _strip_telnet(self, data: bytes) -> bytes:
        """Remove IAC option negotiation sequences from a byte string."""
        out = bytearray()
        i = 0
        while i < len(data):
            if data[i:i+1] == b"\xff":   # IAC
                if i + 2 < len(data):
                    i += 3               # IAC + cmd + option
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
            self._show_prompt()
            line = self._recv_line()
            if line is None:
                # Client disconnected.
                return

            cmd = line.strip().lower()

            if not cmd:
                continue

            if cmd in ("quit", "exit", "q", "bye"):
                self._send("\r\nFarewell. The cat remains. (For now.)\r\n\r\n")
                return

            elif cmd in ("help", "h", "?"):
                self._clear()
                self._send(CYAN + art.CMD_HELP + RESET)
                self._show_current_state()

            elif cmd in ("close the box", "close"):
                self._do_close()

            elif cmd in ("open the box", "open"):
                self._do_open()

            elif cmd in ("pet the cat", "pet"):
                self._do_pet()

            elif cmd in ("status", "state", "s"):
                self._clear()
                self._show_current_state()

            else:
                self._send(
                    "\r\n" + YELLOW + art.MSG_UNKNOWN_CMD + RESET
                )

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _do_close(self) -> None:
        box = self._box
        result = box.close_box()
        self._clear()
        if result:
            self._show_current_state(transition_msg=art.MSG_BOX_CLOSING)
        else:
            state = box.get_state()
            if state == State.DEAD:
                self._send("\r\n" + RED + art.MSG_UNKNOWN_CMD + RESET)
                self._show_current_state()
            else:
                self._send("\r\n" + YELLOW + art.MSG_ALREADY_CLOSED + RESET)
                self._show_current_state()

    def _do_open(self) -> None:
        box = self._box
        state_before = box.get_state()

        if state_before == State.ALIVE:
            self._send("\r\n" + YELLOW + art.MSG_ALREADY_OPEN + RESET)
            self._show_current_state()
            return

        if state_before == State.DEAD:
            self._clear()
            self._show_current_state()
            return

        # SUPERPOSITION → collapse
        resolved = box.open_box()
        self._clear()
        if resolved == State.ALIVE:
            self._show_current_state(transition_msg=art.MSG_BOX_OPENING_ALIVE)
        else:
            self._show_current_state(transition_msg=art.MSG_BOX_OPENING_DEAD)

    def _do_pet(self) -> None:
        box = self._box
        state = box.get_state()
        self._clear()
        if state == State.ALIVE:
            self._send(
                "\r\n" + GREEN
                + "You reach in and pet the cat.\r\n"
                + "It tolerates this. Barely.\r\n"
                + "Purring detected. Quantum state: JUDGED.\r\n"
                + RESET
            )
            self._show_current_state()
        elif state == State.SUPERPOSITION:
            self._send(
                "\r\n" + MAGENTA
                + "You cannot pet what you cannot observe.\r\n"
                + "The box is sealed. Do not open it on behalf of your hand.\r\n"
                + RESET
            )
            self._show_current_state()
        else:  # DEAD
            self._send(
                "\r\n" + RED
                + "...you reach into the box.\r\n"
                + "The cat does not respond.\r\n"
                + "The cat will never respond again.\r\n"
                + "Please do not pet dead cats.\r\n"
                + RESET
            )
            self._show_current_state()


# ---------------------------------------------------------------------------
# Threaded server
# ---------------------------------------------------------------------------

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """TCP server that spawns a new thread per connection."""

    allow_reuse_address = True
    daemon_threads = True          # don't block shutdown on lingering clients


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_server(host: str = "0.0.0.0", port: int = 1701) -> ThreadedTCPServer:
    """
    Create (but do not start) the telnet server.

    Example
    -------
        server = create_server(port=1701)
        server.serve_forever()
    """
    server = ThreadedTCPServer((host, port), CatboxHandler)
    return server


def main(port: int = 1701, half_life: float = 30.0) -> None:
    """
    Start the Catbox telnet server and block until interrupted.

    Parameters
    ----------
    port:       TCP port to listen on (default 1701).
    half_life:  Quantum decay half-life in seconds (default 30).
    """
    import signal

    box = CatBox(half_life=half_life)
    set_catbox(box)

    server = create_server(port=port)

    # Graceful Ctrl-C shutdown
    def _shutdown(sig, frame):
        print("\nShutting down catbox server...", flush=True)
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, _shutdown)
    try:
        signal.signal(signal.SIGTERM, _shutdown)
    except (OSError, AttributeError):
        pass  # SIGTERM not available on all platforms (e.g. Windows)

    print(f"[catbox] Listening on port {port}  (half-life={half_life}s)", flush=True)
    print(f"[catbox] telnet localhost {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Schrödinger's Catbox telnet server")
    parser.add_argument("--port",      type=int,   default=1701,  help="TCP port (default 1701)")
    parser.add_argument("--half-life", type=float, default=30.0,  help="Decay half-life in seconds (default 30)")
    args = parser.parse_args()

    main(port=args.port, half_life=args.half_life)
