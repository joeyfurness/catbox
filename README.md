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

**A conceptual art installation where a digital cat exists in quantum superposition — until you look.**

A Raspberry Pi sits in a gallery. On boot, a program called `cat` starts running.
Visitors telnet in, close the box, and wait. A simulated radioactive atom
begins to decay. Open the box and the wavefunction collapses.

The cat is alive, or the cat is dead. You won't know until you look.

Once dead, the cat stays dead — until someone reboots the Pi.

---

## How It Works

```
telnet catbox.local 1701
```

That's it. No login. No password. Just a raw terminal and a cat.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         SCHRODINGER'S CATBOX                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  [ BOX: OPEN ]  [ CAT: ALIVE ]                                            ║
║──────────────────────────────────────────────────────────────────────────── ║
║                                                                            ║
║      /\_____/\                                                             ║
║     /  o   o  \                                                            ║
║    ( ==  ^  == )       I'm alive! ... probably.                            ║
║     )         (                                                            ║
║    (     w     )                                                           ║
║   ( (  )   (  ) )                                                          ║
║  (__(__)___(__)__)                                                         ║
║                                                                            ║
║  The cat is here. It's alive. It seems happy.                              ║
║  But how long will that last?                                              ║
║                                                                            ║
║  > _                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Commands

| Command | What happens |
|---------|-------------|
| `CLOSE` | Seal the box. Superposition begins. The atom starts to decay. |
| `OPEN` | Open the box. The wavefunction collapses. Hope for the best. |
| `PET` | Pet the cat. Response varies by... circumstances. |
| `STATUS` | Check the current state of things. |
| `HELP` | You probably don't need this. But it's there. |
| `QUIT` | Walk away. The cat doesn't care. (Or does it?) |
| `REBOOT` | Power cycle the Pi. The only way to bring back the dead. |

---

## The Quantum Mechanics

While the box is closed, a background process simulates radioactive decay
using an exponential probability distribution:

```
P(decay by time t) = 1 - e^(-λt)

where λ = ln(2) / half_life
```

**Default half-life: 30 seconds.**

| Time closed | Probability the cat is dead |
|------------|----------------------------|
| 0 seconds | 0% |
| 15 seconds | ~29% |
| 30 seconds | 50% |
| 1 minute | 75% |
| 2 minutes | 93.75% |
| 5 minutes | 99.9% |

The dice roll happens every 500ms. You can watch the probability climb in
real-time on the stats line. You just can't know the outcome until you open
the box.

---

## The Art

The program is called `cat`. Yes, it shadows `/bin/cat`. That's the point.

```bash
$ which cat
/home/schrodinger/catbox/src/main.py

$ cat          # this doesn't concatenate files anymore
               # it runs a quantum physics experiment
```

The Pi runs headless. There is no monitor. The cat exists only for those who
connect to it — observation is the interface. Multiple visitors can connect
simultaneously and share the same cat. One person closes the box, another
opens it. Collective responsibility for quantum murder.

The cat has idle animations. It blinks. It yawns. It falls asleep.
In superposition, it glitches — half-alive, half-dead, bits of both leaking
through. When dead, flowers appear. A ghost drifts by.

---

## Running It

### On the Pi

```bash
# The systemd service starts on boot
sudo systemctl status cat

# Watch the logs
journalctl -u cat -f

# Restart (and revive the cat)
sudo reboot
```

### Locally (for development)

```bash
python3 src/main.py --port 1701 --half-life 30

# Then in another terminal:
telnet localhost 1701
```

### Deploying

```bash
# Push to main — auto-deploys to the Pi
git push origin main
```

### CLI Options

```
--port PORT         Telnet port (default: 1701)
--half-life SECS    Decay half-life in seconds (default: 30)
```

---

## Architecture

```
src/
├── main.py        # Entry point, CLI args, signal handling
├── cat_state.py   # The quantum state machine (3 states, thread-safe)
├── server.py      # Threaded telnet server, TUI rendering, animations
├── tui.py         # Fixed-position 80x24 terminal layout (ANSI escapes)
└── art.py         # ASCII art, idle animations, flavor text, vibes

systemd/
└── cat.service    # Runs on boot as the 'schrodinger' user

deploy.sh          # SCP + restart (also triggered by git push to main)
```

**Zero external dependencies.** Python 3 stdlib only. As it should be.

---

## States

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

The cat is here. It's happy. Don't ruin this.

### Superposition

```
    /\_/??/\_/\
   / o?? ??x o \
  (== ^??? _? ==)     |alive⟩ + |dead⟩
   ) ????????? (
  (  ???????????)
 ( ( ) ????? ( ) )
(__(__)??????(__)__)
```

Is it alive? Is it dead? It's both. It's neither. The box is closed.
You did this.

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

You opened the box and the cat was dead.
It will stay dead until someone reboots the Pi.
Think about what you've done.

---

## FAQ

**Q: Can I save the cat?**
A: Don't close the box.

**Q: Can I bring it back?**
A: `sudo reboot`. Or unplug the Pi and plug it back in. Like God intended.

**Q: What if I close the box and never open it?**
A: Then the cat remains in superposition forever. Schrödinger would be proud.
But the probability display will keep climbing toward 100%, and you'll know.
You'll know.

**Q: Can multiple people connect at once?**
A: Yes. You all share the same cat. Mutual observers of the same quantum system.

**Q: Why telnet?**
A: No auth, no encryption, no pretense. Raw TCP. The way terminals were meant to be.
Also it looks cool.

**Q: Why is the program called `cat`?**
A: `cat` is dead. Long live `cat`.

**Q: Is this actually quantum mechanics?**
A: It's a random number generator with exponential decay statistics. So... yes?
About as quantum as Schrödinger's original thought experiment, which was also
just a metaphor.

---

## Credits

A thing by Joey. The cat is fictional. Probably.

```
    /\_____/\
   /  -   -  \
  ( ==  ^  == )    zzZ
   )         (
  (     w     )
 ( (  )   (  ) )
(__(__)___(__)__)
```
