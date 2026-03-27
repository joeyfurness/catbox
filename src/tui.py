"""
tui.py — Fixed-position TUI renderer for Schrödinger's Catbox

Builds ANSI escape sequences that position content at fixed screen
locations, giving telnet clients a proper TUI feel instead of scrolling
text.  All render methods return bytes buffers — the caller sends them
atomically via sendall() to prevent interleaving with other threads.

Designed for 80x24 minimum.  Scales header/footer rules to terminal width.
"""

import random
from cat_state import CatBox, State
import art

# ---------------------------------------------------------------------------
# ANSI escape helpers
# ---------------------------------------------------------------------------

RESET     = "\033[0m"
BOLD      = "\033[1m"
DIM       = "\033[2m"
GREEN     = "\033[32m"
RED       = "\033[31m"
YELLOW    = "\033[33m"
CYAN      = "\033[36m"
MAGENTA   = "\033[35m"
WHITE     = "\033[37m"
BG_BLACK  = "\033[40m"
INVERT    = "\033[7m"

CLEAR_SCREEN = "\033[2J\033[H"
ERASE_LINE   = "\033[2K"
HIDE_CURSOR  = "\033[?25l"
SHOW_CURSOR  = "\033[?25h"
SAVE_CURSOR  = "\0337"
REST_CURSOR  = "\0338"


def _move(row: int, col: int = 1) -> str:
    return f"\033[{row};{col}H"


def _erase_and_write(row: int, text: str, col: int = 1) -> str:
    """Move to row, erase line, write text."""
    return f"{_move(row, col)}{ERASE_LINE}{text}"


def _center(text: str, width: int) -> str:
    """Center text within width."""
    padding = max(0, (width - len(text)) // 2)
    return " " * padding + text


def _rule(char: str, width: int) -> str:
    return char * width


# ---------------------------------------------------------------------------
# Screen layout (row numbers for 80x24)
# ---------------------------------------------------------------------------
# Rows are 1-indexed (ANSI standard).
#
#  1  Header title
#  2  ════════════ (double rule)
#  3  State header (colored)
#  4  ──────────── (thin rule)
#  5  \
#  6   |
#  7   |
#  8   |  Art region (7 lines)
#  9   |
# 10   |
# 11  /
# 12  ──────────── (thin rule)
# 13  \
# 14   |  Description (3 lines)
# 15  /
# 16  Flavor text
# 17  Status/stats line
# 18  ──────────── (thin rule)
# 19  \
# 20   |  Action prompt (2 lines)
# 21  /
# 22  ──────────── (thin rule)
# 23  Footer
# 24  > (input line)

ROW_HEADER    = 1
ROW_RULE_TOP  = 2
ROW_STATE     = 3
ROW_RULE_ST   = 4
ROW_ART       = 5   # through 11
ROW_RULE_ART  = 12
ROW_DESC      = 13  # through 15
ROW_FLAVOR    = 16
ROW_STATS     = 17
ROW_RULE_ACT  = 18
ROW_ACTION    = 19  # through 21 (19, 20, and a spare 21)
ROW_RULE_BOT  = 22
ROW_FOOTER    = 23
ROW_INPUT     = 24

ART_HEIGHT = 7   # rows 5-11


# ---------------------------------------------------------------------------
# Public render functions — all return str (caller encodes + sends)
# ---------------------------------------------------------------------------

def build_full_screen(box: CatBox, cols: int, rows: int,
                      art_frame: list[str], flavor: str) -> str:
    """
    Build a complete screen redraw.

    Parameters
    ----------
    box:        The shared CatBox instance.
    cols:       Terminal width.
    rows:       Terminal height.
    art_frame:  List of 7 strings (current idle animation frame).
    flavor:     Random flavor text string.

    Returns a complete ANSI string that clears and redraws the screen.
    """
    state = box.get_state()
    buf = []
    buf.append(CLEAR_SCREEN)
    buf.append(HIDE_CURSOR)

    # Row 1: Header
    title = _center("SCHRODINGER'S CATBOX", cols)
    buf.append(_erase_and_write(ROW_HEADER, BOLD + CYAN + title + RESET))

    # Row 2: Top rule
    buf.append(_erase_and_write(ROW_RULE_TOP, DIM + _rule("═", cols) + RESET))

    # Row 3: State header
    state_text, state_color = _state_header(state)
    buf.append(_erase_and_write(ROW_STATE,
               state_color + BOLD + _center(state_text, cols) + RESET))

    # Row 4: Thin rule
    buf.append(_erase_and_write(ROW_RULE_ST, DIM + _rule("─", cols) + RESET))

    # Rows 5-11: Art
    art_color = _art_color(state)
    for i in range(ART_HEIGHT):
        line = art_frame[i] if i < len(art_frame) else ""
        buf.append(_erase_and_write(ROW_ART + i, art_color + line + RESET))

    # Row 12: Rule
    buf.append(_erase_and_write(ROW_RULE_ART, DIM + _rule("─", cols) + RESET))

    # Rows 13-15: Description
    desc = _get_desc(state)
    for i in range(3):
        line = desc[i] if i < len(desc) else ""
        buf.append(_erase_and_write(ROW_DESC + i, line))

    # Row 16: Flavor text
    buf.append(_erase_and_write(ROW_FLAVOR,
               DIM + "  " + flavor + RESET))

    # Row 17: Stats/status
    buf.append(_build_stats_line(box, state, cols))

    # Row 18: Rule
    buf.append(_erase_and_write(ROW_RULE_ACT, DIM + _rule("─", cols) + RESET))

    # Rows 19-21: Action text
    action = _get_action(state)
    for i in range(3):
        line = action[i] if i < len(action) else ""
        color = YELLOW if line else ""
        reset = RESET if line else ""
        buf.append(_erase_and_write(ROW_ACTION + i, color + line + reset))

    # Row 22: Bottom rule
    buf.append(_erase_and_write(ROW_RULE_BOT, DIM + _rule("─", cols) + RESET))

    # Row 23: Footer
    footer = _center(art.FOOTER, cols)
    buf.append(_erase_and_write(ROW_FOOTER, DIM + footer + RESET))

    # Row 24: Input line
    buf.append(_erase_and_write(ROW_INPUT, BOLD + "> " + RESET))

    buf.append(SHOW_CURSOR)

    return "".join(buf)


def build_art_update(box: CatBox, art_frame: list[str],
                     cols: int) -> str:
    """
    Build a partial update for the art region + stats line only.
    Used by the render thread for idle animation ticks.

    Returns an ANSI string wrapped in save/restore cursor so the
    user's input position is preserved.
    """
    state = box.get_state()
    buf = []
    buf.append(SAVE_CURSOR)
    buf.append(HIDE_CURSOR)

    # Art region
    art_color = _art_color(state)
    for i in range(ART_HEIGHT):
        line = art_frame[i] if i < len(art_frame) else ""
        buf.append(_erase_and_write(ROW_ART + i, art_color + line + RESET))

    # Stats line
    buf.append(_build_stats_line(box, state, cols))

    buf.append(SHOW_CURSOR)
    buf.append(REST_CURSOR)

    return "".join(buf)


def build_inline_anim_frame(art_frame: list[str], cols: int,
                            color: str = MAGENTA,
                            state_text: str = "",
                            state_color: str = "",
                            status_text: str = "") -> str:
    """
    Update just the art region (rows 5-11) within the existing TUI layout.
    Optionally updates the state header (row 3) and status row (row 17).
    Used for close/open/pet animations that should keep the TUI chrome intact.
    """
    buf = []
    buf.append(SAVE_CURSOR)
    buf.append(HIDE_CURSOR)

    # Optionally update state header
    if state_text:
        sc = state_color or color
        buf.append(_erase_and_write(ROW_STATE,
                   sc + BOLD + _center(state_text, cols) + RESET))

    # Art region
    for i in range(ART_HEIGHT):
        line = art_frame[i] if i < len(art_frame) else ""
        buf.append(_erase_and_write(ROW_ART + i, color + line + RESET))

    # Optionally update status line
    if status_text:
        buf.append(_erase_and_write(ROW_STATS,
                   (state_color or color) + "  " + status_text + RESET))

    buf.append(SHOW_CURSOR)
    buf.append(REST_CURSOR)

    return "".join(buf)


def build_stats_update(box: CatBox, cols: int) -> str:
    """Build a minimal update for just the stats line (row 17)."""
    state = box.get_state()
    buf = []
    buf.append(SAVE_CURSOR)
    buf.append(HIDE_CURSOR)
    buf.append(_build_stats_line(box, state, cols))
    buf.append(SHOW_CURSOR)
    buf.append(REST_CURSOR)
    return "".join(buf)


def build_transition_frame(text: str, cols: int, color: str = MAGENTA) -> str:
    """Build a full-screen frame for transition animations."""
    buf = []
    buf.append(CLEAR_SCREEN)
    buf.append(HIDE_CURSOR)

    lines = text.strip("\n").split("\n")
    # Center vertically
    start_row = max(1, (24 - len(lines)) // 2)
    for i, line in enumerate(lines):
        row = start_row + i
        if row > 24:
            break
        buf.append(_erase_and_write(row, color + line + RESET))

    return "".join(buf)


def build_help_overlay(cols: int) -> str:
    """Build the help text as a centered overlay."""
    buf = []
    buf.append(CLEAR_SCREEN)
    buf.append(HIDE_CURSOR)

    lines = art.CMD_HELP.strip("\n").split("\n")
    start_row = max(1, (24 - len(lines)) // 2)
    for i, line in enumerate(lines):
        row = start_row + i
        if row > 24:
            break
        buf.append(_erase_and_write(row, CYAN + line + RESET))

    buf.append(_erase_and_write(24, DIM + "  Press ENTER to return..." + RESET))
    return "".join(buf)


def build_input_line(prefix: str = "") -> str:
    """Redraw just the input line (row 24)."""
    return _erase_and_write(ROW_INPUT, BOLD + "> " + RESET + prefix)


def build_welcome(cols: int) -> str:
    """Build the welcome splash screen."""
    buf = []
    buf.append(CLEAR_SCREEN)
    buf.append(HIDE_CURSOR)

    lines = art.WELCOME_BANNER.strip("\n").split("\n")
    start_row = max(1, (24 - len(lines)) // 2 - 1)
    for i, line in enumerate(lines):
        row = start_row + i
        if row > 23:
            break
        buf.append(_erase_and_write(row, CYAN + line + RESET))

    buf.append(_erase_and_write(24,
               DIM + _center("catbox.local", cols) + RESET))
    buf.append(SHOW_CURSOR)
    return "".join(buf)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _state_header(state: State) -> tuple[str, str]:
    if state == State.ALIVE:
        return art.TUI_STATE_ALIVE, GREEN
    elif state == State.SUPERPOSITION:
        return art.TUI_STATE_SUPER, MAGENTA
    else:
        return art.TUI_STATE_DEAD, RED


def _art_color(state: State) -> str:
    if state == State.ALIVE:
        return GREEN
    elif state == State.SUPERPOSITION:
        return MAGENTA
    else:
        return RED


def _get_desc(state: State) -> list[str]:
    if state == State.ALIVE:
        return art.TUI_DESC_ALIVE
    elif state == State.SUPERPOSITION:
        return art.TUI_DESC_SUPER
    else:
        return art.TUI_DESC_DEAD


def _get_action(state: State) -> list[str]:
    if state == State.ALIVE:
        return art.TUI_ACTION_ALIVE
    elif state == State.SUPERPOSITION:
        return art.TUI_ACTION_SUPER
    else:
        return art.TUI_ACTION_DEAD


def _build_stats_line(box: CatBox, state: State, cols: int) -> str:
    """Build the stats/status line at ROW_STATS."""
    if state == State.ALIVE:
        text = "  Status: VERY MUCH ALIVE (as far as you know)"
        return _erase_and_write(ROW_STATS, GREEN + DIM + text + RESET)
    elif state == State.SUPERPOSITION:
        elapsed = box.time_in_box() or 0.0
        prob = box.decay_probability()
        text = (f"  [ Box sealed for {elapsed:.1f}s"
                f" | decay probability: {prob*100:.1f}% ]")
        return _erase_and_write(ROW_STATS, MAGENTA + BOLD + text + RESET)
    else:
        text = "  Status: DEFINITIVELY DEAD (thanks for opening the box)"
        return _erase_and_write(ROW_STATS, RED + DIM + text + RESET)


def get_flavor(state: State) -> str:
    """Pick a random flavor text for the given state."""
    if state == State.ALIVE:
        return random.choice(art.FLAVOR_TEXTS_ALIVE)
    elif state == State.SUPERPOSITION:
        return random.choice(art.FLAVOR_TEXTS_CLOSED)
    else:
        return random.choice(art.FLAVOR_TEXTS_DEAD)


def get_idle_data(state: State):
    """Return (frames, schedule) for the given state's idle animation."""
    if state == State.ALIVE:
        return art.IDLE_ALIVE_FRAMES, art.IDLE_ALIVE_SCHEDULE
    elif state == State.SUPERPOSITION:
        return art.IDLE_SUPER_FRAMES, art.IDLE_SUPER_SCHEDULE
    else:
        return art.IDLE_DEAD_FRAMES, art.IDLE_DEAD_SCHEDULE
