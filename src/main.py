#!/usr/bin/env python3
"""
main.py — Entry point for Schrödinger's Catbox telnet server.

Usage
-----
    python3 main.py [--port PORT] [--half-life SECONDS]

The server listens for telnet connections on the specified port and runs the
quantum Schrödinger's Catbox experiment.  A single CatBox instance is shared
across all connections.  SIGTERM and SIGINT trigger a graceful shutdown.
"""

import argparse
import signal
import sys
import threading
import os

# Ensure the src/ directory is on the path when invoked directly.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from cat_state import CatBox
import server as _server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Schrödinger's Catbox — quantum art installation telnet server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1701,
        help="TCP port to listen on",
    )
    parser.add_argument(
        "--half-life",
        type=float,
        default=30.0,
        dest="half_life",
        help="Quantum decay half-life in seconds",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Create the shared CatBox and register it with the server module.
    box = CatBox(half_life=args.half_life)
    _server.set_catbox(box)

    # Create the threaded telnet server.
    srv = _server.create_server(port=args.port)

    # Graceful shutdown handler for SIGTERM and SIGINT.
    def _shutdown(sig, frame):
        print(f"\n[catbox] Received signal {sig} — shutting down...", flush=True)
        threading.Thread(target=srv.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, _shutdown)
    try:
        signal.signal(signal.SIGTERM, _shutdown)
    except (OSError, AttributeError):
        pass  # SIGTERM not available on all platforms (e.g. Windows)

    print(f"[catbox] Starting Schrödinger's Catbox", flush=True)
    print(f"[catbox] Port      : {args.port}", flush=True)
    print(f"[catbox] Half-life : {args.half_life}s", flush=True)
    print(f"[catbox] telnet localhost {args.port}", flush=True)
    print(f"[catbox] Press Ctrl-C to stop.", flush=True)

    srv.serve_forever()
    print("[catbox] Server stopped.", flush=True)


if __name__ == "__main__":
    main()
