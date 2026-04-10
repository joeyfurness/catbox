```
     /\_____/\
    /  o   o  \
   ( ==  ^  == )
    )         (        You found the catbox.
   (     w     )
  ( (  )   (  ) )
 (__(__)___(__)__)
```

# Schrodinger's Catbox

**A digital cat that might be dead. You have to look to find out.**

So there's a Raspberry Pi sitting in a room somewhere. When it boots, a program
called `cat` starts running. (Yes, *that* `cat`. We'll get to that.)

You telnet in. There's a cat. It's alive. It's vibing. You can pet it.

Then you close the box.

While the box is closed, a simulated radioactive atom is decaying in the background.
Maybe it's already triggered. Maybe it hasn't. You don't know. Open the box and
find out. Or don't. The cat doesn't care. (Or does it?)

If the atom decayed, the cat is dead. It stays dead. The only resurrection
is `sudo reboot`.

---

## How It Works

```
telnet catbox.local 1701
```

No login. No password. Just a cat.

```
+==============================================================================+
|                         SCHRODINGER'S CATBOX                                 |
+==============================================================================+
|  [ BOX: OPEN ]  [ CAT: ALIVE ]                                              |
|----------------------------------------------------------------------------- |
|                                                                              |
|      /\_____/\                                                               |
|     /  o   o  \                                                              |
|    ( ==  ^  == )       I'm alive! ... probably.                              |
|     )         (                                                              |
|    (     w     )                                                             |
|   ( (  )   (  ) )                                                            |
|  (__(__)___(__)__)                                                           |
|                                                                              |
|  The cat is here. It's alive. It seems happy.                                |
|  But how long will that last?                                                |
|                                                                              |
|  > _                                                                         |
+==============================================================================+
```

### Commands

| Command | What happens |
|---------|-------------|
| `CLOSE` | Seal the box. Superposition begins. The atom starts to decay. |
| `OPEN` | Open the box. Collapse the wavefunction. Good luck. |
| `PET` | Pet the cat. (Results may vary depending on... aliveness.) |
| `STATUS` | What's going on in there? |
| `HELP` | It's there if you need it. |
| `QUIT` | Walk away. |
| `REBOOT` | Power cycle the Pi. The only known cure for death. |

---

## The Quantum Mechanics (sort of)

While the box is closed, a background process rolls dice using an exponential
probability distribution:

```
P(decay by time t) = 1 - e^(-lambda*t)

where lambda = ln(2) / half_life
```

Half-life is 30 seconds by default. So:

| Time closed | Chance the cat is dead |
|------------|----------------------|
| 0 seconds | 0% |
| 15 seconds | ~29% |
| 30 seconds | 50% |
| 1 minute | 75% |
| 2 minutes | 93.75% |
| 5 minutes | 99.9% — yeah it's dead |

The dice roll happens every 500ms. There's a probability counter ticking up in
real-time while the box is closed, which is a fun thing to stare at while you
contemplate what you've set in motion. But you still don't know the actual outcome
until you open it.

---

## Why is `cat` called `cat`

Because it's funny.

```bash
$ which cat
/home/schrodinger/catbox/src/main.py

$ cat          # doesn't concatenate files anymore
               # runs a quantum physics experiment instead
```

This is the whole bit. The Pi runs headless — no monitor, no display.
The cat exists only when someone connects to observe it. Multiple visitors
can connect at once and they all share the same cat. One person closes
the box, someone else opens it. Distributed quantum murder.

The cat has idle animations too. It blinks, yawns, falls asleep if you
leave it alone long enough. In superposition it glitches out — half-alive,
half-dead, bits of each state bleeding through. When it's dead, flowers
grow. A ghost drifts by sometimes. I spent way too long on the ghost.

---

## Running It

### On the Pi

```bash
# systemd starts it on boot
sudo systemctl status cat

# tail the logs
journalctl -u cat -f

# bring the cat back from the dead
sudo reboot
```

### Local dev

```bash
python3 src/main.py --port 1701 --half-life 30

# then:
telnet localhost 1701
```

### Deploying

```bash
git push origin main
# that's it, auto-deploys to the Pi
```

### CLI flags

```
--port PORT         Telnet port (default: 1701)
--half-life SECS    Decay half-life in seconds (default: 30)
```

---

## Architecture

```
src/
  main.py        - Entry point, CLI args, signal handling
  cat_state.py   - The quantum state machine (thread-safe, 3 states)
  server.py      - Threaded telnet server, TUI rendering, animations
  tui.py         - Fixed 80x24 terminal layout via ANSI escapes
  art.py         - ASCII art, idle animations, flavor text

systemd/
  cat.service    - Runs on boot as the 'schrodinger' user

deploy.sh        - SCP + restart (also triggered by push to main)
```

Zero external dependencies. Python 3 stdlib only.

---

## The Three States

### Alive

```
    /\_____/\
   /  o   o  \
  ( ==  ^  == )       I'm alive! ... probably.
   )         (
  (     w     )
 ( (  )   (  ) )
(__(__)___(__)__)
```

It's fine. Everything is fine. Don't touch anything.

### Superposition

```
    /\_/??/\_/\
   / o?? ??x o \
  (== ^??? _? ==)     |alive> + |dead>
   ) ????????? (
  (  ???????????)
 ( ( ) ????? ( ) )
(__(__)??????(__)__)
```

Both alive and dead. Neither alive nor dead. You closed the box
and now you have to live with this ambiguity.

### Dead

```
    /\_____/\
   /  x   x  \
  ( ==  _  == )
   )  R.I.P.  (
  (   ~cat~    )
 ( (  )   (  ) )
(__(__)___(__)__)
```

You killed it. Well — you might have killed it when you closed the box,
or it might have been the opening that did it. Depends on your
interpretation of quantum mechanics, I guess.

Stays dead until reboot. Think about what you've done.

---

## FAQ

**Can I save the cat?**
Don't close the box.

**Can I bring it back?**
`sudo reboot`. Or just yank the power cord and plug it back in. Same thing.

**What if I close the box and never open it?**
Then the cat stays in superposition forever. Schrodinger would approve.
But that probability counter is going to keep ticking toward 100% and
at some point you're just lying to yourself.

**Can multiple people connect?**
Yep. Same cat for everyone. Mutual observers of the same quantum system.
One of you will probably close the box. The group dynamics around this are
actually kind of interesting.

**Why telnet?**
No auth, no encryption, no ceremony. Raw TCP. It looks cool and it
fits the vibe. Also I didn't want to deal with SSH key management for
gallery visitors.

**Why is the program called `cat`?**
`cat` is dead. Long live `cat`.

**Is this real quantum mechanics?**
It's a random number generator with exponential decay statistics.
So about as quantum as Schrodinger's original thought experiment, which
was also just a metaphor. (He was making fun of the Copenhagen
interpretation, not endorsing it. People forget that part.)

---

## Credits

Made by Joey. The cat is fictional. Probably.

```
    /\_____/\
   /  -   -  \
  ( ==  ^  == )    zzZ
   )         (
  (     w     )
 ( (  )   (  ) )
(__(__)___(__)__)
```
