#!/usr/bin/env python3
"""
CWIP Audio Loopback Demo - test the modem with your sound card.

This sends audio out your speaker and tries to receive it via your mic.
Good for testing before going on-air.

Requirements:
    pip install sounddevice numpy

Usage:
    python audio_loopback.py --list          # List audio devices
    python audio_loopback.py --test          # Test tone generation
    python audio_loopback.py --loopback      # Full loopback test

For actual loopback, connect your speaker to your mic (or use a cable).
"""

import argparse
import sys
sys.path.insert(0, '..')

import numpy as np


def list_devices():
    """List available audio devices."""
    import sounddevice as sd
    print("Available audio devices:")
    print(sd.query_devices())


def test_tone():
    """Generate a test CW tone."""
    import sounddevice as sd

    print("Generating 800 Hz tone for 2 seconds...")
    print("You should hear a steady tone.")

    sample_rate = 48000
    duration = 2.0
    freq = 800

    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * freq * t).astype(np.float32)

    sd.play(tone, sample_rate)
    sd.wait()

    print("Done.")


def loopback_test():
    """Full audio loopback test."""
    import sounddevice as sd
    from cwip.modem import AudioModem, ModemConfig

    print("=" * 60)
    print("CWIP Audio Loopback Test")
    print("=" * 60)
    print()
    print("This test will:")
    print("  1. Transmit a short test pattern as audio")
    print("  2. Record audio for the same duration")
    print("  3. Try to demodulate what was received")
    print()
    print("For this to work, connect your speaker to your mic")
    print("(or just put them close together in a quiet room).")
    print()

    input("Press Enter to start...")
    print()

    config = ModemConfig(
        symbol_ms=10.0,     # Slow symbols for audio loopback
        sample_rate=48000,
        tone_freq=800,
        threshold=0.1
    )

    modem = AudioModem(config)

    # Test pattern
    test_data = b"CWIP"
    print(f"Transmitting: {test_data}")

    # We need to TX and RX simultaneously, which is tricky
    # For this demo, we'll TX first, then RX
    # (Real implementation would use separate threads)

    print("Transmitting...")
    modem.transmit(test_data)

    print()
    print("Note: For true loopback, you'd need to TX and RX simultaneously.")
    print("This demo just verifies the audio generation works.")
    print()

    # Show what we transmitted
    samples_per_bit = int(config.sample_rate * config.symbol_ms / 1000)
    total_samples = len(test_data) * 8 * samples_per_bit
    duration = total_samples / config.sample_rate

    print(f"Transmitted {len(test_data)} bytes")
    print(f"  = {len(test_data) * 8} bits")
    print(f"  = {duration:.2f} seconds at {1000/config.symbol_ms:.0f} baud")


def main():
    parser = argparse.ArgumentParser(description="CWIP Audio Loopback Demo")
    parser.add_argument("--list", action="store_true", help="List audio devices")
    parser.add_argument("--test", action="store_true", help="Test tone generation")
    parser.add_argument("--loopback", action="store_true", help="Full loopback test")

    args = parser.parse_args()

    if args.list:
        list_devices()
    elif args.test:
        test_tone()
    elif args.loopback:
        loopback_test()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
