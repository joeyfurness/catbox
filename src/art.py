"""
art.py — ASCII art, idle animation frames, and text for Schrödinger's Catbox
All art kept within 80 columns.
"""


# ---------------------------------------------------------------------------
# Helper: convert a raw art string to a list of padded lines
# ---------------------------------------------------------------------------

def _to_frame(art_str, height=7, width=72):
    """Split a raw art string into exactly `height` lines, each `width` chars."""
    lines = art_str.strip("\n").split("\n")
    while len(lines) < height:
        lines.append("")
    lines = lines[:height]
    return [line.ljust(width) for line in lines]


# ---------------------------------------------------------------------------
# IDLE ANIMATION FRAMES — lists of 7-line frames for the render loop
# ---------------------------------------------------------------------------

# ---- ALIVE idle frames ----

IDLE_ALIVE_FRAMES = [
    _to_frame(r"""
        /\_____/\
       /  o   o  \
      ( ==  ^  == )       I'm alive! ... probably.
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\
       /  -   -  \
      ( ==  ^  == )       I'm alive! ... probably.
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\
       /      o o\
      ( ==  ^  ==)        ...what are you looking at?
       )         (
      (    w      )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\
       /  o   o  \
      ( ==  O  == )       *yaaawn*
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\
       /o o      \
      (==  ^  == )        hmm?
       )         (
      (      w    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\
       /  -   -  \
      ( ==  ^  == )       z z z
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
]

# Frame indices per tick (500ms each). Lots of normal, brief blinks/actions.
IDLE_ALIVE_SCHEDULE = [
    # normal                   blink normal
    0, 0, 0, 0, 0, 0, 0, 0,   1, 0,
    # normal              look right      normal
    0, 0, 0, 0, 0, 0,    2, 2, 2, 0,     0, 0, 0, 0,
    # blink normal        normal               yawn         normal
    1, 0,                 0, 0, 0, 0, 0, 0,    3, 3, 3, 0,  0, 0, 0, 0,
    # look left      normal              blink  sleepy       normal
    4, 4, 4, 0,      0, 0, 0, 0, 0, 0,   1,    5, 5, 5, 0,  0, 0, 0, 0,
]

# ---- SUPERPOSITION idle frames ----

IDLE_SUPER_FRAMES = [
    _to_frame(r"""
    /\_/??/\_/\
   / o?? ??x o \
  (== ^??? _? ==)         |alive> + |dead>
   ) ????????? (
  (  ???????????)
 ( ( ) ????? ( ) )
(__(__)??????(__)__)"""),

    _to_frame(r"""
    /\_o??o\_/\
   / o?o ??o o \
  (== ^?^? ?? ==)         |alive> + |dead>
   ) ???w????? (
  (  ???????????)
 ( ( ) ????? ( ) )
(__(__)??????(__)__)"""),

    _to_frame(r"""
    /\_x??x\_/\
   / x?? ??x x \
  (== _??? _? ==)         |alive> + |dead>
   ) ???R.I.P.? (
  (  ???????????)
 ( ( ) ????? ( ) )
(__(__)??????(__)__)"""),

    _to_frame(r"""
    /\#/??#\_/\
   / #?? ??# # \
  (#= #??? #? ==#)       |||SIGNAL LOST|||
   ) ##??##### (
  (  ###########)
 ( ( # ##### # ) )
(__(#_#)###(#_#)__)"""),
]

# Fast glitchy cycling
IDLE_SUPER_SCHEDULE = [
    0, 0, 1, 0, 0, 2, 0, 0, 3, 0,
    1, 0, 0, 2, 0, 1, 3, 0, 0, 0,
]

# ---- DEAD idle frames ----

IDLE_DEAD_FRAMES = [
    _to_frame(r"""
        /\_____/\
       /  x   x  \
      ( ==  _  == )
       )  R.I.P.  (
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\
       /  x   x  \
      ( ==  _  == )       @}-,-'--
       )  R.I.P.  (
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\          .  *  .
       /  x   x  \       ( o  o )
      ( ==  _  == )        ( ^ )   ~ boo ~
       )  R.I.P.  (         |
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),

    _to_frame(r"""
        /\_____/\
       /  x   x  \
      ( ==  _  == )
       )  R.I.P.  (
      (   ~cat~    )  @}-,-'--  @}-,-'--
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
]

# Slow, mournful cycling
IDLE_DEAD_SCHEDULE = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0,
    2, 2, 2, 2, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    3, 3, 3, 0, 0, 0, 0, 0, 0, 0,
]


# ---------------------------------------------------------------------------
# CAT ART (static, for transitions and fallback)
# ---------------------------------------------------------------------------

CAT_ALIVE = r"""
    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

    ~ meow ~
"""

CAT_ALIVE_FULL = r"""
        /\_____/\
       /  o   o  \
      ( ==  ^  == )       I'm alive! ... probably.
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)

    Status: VERY MUCH ALIVE (as far as you know)
"""

CAT_DEAD = r"""
    /\_____/\
   /  x   x  \
  ( ==  _  == )
   )  R.I.P.  (
  (    ~cat~   )
 ( (  )   (  ) )
(__(__)___(__)__)

    * the quantum has spoken *
"""

CAT_DEAD_FULL = r"""
        /\_____/\
       /  x   x  \
      ( ==  _  == )       It was the particle. It's always
       )  R.I.P.  (       the particle.
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)

    Status: DEFINITIVELY DEAD (thanks for opening the box)
"""

CAT_SUPERPOSITION = r"""
    /\_/??/\_/\
   / o?? ??x o \
  (== ^??? _? ==)      S U P E R P O S I T I O N
   ) ????????? (
  (  ???????????)
 ( ( ) ????? ( ) )
(__(__)??????(__)__)

    alive AND dead — don't peek!
"""

CAT_BOX_CLOSED = r"""
  +---------------------------+
  |                           |
  |   ???????????????????     |
  |   ???????????????????     |
  |      THE BOX IS SHUT      |
  |   ???????????????????     |
  |   ???????????????????     |
  |                           |
  +---------------------------+
  |  [QUANTUM DECAY RUNNING]  |
  +---------------------------+
"""

CAT_GHOST = r"""
        . * .  *  . *
      *    _____    .
     .   / x   x \   *
    *  (  == _ ==  )    ~ boo ~
     .   ) R.I.P.(   *
      * (  ~cat~ ) .
     .   \       / *  .
      *   \_____/   .
        . * .  *  . *
"""


# ---------------------------------------------------------------------------
# TRANSITION ANIMATION FRAMES
# ---------------------------------------------------------------------------

# Box closing: cat watches the lid come down
ANIM_BOX_CLOSING = [
    r"""
        /\_____/\
       /  O   O  \
      ( ==  ^  == )       ...what are you doing?
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)
""",
    r"""
  +=+=+=+=+=+=+=+=+=+=+=+=+=+
        /\_____/\
       /  O   O  \            wait--
      ( ==  ^  == )
  +=+=+=+=+=+=+=+=+=+=+=+=+=+
""",
    r"""
  +===========================+
  |///////////////////////////|
  |///////////////////////////|
  |////////  SEALED  /////////|
  |///////////////////////////|
  |///////////////////////////|
  +===========================+
""",
]

# Box opening: alive reveal
ANIM_OPEN_ALIVE = [
    r"""
  +===========================+
  |                           |
  |       . . . . . .        |
  |                           |
  +===========================+
""",
    r"""
  +===-----
  |   /\_____/\
  |  /  o   o  \   ...oh.
  |  ( ==  ^  == )   it's you.
  +===-----
""",
]

# Box opening: dead reveal
ANIM_OPEN_DEAD = [
    r"""
  +===========================+
  |                           |
  |       . . . . . .        |
  |                           |
  +===========================+
""",
    r"""
  +===-----
  |
  |         . . .
  |
  |             oh no.
  +===-----
""",
]

# Reboot sequence
ANIM_REBOOT = [
    r"""
  [QUANTUM RESET INITIATED]

    /\_____/\
   /  @   @  \
  ( == ??? == )     REBOOTING...
   )  ?????  (
  (  ??????????)
 ( (  )   (  ) )
(__(__)___(__)__)
""",
    r"""
  [COLLAPSING ALL WAVE FUNCTIONS]

    . . . . . . . . .
    .                 .
    .  PLEASE  STAND  .
    .      BY         .
    .                 .
    . . . . . . . . .
""",
]

# ---------------------------------------------------------------------------
# INLINE ANIMATION FRAMES — 7-line _to_frame format for in-layout animation
# These render inside the art region (rows 5-11) without clearing the TUI.
# ---------------------------------------------------------------------------

# Box closing (plays in art region)
INLINE_CLOSE = [
    _to_frame(r"""
        /\_____/\
       /  O   O  \
      ( ==  ^  == )       ...what are you doing?
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
    _to_frame(r"""
  +=+=+=+=+=+=+=+=+=+=+=+=+=+
        /\_____/\
       /  O   O  \            wait--
      ( ==  ^  == )
  +=+=+=+=+=+=+=+=+=+=+=+=+=+
                              """),
    _to_frame(r"""
  +===========================+
  |///////////////////////////|
  |///////////////////////////|
  |////////  SEALED  /////////|
  |///////////////////////////|
  |///////////////////////////|
  +===========================+"""),
]

# Box opening → alive (plays in art region)
INLINE_OPEN_ALIVE = [
    _to_frame(r"""
  +===========================+
  |                           |
  |                           |
  |       . . . . . .        |
  |                           |
  |                           |
  +===========================+"""),
    _to_frame(r"""
  +===-----
  |   /\_____/\
  |  /  o   o  \              ...oh.
  |  ( ==  ^  == )            it's you.
  +===-----

                              """),
]

# Box opening → dead (plays in art region)
INLINE_OPEN_DEAD = [
    _to_frame(r"""
  +===========================+
  |                           |
  |                           |
  |       . . . . . .        |
  |                           |
  |                           |
  +===========================+"""),
    _to_frame(r"""
  +===-----
  |
  |         . . .
  |
  |             oh no.
  +===-----
                              """),
]

# Death detected mid-superposition (plays in art region)
INLINE_DEATH = [
    _to_frame(r"""
    /\_/##/\_/\
   / x## ##x x \
  (== _### #? ==)             !! QUANTUM EVENT !!
   ) ######### (
  (  ###########)
 ( ( ) ##### ( ) )
(__(__)######(__)__)"""),
    _to_frame(r"""
        /\_____/\
       /  x   x  \
      ( ==  _  == )           !! WAVE FUNCTION COLLAPSED !!
       )  R.I.P.  (
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
]

# Pet → alive
INLINE_PET_ALIVE = [
    _to_frame(r"""
        /\_____/\
  -->  /  O   O  \
      ( ==  ^  == )       ...a hand approaches.
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
    _to_frame(r"""
        /\_____/\
  ~~~  /  ^   ^  \
      ( == ~w~ == )       *purrrrrrrr*
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
    _to_frame(r"""
        /\_____/\
       /  -   -  \
      ( == ^w^ == )       Quantum state: JUDGED.
       )         (
      (     w     )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
]

# Pet → superposition
INLINE_PET_SUPER = [
    _to_frame(r"""
  +---------------------------+
  |                           |
  -->  ???????????????????    |       You reach for the box...
  |    ???????????????????    |
  |       THE BOX IS SHUT     |
  |                           |
  +---------------------------+"""),
    _to_frame(r"""
  +---------------------------+
  |                           |
  |  You cannot pet what you  |
  |  cannot observe.          |       The box is sealed.
  |                           |
  |  The cat is Schrodinger's |
  +---------------------------+"""),
]

# Pet → dead
INLINE_PET_DEAD = [
    _to_frame(r"""
        /\_____/\
  -->  /  x   x  \
      ( ==  _  == )       ...you reach into the box.
       )  R.I.P.  (
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
    _to_frame(r"""
        /\_____/\
       /  x   x  \
      ( ==  _  == )       The cat does not respond.
       )  R.I.P.  (       The cat will never respond again.
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
    _to_frame(r"""
        /\_____/\
       /  x   x  \
      ( ==  _  == )
       )  R.I.P.  (       Please do not pet dead cats.
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
]

# Reboot (plays in art region)
INLINE_REBOOT = [
    _to_frame(r"""
    [QUANTUM RESET INITIATED]

        /\_____/\
       /  @   @  \
      ( == ??? == )       REBOOTING...
     ( (  )   (  ) )
    (__(__)___(__)__)"""),
    _to_frame(r"""
    [COLLAPSING ALL WAVE FUNCTIONS]

    . . . . . . . . . . .
    .                     .
    .    PLEASE  STAND    .
    .        BY           .
    . . . . . . . . . . ."""),
]


# ---------------------------------------------------------------------------
# LEGACY TRANSITION FRAMES (full-screen, kept for reference)
# ---------------------------------------------------------------------------

# Death detected mid-superposition
ANIM_DEATH_DETECTED = [
    r"""

    !! QUANTUM EVENT DETECTED !!

    /\_/##/\_/\
   / x## ##x x \
  (== _### #? ==)
   ) ######### (
  (  ###########)
 ( ( ) ##### ( ) )
(__(__)######(__)__)
""",
    r"""

    !! WAVE FUNCTION COLLAPSED !!

        /\_____/\
       /  x   x  \
      ( ==  _  == )
       )  R.I.P.  (
      (   ~cat~    )
     ( (  )   (  ) )
    (__(__)___(__)__)
""",
]


# ---------------------------------------------------------------------------
# WELCOME / INTRO SCREEN
# ---------------------------------------------------------------------------

WELCOME_BANNER = r"""
========================================================================
   ____      _               _ _             _
  / ___|  __| |__  _ __ ___ | (_)_ __   __ _| |
  \___ \ / _` '__ \| '__/ _ \| | | '_ \ / _` | |
   ___) | (_| | | | | | | (_) | | | | | | (_| | |_
  |____/ \__,_|_| |_|_|  \___/|_|_|_| |_|\__, |_(_)
   ____      _   _               _          |_|
  / ___|__ _| |_| |__   ___ __  | |
 | |   / _` | __| '_ \ / _ \\ \/ /| |
 | |__| (_| | |_| |_) | (_) |>  < |_|
  \____\__,_|\__|_.__/ \___//_/\_\(_)

========================================================================
"""

WELCOME_SHORT = r"""
+----------------------------------------------------------------------+
|               *** SCHRODINGER'S CATBOX ***                           |
+----------------------------------------------------------------------+
"""


# ---------------------------------------------------------------------------
# TUI-FRIENDLY COMPACT DESCRIPTIONS (fit in 4 lines for 80x24 layout)
# ---------------------------------------------------------------------------

TUI_DESC_ALIVE = [
    "The cat sits in its open box, blissfully unaware of quantum",
    "mechanics. The Geiger counter is silent. The cat is fine.",
    "Probably smug about it.",
]

TUI_DESC_SUPER = [
    "The box is sealed. The cat exists in quantum superposition --",
    "simultaneously alive AND dead, until observation collapses",
    "the wave function. Don't think about it too hard.",
]

TUI_DESC_DEAD = [
    "The radioactive particle decayed. The Geiger counter fired.",
    "The flask shattered. It is an ex-cat. It has ceased to be.",
    "The only cure: REBOOT the universe (or just the Pi).",
]


# ---------------------------------------------------------------------------
# STATE HEADERS (short, for TUI status row)
# ---------------------------------------------------------------------------

TUI_STATE_ALIVE = "[ BOX: OPEN ]  [ CAT: ALIVE ]"
TUI_STATE_SUPER = "[ BOX: CLOSED ]  [ STATE: UNKNOWN ]"
TUI_STATE_DEAD  = "[ BOX: OPEN ]  [ CAT: DEAD ]"


# ---------------------------------------------------------------------------
# STATE-SPECIFIC MESSAGES (kept for transition text)
# ---------------------------------------------------------------------------

MSG_ALIVE_HEADER = """
[ THE BOX IS OPEN ]  [ THE CAT IS ALIVE ]
"""

MSG_ALIVE_DESCRIPTION = """
The cat sits in its open box, blissfully unaware of quantum mechanics.
No radioactive particle has been detected. No poison flask has tipped.
The Geiger counter is silent. The cat is fine. Probably smug about it.
"""

MSG_DEAD_HEADER = """
[ THE BOX IS OPEN ]  [ THE CAT IS DEAD ]
"""

MSG_DEAD_DESCRIPTION = """
The radioactive particle decayed while the box was closed. The Geiger
counter fired. The flask shattered. The cat has shuffled off this mortal
coil. It is an ex-cat. It has ceased to be.

The only cure: a full reboot of the universe (or just the Raspberry Pi).
Type REBOOT to restart the experiment.
"""

MSG_SUPERPOSITION_HEADER = """
[ THE BOX IS CLOSED ]  [ STATE: UNKNOWN ]
"""

MSG_SUPERPOSITION_DESCRIPTION = """
The box is sealed. The cat exists in quantum superposition — simultaneously
alive AND dead, until observation collapses the wave function.

A radioactive atom may or may not have decayed. A Geiger counter may or may
not have fired. A flask of poison may or may not have shattered.

The cat is fine. The cat is dead. The cat is Schrodinger's problem now.
"""


# ---------------------------------------------------------------------------
# COMMAND PROMPTS & INTERACTION TEXT
# ---------------------------------------------------------------------------

TUI_ACTION_ALIVE = [
    ">> Type CLOSE to close the box and begin quantum decay.",
]

TUI_ACTION_SUPER = [
    ">> Type OPEN to open the box and collapse the superposition.",
    "   (Warning: you might not like what you find.)",
]

TUI_ACTION_DEAD = [
    ">> The cat is dead. Type REBOOT to restart the experiment.",
    "   (Or just sit with the weight of your choices.)",
]

PROMPT_OPEN_BOX = """
>> Type CLOSE to close the box and begin quantum decay.
"""

PROMPT_CLOSED_BOX = """
>> Type OPEN to open the box and collapse the superposition.
   (Warning: you might not like what you find.)
"""

PROMPT_DEAD_BOX = """
>> The cat is dead. There is nothing left to do here.
   Type REBOOT to restart the experiment.
   (Or just sit with the weight of your choices.)
"""

CMD_HELP = """
+------------------------------------------------------------------+
| COMMANDS                                                          |
|                                                                   |
|   CLOSE    -- Close the box. Quantum decay begins.               |
|   OPEN     -- Open the box. Superposition collapses.             |
|   PET      -- Pet the cat. (Results may vary.)                   |
|   STATUS   -- Display current state.                             |
|   REBOOT   -- Reboot the Pi. Revive the cat.                    |
|   HELP     -- Show this help text.                               |
|   QUIT     -- Disconnect.                                        |
|                                                                   |
| NOTE: Once the cat is dead, only a reboot revives it.            |
+------------------------------------------------------------------+
"""


# ---------------------------------------------------------------------------
# TRANSITION MESSAGES
# ---------------------------------------------------------------------------

MSG_BOX_CLOSING = """
You reach for the lid...

  [click]

The box is sealed. The quantum experiment has begun.
The cat's fate is now entangled with a radioactive atom.
Don't think about it too hard.
"""

MSG_BOX_OPENING_ALIVE = """
You lift the lid with trembling hands...

...

...the cat stares back at you, deeply unimpressed.

It's alive. This time.
"""

MSG_BOX_OPENING_DEAD = """
You lift the lid with trembling hands...

...

...

Oh.

The quantum particle decayed while the box was closed.
The Geiger counter fired. The flask tipped. The cat is gone.

You did this. (Schrodinger did this. Quantum mechanics did this.)
(Okay, maybe you did this a little.)
"""

MSG_REBOOT = """
Initiating quantum reset...
The cat's universe is rebooting.
All wave functions will be resolved. All superpositions collapsed.
The cat will live again.

Goodbye.
"""


# ---------------------------------------------------------------------------
# ERROR / UNKNOWN COMMAND MESSAGES
# ---------------------------------------------------------------------------

MSG_UNKNOWN_CMD = """
The cat does not recognize that command. (The cat is judging you.)
Type HELP to see available commands.
"""

MSG_ALREADY_OPEN = """
The box is already open. The cat can see you. It blinks slowly.
This is not a situation that requires further commands.
"""

MSG_ALREADY_CLOSED = """
The box is already closed! The experiment is underway.
Please wait — or open the box and face your destiny.
"""


# ---------------------------------------------------------------------------
# FOOTER / FLAVOR TEXT
# ---------------------------------------------------------------------------

FOOTER = "Schrodinger's Catbox  |  catbox.local"

FLAVOR_TEXTS_ALIVE = [
    "The cat is in its happy place. Warm. Fed. Blissfully pre-quantum.",
    "No particles have decayed today. Good day to be a cat.",
    "The wave function is unsettled. The cat has opinions about none of it.",
    "Alive and judgmental. As cats tend to be.",
    "Technically, the cat was always going to be fine. Probably.",
]

FLAVOR_TEXTS_DEAD = [
    "The universe is indifferent. The cat is a casualty of probability.",
    "In another branch of the many-worlds interpretation, the cat lived.",
    "The half-life of the atom was shorter than the cat's nine lives.",
    "The cat existed. Then the particle decided otherwise.",
    "Observation: complete. Outcome: unfortunate.",
]

FLAVOR_TEXTS_CLOSED = [
    "The particle is either decayed or not. The cat is either fine or not.",
    "Quantum uncertainty: nature's way of keeping you guessing.",
    "Schrodinger reportedly was trying to argue AGAINST this interpretation.",
    "The cat has thoughts about being placed in boxes. Many thoughts.",
    "Heisenberg is watching. So is the cat, in some sense.",
]
