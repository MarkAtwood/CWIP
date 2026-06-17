#!/usr/bin/env python3
"""
CWIP Monitor - ncurses display of CWIP traffic.

Shows incoming tiles, signal quality, and decoded packets.
The thing people will screenshot.

Usage:
    python cwip_monitor.py --device /dev/ttyUSB0
    python cwip_monitor.py --demo  # Demo mode with fake data
"""

import argparse
import sys
import time
from datetime import datetime
from collections import deque

# Only import curses if we're running interactively
try:
    import curses
    HAS_CURSES = True
except ImportError:
    HAS_CURSES = False

sys.path.insert(0, '..')


class MonitorState:
    """State for the monitor display."""

    def __init__(self):
        self.tiles_rx = 0
        self.tiles_tx = 0
        self.bytes_rx = 0
        self.bytes_tx = 0
        self.errors_corrected = 0
        self.errors_failed = 0
        self.snr_db = 0.0
        self.last_callsign = ""
        self.last_grid = ""
        self.log = deque(maxlen=20)
        self.start_time = time.time()

    def add_log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"{timestamp} {msg}")


def draw_screen(stdscr, state: MonitorState):
    """Draw the monitor UI."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Title
    title = " CWIP Monitor "
    stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_REVERSE)

    # Stats box
    stdscr.addstr(2, 2, "┌─ Statistics ─────────────────────────┐")
    stdscr.addstr(3, 2, f"│ Tiles RX: {state.tiles_rx:>10}               │")
    stdscr.addstr(4, 2, f"│ Tiles TX: {state.tiles_tx:>10}               │")
    stdscr.addstr(5, 2, f"│ Bytes RX: {state.bytes_rx:>10}               │")
    stdscr.addstr(6, 2, f"│ Bytes TX: {state.bytes_tx:>10}               │")
    stdscr.addstr(7, 2, f"│ FEC Corrected: {state.errors_corrected:>5}              │")
    stdscr.addstr(8, 2, f"│ FEC Failed:    {state.errors_failed:>5}              │")
    stdscr.addstr(9, 2, "└──────────────────────────────────────┘")

    # Signal box
    stdscr.addstr(2, 45, "┌─ Signal ──────────────────┐")
    stdscr.addstr(3, 45, f"│ SNR: {state.snr_db:>+6.1f} dB           │")
    stdscr.addstr(4, 45, f"│ Last: {state.last_callsign:<12}       │")
    stdscr.addstr(5, 45, f"│ Grid: {state.last_grid:<12}       │")
    stdscr.addstr(6, 45, "│                           │")

    # SNR bar
    snr_bar_width = 20
    snr_normalized = max(0, min(1, (state.snr_db + 20) / 40))  # -20 to +20 dB
    bar_filled = int(snr_bar_width * snr_normalized)
    bar = "█" * bar_filled + "░" * (snr_bar_width - bar_filled)
    stdscr.addstr(7, 45, f"│ [{bar}] │")
    stdscr.addstr(8, 45, "│  -20 dB          +20 dB  │")
    stdscr.addstr(9, 45, "└───────────────────────────┘")

    # Log
    log_start = 11
    stdscr.addstr(log_start, 2, "┌─ Activity Log ─" + "─" * (width - 22) + "┐")
    for i, msg in enumerate(state.log):
        if log_start + 1 + i >= height - 2:
            break
        line = f"│ {msg}"
        line = line[:width-4] + " " * (width - 4 - len(line)) + "│"
        stdscr.addstr(log_start + 1 + i, 2, line)

    # Fill remaining log lines
    for i in range(len(state.log), min(15, height - log_start - 3)):
        line = "│" + " " * (width - 6) + "│"
        stdscr.addstr(log_start + 1 + i, 2, line)

    log_end = min(log_start + 16, height - 2)
    stdscr.addstr(log_end, 2, "└" + "─" * (width - 6) + "┘")

    # Footer
    uptime = int(time.time() - state.start_time)
    footer = f" q=quit │ Uptime: {uptime//3600:02d}:{(uptime//60)%60:02d}:{uptime%60:02d} "
    stdscr.addstr(height - 1, (width - len(footer)) // 2, footer, curses.A_REVERSE)

    stdscr.refresh()


def demo_mode(stdscr):
    """Run demo with simulated data."""
    import random

    curses.curs_set(0)
    stdscr.nodelay(True)

    state = MonitorState()
    state.add_log("Starting CWIP monitor (demo mode)")
    state.add_log("Listening on 7.055 MHz...")

    callsigns = ["K7ABC", "W1XYZ", "VE3DEF", "G4XYZ", "JA1ABC"]
    grids = ["CN87", "FN31", "IO91", "PM95", "EN52"]

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
        except:
            pass

        # Simulate activity
        if random.random() < 0.1:
            state.tiles_rx += 1
            state.bytes_rx += random.randint(50, 200)
            state.snr_db = random.uniform(-15, 15)
            state.last_callsign = random.choice(callsigns)
            state.last_grid = random.choice(grids)

            if random.random() < 0.3:
                state.errors_corrected += random.randint(1, 5)

            state.add_log(f"RX tile from {state.last_callsign} ({state.last_grid})")

        draw_screen(stdscr, state)
        time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(description="CWIP Traffic Monitor")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    parser.add_argument("--device", help="Audio device for receive")

    args = parser.parse_args()

    if not HAS_CURSES:
        print("Error: curses not available on this platform")
        print("On Windows, try: pip install windows-curses")
        sys.exit(1)

    if args.demo:
        curses.wrapper(demo_mode)
    else:
        print("Live mode not yet implemented.")
        print("Use --demo for demo mode.")


if __name__ == "__main__":
    main()
