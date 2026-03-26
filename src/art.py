"""
art.py — ASCII art and text strings for Schrödinger's Catbox
All art kept within 80 columns.
"""

# ---------------------------------------------------------------------------
# CAT ART
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
# STATE-SPECIFIC MESSAGES
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

PROMPT_OPEN_BOX = """
>> Type CLOSE to close the box and begin quantum decay.
"""

PROMPT_CLOSED_BOX = """
>> Type OPEN to open the box and collapse the superposition.
   (Warning: you might not like what you find.)
"""

PROMPT_DEAD_BOX = """
>> The cat is dead. There is nothing left to do here.
   Power-cycle the Pi to start a new experiment.
   (Or just sit with the weight of your choices.)
"""

CMD_HELP = """
+------------------------------------------------------------------+
| COMMANDS                                                          |
|                                                                   |
|   CLOSE    -- Close the box. Quantum decay begins.               |
|   OPEN     -- Open the box. Superposition collapses.             |
|   STATUS   -- Display current state.                             |
|   HELP     -- Show this help text.                               |
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

FOOTER = """
------------------------------------------------------------------------
  Schrodinger's Catbox  |  catbox.local
  telnet for visitors   |  ssh for the artist
------------------------------------------------------------------------
"""

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
