# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Schrödinger's Catbox** — a conceptual art installation running on a headless Raspberry Pi (`schrodinger@catbox.local`). A program called `cat` runs on boot displaying an ASCII cat. Visitors can interact remotely to "close the box" (starting quantum decay via RNG) and "open the box" (collapsing the superposition, potentially killing the cat). Only a reboot revives a dead cat.

## Target Architecture

- **Runtime**: Headless Raspberry Pi (Debian/Raspbian), accessed via SSH
- **Deploy target**: `schrodinger@catbox.local` (SSH keys should be in `~/.ssh`)
- **Boot service**: `cat` process starts on boot via systemd unit
- **Remote interaction**: Telnet server (port 23 or custom) — allows unauthenticated, raw-text interaction fitting the art piece aesthetic. No SSH session needed for visitors.
- **Language**: Python 3 (available on Raspbian by default) or C — keep dependencies minimal

## Core Concepts

| State | Description |
|-------|-------------|
| **Alive** | Cat is displayed, box is open, no decay process running |
| **Box Closed** | Superposition begins — RNG "quantum decay" runs in background |
| **Box Opened** | Superposition collapses — if RNG triggered during closed period, cat is dead |
| **Dead** | Cat is dead. Only a reboot (power cycle) revives it |

The random decay simulates radioactive decay: while the box is closed, a random event may "kill" the cat at any moment. Opening the box reveals the outcome. Once dead, the cat stays dead until the Pi reboots.

## Key Commands

```bash
# Deploy to Pi
scp -r ./src/ schrodinger@catbox.local:~/catbox/
ssh schrodinger@catbox.local 'sudo systemctl restart cat'

# SSH into the Pi
ssh schrodinger@catbox.local

# Test the telnet interface locally on the Pi
telnet localhost <PORT>

# Check service status
ssh schrodinger@catbox.local 'systemctl status cat'

# View logs
ssh schrodinger@catbox.local 'journalctl -u cat -f'

# Reboot (revive the cat)
ssh schrodinger@catbox.local 'sudo reboot'
```

## Design Principles

- **Playful and whimsical** — this is art, not enterprise software. ASCII art, fun messages, personality in the text.
- **Minimal dependencies** — should run with Python stdlib or basic C. No pip installs if avoidable.
- **Stateless on disk** — cat state lives only in memory. Reboot = fresh start = alive cat.
- **Telnet for visitors** — raw TCP/telnet gives the retro terminal aesthetic and requires no auth. SSH is for the artist/admin only.
- **The cat program must be named `cat`** — yes, this shadows `/bin/cat`. That's part of the art.
