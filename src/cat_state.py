"""
cat_state.py — Core CatBox state machine and quantum decay RNG

Implements the Schrodinger's Catbox state machine:
  ALIVE       → Box is open. Cat is visible, no decay running.
  SUPERPOSITION → Box is closed. Quantum decay ticking in background.
  DEAD        → Cat has decayed. Only a reboot revives it.

Thread-safe: multiple telnet clients share a single CatBox instance.
"""

import threading
import time
import math
import random
from enum import Enum, auto

# Art module (created by ascii-artist teammate).
# Imported at runtime; not required for the state machine to function.
try:
    import art
except ImportError:
    art = None


class State(Enum):
    ALIVE = auto()
    SUPERPOSITION = auto()
    DEAD = auto()


# Half-life of the quantum decay in seconds.
# After this many seconds with the box closed, there is a ~50% chance
# the cat has decayed.  Adjust to taste for the installation.
DEFAULT_HALF_LIFE = 30.0

# How often (seconds) the background decay thread checks for decay.
DECAY_TICK_INTERVAL = 0.5


class CatBox:
    """
    The Schrodinger's Catbox.

    Usage
    -----
        box = CatBox(half_life=30.0)
        box.close_box()   # start quantum decay
        time.sleep(10)
        box.open_box()    # collapse superposition
        print(box.get_state())
        print(box.is_alive())
    """

    def __init__(self, half_life: float = DEFAULT_HALF_LIFE) -> None:
        self._half_life = half_life          # seconds
        self._state = State.ALIVE
        self._lock = threading.Lock()
        self._box_closed_at: float | None = None  # monotonic timestamp

        # Background decay thread — runs only while box is closed.
        self._decay_thread: threading.Thread | None = None
        self._stop_decay = threading.Event()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def close_box(self) -> bool:
        """
        Close the box, beginning quantum superposition.

        Returns True if the box was successfully closed (was ALIVE).
        Returns False if already closed or the cat is DEAD.
        """
        with self._lock:
            if self._state != State.ALIVE:
                return False
            self._state = State.SUPERPOSITION
            self._box_closed_at = time.monotonic()
            self._stop_decay.clear()

        self._start_decay_thread()
        return True

    def open_box(self) -> State:
        """
        Open the box, collapsing the quantum superposition.

        The outcome has already been determined by the background decay
        thread.  If the cat decayed while the box was shut, it is DEAD.
        Otherwise it is ALIVE again.

        Returns the resolved State (ALIVE or DEAD).
        """
        self._stop_decay.set()          # signal background thread to stop

        with self._lock:
            if self._state == State.DEAD:
                return State.DEAD
            if self._state == State.ALIVE:
                # Box was never properly closed (edge case).
                return State.ALIVE
            # Superposition → collapse to ALIVE (decay thread would have
            # already set DEAD if decay occurred).
            self._state = State.ALIVE
            self._box_closed_at = None
            return State.ALIVE

    def get_state(self) -> State:
        """Return the current state (thread-safe snapshot)."""
        with self._lock:
            return self._state

    def is_alive(self) -> bool:
        """Convenience: True if the cat is not DEAD."""
        return self.get_state() != State.DEAD

    def time_in_box(self) -> float | None:
        """
        Seconds since the box was closed, or None if box is open.
        Useful for displaying elapsed superposition time to visitors.
        """
        with self._lock:
            if self._box_closed_at is None:
                return None
            return time.monotonic() - self._box_closed_at

    def decay_probability(self) -> float:
        """
        Cumulative probability [0, 1] that decay has occurred given the
        elapsed closed time, according to the exponential decay model:

            P(t) = 1 - exp(-lambda * t)  where lambda = ln(2) / half_life

        Returns 0.0 when the box is open.
        """
        elapsed = self.time_in_box()
        if elapsed is None:
            return 0.0
        lam = math.log(2) / self._half_life
        return 1.0 - math.exp(-lam * elapsed)

    # ------------------------------------------------------------------
    # Internal quantum decay machinery
    # ------------------------------------------------------------------

    def _start_decay_thread(self) -> None:
        """Spin up the background quantum decay thread."""
        t = threading.Thread(
            target=self._decay_loop,
            name="quantum-decay",
            daemon=True,
        )
        t.start()
        self._decay_thread = t

    def _decay_loop(self) -> None:
        """
        Background thread: periodically rolls the quantum dice.

        The probability of decay in each tick is derived from the
        instantaneous decay rate so that the cumulative probability
        follows the correct exponential model over continuous time.

        Per-tick probability:
            p_tick = 1 - exp(-lambda * dt)

        where dt = DECAY_TICK_INTERVAL.  This ensures that regardless of
        tick granularity, the long-run decay statistics match the
        specified half-life exactly.
        """
        lam = math.log(2) / self._half_life
        p_tick = 1.0 - math.exp(-lam * DECAY_TICK_INTERVAL)

        while not self._stop_decay.wait(timeout=DECAY_TICK_INTERVAL):
            # Check if still in superposition under the lock.
            with self._lock:
                if self._state != State.SUPERPOSITION:
                    return

            # The quantum dice roll.
            if random.random() < p_tick:
                with self._lock:
                    if self._state == State.SUPERPOSITION:
                        self._state = State.DEAD
                        self._box_closed_at = None
                return  # Cat is dead; decay thread's work is done.
