```
     /\_____/\
    /  o   o  \
   ( ==  ^  == )
    )         (
   (     w     )
  ( (  )   (  ) )
 (__(__)___(__)__)
```

# Schrodinger's Catbox

A Raspberry Pi sits in a room. On boot, a program called `cat` starts. You telnet in, there's a cat. You can pet it.

Then you close the box.

While the box is closed, a simulated radioactive atom decays in the background. Maybe it already triggered. Maybe not. Open the box to find out. If the atom decayed, the cat is dead. It stays dead. Only way back is `sudo reboot`.

## Connecting

```
telnet catbox.local 1701
```

No login. No password.

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

| Command | |
|---------|---|
| `CLOSE` | Seal the box. Superposition begins. |
| `OPEN` | Collapse the wavefunction. |
| `PET` | Pet the cat. |
| `STATUS` | Check on things. |
| `HELP` | Help. |
| `QUIT` | Leave. |
| `REBOOT` | Power cycle the Pi. Only known cure for death. |

## The math

Exponential decay while the box is closed:

```
P(decay by time t) = 1 - e^(-lambda*t)

where lambda = ln(2) / half_life
```

Default half-life is 30 seconds.

| Time closed | Chance dead |
|------------|-------------|
| 0s | 0% |
| 15s | ~29% |
| 30s | 50% |
| 1 min | 75% |
| 2 min | 93.75% |
| 5 min | 99.9% |

Dice roll every 500ms. There's a probability counter ticking up in real-time while you watch. You don't know the actual outcome until you open it.

## Why `cat`

```bash
$ which cat
/home/schrodinger/catbox/src/main.py

$ cat
# doesn't concatenate files anymore
# runs a quantum physics experiment instead
```

The Pi is headless. No monitor. The cat exists only when someone connects to observe it. Multiple visitors share the same cat. One person closes the box, someone else opens it.

It has idle animations. Blinks, yawns, falls asleep. In superposition it glitches. Half-alive, half-dead, bits of each state bleeding through. When it dies, flowers grow. A ghost drifts by sometimes.

## The three states

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

Don't touch anything.

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

You closed the box and now you have to live with this.

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

Stays dead until reboot.

## Running it

### On the Pi

```bash
sudo systemctl status cat
journalctl -u cat -f
sudo reboot    # bring the cat back
```

### Local dev

```bash
python3 src/main.py --port 1701 --half-life 30
telnet localhost 1701
```

### Deploying

```bash
git push origin main
```

Auto-deploys to the Pi.

### Flags

```
--port PORT         Telnet port (default: 1701)
--half-life SECS    Decay half-life in seconds (default: 30)
```

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

No external dependencies. Python 3 stdlib only.

## FAQ

**Can I save the cat?**
Don't close the box.

**Can I bring it back?**
`sudo reboot`

**What if I close the box and never open it?**
Then it stays in superposition forever. But that probability counter keeps ticking toward 100% and at some point you're just lying to yourself.

**Multiple people?**
Same cat for everyone. The group dynamics around who closes the box are actually kind of interesting.

**Why telnet?**
Raw TCP. No auth. Fits the look. Didn't want to deal with SSH keys for gallery visitors.

**Is this real quantum mechanics?**
It's a random number generator with exponential decay statistics. About as quantum as Schrodinger's original thought experiment, which was also just a metaphor. He was making fun of the Copenhagen interpretation, not endorsing it. People forget that.

---

Made by Joey.

```
    /\_____/\
   /  -   -  \
  ( ==  ^  == )    zzZ
   )         (
  (     w     )
 ( (  )   (  ) )
(__(__)___(__)__)
```
