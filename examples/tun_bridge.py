#!/usr/bin/env python3
"""
CWIP TUN Bridge - connects IPv6 to CWIP radio.

This creates a TUN device and bridges IPv6 packets to/from the radio.
Requires root/sudo to create the TUN device.

Usage:
    sudo python tun_bridge.py --rig ic7300 --device /dev/ttyUSB0 --call K7ABC

Requirements:
    pip install python-pytun

On Linux, you may need to:
    sudo modprobe tun
"""

import argparse
import sys
sys.path.insert(0, '..')


def create_tun(name: str = "cwip0"):
    """Create a TUN device for IPv6."""
    try:
        import pytun
    except ImportError:
        print("Error: python-pytun required. Install with: pip install python-pytun")
        sys.exit(1)

    tun = pytun.TunTapDevice(name=name, flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
    tun.addr = "fd00:cwip::1"  # ULA address
    tun.netmask = "ffff:ffff:ffff:ffff::"
    tun.mtu = 256  # Small MTU for CWIP
    tun.up()

    return tun


def main():
    parser = argparse.ArgumentParser(description="CWIP TUN Bridge")
    parser.add_argument("--rig", default="ic7300", help="Rig type (ic7300, ft991a, hamlib)")
    parser.add_argument("--device", default="/dev/ttyUSB0", help="Serial device")
    parser.add_argument("--call", required=True, help="Your callsign")
    parser.add_argument("--freq", type=int, default=7055000, help="Frequency in Hz")
    parser.add_argument("--tun", default="cwip0", help="TUN device name")

    args = parser.parse_args()

    print("=" * 60)
    print("CWIP TUN Bridge")
    print("=" * 60)
    print()
    print(f"Callsign:  {args.call}")
    print(f"Rig:       {args.rig}")
    print(f"Device:    {args.device}")
    print(f"Frequency: {args.freq / 1e6:.3f} MHz")
    print(f"TUN:       {args.tun}")
    print()

    # This is a skeleton - full implementation would:
    # 1. Create TUN device
    # 2. Connect to rig
    # 3. Set frequency and mode
    # 4. Loop:
    #    - Read packets from TUN
    #    - Frame as CWIP tiles
    #    - Transmit via rig
    #    - Receive from rig
    #    - Decode tiles
    #    - Write packets to TUN

    print("This is a skeleton implementation.")
    print("Full bridge requires completing the TX/RX loop.")
    print()
    print("For now, use loopback_demo.py to test the stack,")
    print("and audio_loopback.py to test the modem.")


if __name__ == "__main__":
    main()
