#!/usr/bin/env python3
"""
CWIP Loopback Demo - proves the stack works with no hardware.

This encodes a packet, applies FEC, and decodes it, all in memory.
Run this first to verify your installation works.

Usage: python loopback_demo.py
"""

import sys
sys.path.insert(0, '..')

from cwip import Tile, encode_rs, decode_rs
from cwip.ham64 import encode_callsign, decode_callsign, Ham64Address


def main():
    print("=" * 60)
    print("CWIP Loopback Demo")
    print("=" * 60)
    print()

    # Test Ham64 encoding
    print("[1] Ham64 Address Encoding")
    print("-" * 40)

    callsign = "K7ABC"
    addr = Ham64Address.from_callsign(callsign)
    ipv6 = addr.to_ipv6()
    print(f"Callsign: {callsign}")
    print(f"IPv6:     {ipv6}")

    # Round-trip
    decoded = Ham64Address.from_ipv6(str(ipv6))
    print(f"Decoded:  {decoded.decode_identifier()}")
    assert decoded.decode_identifier().rstrip('?') == callsign
    print("✓ Ham64 round-trip successful")
    print()

    # Test tile framing
    print("[2] Tile Framing")
    print("-" * 40)

    tile = Tile(
        msg_type=1,         # Data
        stream_id=0x1234,
        seq=42,
        payload=b"Hello, CWIP!",
        flags=Tile.FLAG_FIRST | Tile.FLAG_LAST
    )

    raw = tile.to_bytes()
    print(f"Tile payload: {tile.payload}")
    print(f"Serialized:   {raw.hex()}")
    print(f"Length:       {len(raw)} bytes")

    # Round-trip
    decoded_tile = Tile.from_bytes(raw)
    assert decoded_tile.payload == tile.payload
    assert decoded_tile.stream_id == tile.stream_id
    print("✓ Tile round-trip successful")
    print()

    # Test FEC
    print("[3] Reed-Solomon FEC")
    print("-" * 40)

    data = b"The quick brown fox jumps over the lazy dog"
    print(f"Original:  {data}")

    encoded = encode_rs(data, "F1")
    print(f"Encoded:   {len(encoded)} bytes (added {len(encoded) - len(data)} parity)")

    # Corrupt some bytes
    corrupted = bytearray(encoded)
    corrupted[5] ^= 0xFF
    corrupted[10] ^= 0xFF
    corrupted[15] ^= 0xFF
    print(f"Corrupted: 3 bytes flipped")

    decoded, errors = decode_rs(bytes(corrupted), "F1")
    print(f"Decoded:   {decoded}")
    print(f"Corrected: {errors} errors")
    assert decoded == data
    print("✓ FEC round-trip successful")
    print()

    # Full stack test
    print("[4] Full Stack Test")
    print("-" * 40)

    # Create an IPv6 packet (just headers for demo)
    ipv6_packet = bytes([
        0x60, 0x00, 0x00, 0x00,  # Version, traffic class, flow label
        0x00, 0x08,              # Payload length
        0x3A,                    # Next header (ICMPv6)
        0x40,                    # Hop limit
    ]) + ipv6.packed + ipv6.packed  # Src + dst (same for demo)
    ipv6_packet += b"PINGDATA"  # Payload

    print(f"IPv6 packet: {len(ipv6_packet)} bytes")

    # Frame it
    tile = Tile(
        msg_type=1,
        stream_id=0xABCD,
        seq=1,
        payload=ipv6_packet,
        flags=Tile.FLAG_FIRST | Tile.FLAG_LAST
    )

    # Encode
    raw = tile.to_bytes()
    fec_encoded = encode_rs(raw, "F1")
    print(f"With FEC:    {len(fec_encoded)} bytes")

    # Simulate transmission (just copy for loopback)
    received = fec_encoded

    # Decode
    fec_decoded, _ = decode_rs(received, "F1")
    rx_tile = Tile.from_bytes(fec_decoded)

    print(f"Received:    {len(rx_tile.payload)} byte payload")
    assert rx_tile.payload == ipv6_packet
    print("✓ Full stack test successful")
    print()

    print("=" * 60)
    print("All tests passed! CWIP stack is working.")
    print("=" * 60)


if __name__ == "__main__":
    main()
