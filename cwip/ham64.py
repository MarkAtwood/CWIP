"""Ham64: Human identifier encoding for IPv6 addresses."""

from dataclasses import dataclass
from typing import Optional
import ipaddress

# Ham64 symbol table (6-bit values)
SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ .-/+=$@#&()*!?'\"<>\\^~;:[]{|}%_"
SYMBOL_TO_VALUE = {c: i for i, c in enumerate(SYMBOLS)}
VALUE_TO_SYMBOL = {i: c for i, c in enumerate(SYMBOLS)}

END_SYMBOL = 63  # '?' marks end of identifier
AUTH_SYMBOL = 62  # '%' marks AUTH prefix

# Identifier types
TYPE_CALLSIGN = 0
TYPE_AIRCRAFT = 1
TYPE_AIRPORT = 2
TYPE_VEHICLE = 3
TYPE_BOAT_HIN = 4
TYPE_MAIDENHEAD = 5
TYPE_GENERIC = 6
TYPE_POSTAL = 7
TYPE_TELEPHONE = 8


@dataclass
class Ham64Address:
    """A Ham64-encoded IPv6 address."""

    prefix: bytes           # /16 prefix (2 bytes)
    version: int            # VERS field (3 bits)
    id_type: int            # TYPE field (4 bits)
    a_kind: int             # A-KIND field (2 bits)
    symbols: list[int]      # Symbol values (up to 17)

    @classmethod
    def from_callsign(cls, callsign: str, prefix: bytes = b'\x20\x01') -> "Ham64Address":
        """Create Ham64 address from amateur radio callsign."""
        symbols = encode_identifier(callsign.upper())
        return cls(
            prefix=prefix,
            version=1,
            id_type=TYPE_CALLSIGN,
            a_kind=0,
            symbols=symbols
        )

    @classmethod
    def from_ipv6(cls, addr: str) -> "Ham64Address":
        """Parse Ham64 address from IPv6 string."""
        ip = ipaddress.IPv6Address(addr)
        packed = ip.packed

        prefix = packed[:2]
        payload = packed[2:]

        # Parse header (first 9 bits)
        b0, b1 = payload[0], payload[1]
        version = (b0 >> 5) & 0x07
        id_type = (b0 >> 1) & 0x0F
        a_kind = ((b0 & 0x01) << 1) | ((b1 >> 7) & 0x01)

        # Extract symbols (6 bits each, starting at bit 9)
        symbols = []
        bit_offset = 9
        while bit_offset + 6 <= 112:
            byte_idx = bit_offset // 8
            bit_idx = bit_offset % 8

            if bit_idx <= 2:
                val = (payload[byte_idx] >> (2 - bit_idx)) & 0x3F
            else:
                val = ((payload[byte_idx] << (bit_idx - 2)) & 0x3F)
                if byte_idx + 1 < len(payload):
                    val |= (payload[byte_idx + 1] >> (10 - bit_idx)) & ((1 << (bit_idx - 2)) - 1)

            symbols.append(val)
            bit_offset += 6

            if val == END_SYMBOL:
                break

        return cls(prefix=prefix, version=version, id_type=id_type, a_kind=a_kind, symbols=symbols)

    def to_ipv6(self) -> ipaddress.IPv6Address:
        """Convert to IPv6 address."""
        # Build 112-bit payload
        payload = bytearray(14)

        # Header: VERS (3) + TYPE (4) + A-KIND (2) = 9 bits
        payload[0] = ((self.version & 0x07) << 5) | ((self.id_type & 0x0F) << 1) | ((self.a_kind >> 1) & 0x01)
        payload[1] = (self.a_kind & 0x01) << 7

        # Pack symbols (6 bits each)
        bit_offset = 9
        for sym in self.symbols:
            byte_idx = bit_offset // 8
            bit_idx = bit_offset % 8

            if bit_idx <= 2:
                payload[byte_idx] |= (sym & 0x3F) << (2 - bit_idx)
            else:
                payload[byte_idx] |= (sym >> (bit_idx - 2)) & 0xFF
                if byte_idx + 1 < len(payload):
                    payload[byte_idx + 1] |= (sym << (10 - bit_idx)) & 0xFF

            bit_offset += 6

        # Combine prefix + payload
        full = self.prefix + bytes(payload)
        return ipaddress.IPv6Address(full)

    def decode_identifier(self) -> str:
        """Decode symbols back to human-readable identifier."""
        chars = []
        for sym in self.symbols:
            if sym == END_SYMBOL:
                break
            if sym < len(VALUE_TO_SYMBOL):
                chars.append(VALUE_TO_SYMBOL[sym])
        return ''.join(chars)


def encode_identifier(text: str) -> list[int]:
    """Encode text string to Ham64 symbols."""
    symbols = []
    for char in text.upper():
        if char in SYMBOL_TO_VALUE:
            symbols.append(SYMBOL_TO_VALUE[char])

    # Pad with END if room
    if len(symbols) < 17:
        symbols.append(END_SYMBOL)

    return symbols[:17]  # Max 17 symbols


def encode_callsign(callsign: str) -> ipaddress.IPv6Address:
    """Convenience function: callsign -> IPv6 address."""
    addr = Ham64Address.from_callsign(callsign)
    return addr.to_ipv6()


def decode_callsign(ipv6: str) -> str:
    """Convenience function: IPv6 address -> callsign."""
    addr = Ham64Address.from_ipv6(ipv6)
    return addr.decode_identifier()
