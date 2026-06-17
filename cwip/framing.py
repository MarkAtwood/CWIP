"""CWIP tile framing and packet construction."""

import struct
from dataclasses import dataclass
from typing import Optional
from .fec import encode_rs, decode_rs
from .linecode import encode_8b10b, decode_8b10b


@dataclass
class Tile:
    """A single CWIP tile (the fundamental unit of transmission)."""

    msg_type: int           # 0=Identity, 1=Data, 2=Ack, 3=Nak, 5=Diag, 6=reserved
    stream_id: int          # 16-bit stream identifier
    seq: int                # 8-bit sequence number
    payload: bytes          # Variable length payload
    flags: int = 0          # Header flags byte
    auth: Optional[bytes] = None  # 16-byte HMAC if auth_present

    # Flag bits
    FLAG_CAP = 0x02
    FLAG_DIAG = 0x04
    FLAG_FIRST = 0x08
    FLAG_LAST = 0x10
    FLAG_ACK_REQ = 0x20
    FLAG_AUTH_PRESENT = 0x40

    def to_bytes(self) -> bytes:
        """Serialize tile to bytes (before FEC)."""
        header = struct.pack(">BBHB",
            (self.msg_type << 4) | (self.flags >> 4),
            (self.flags << 4) & 0xF0,
            self.stream_id,
            self.seq
        )
        data = header + self.payload
        crc = _crc32(data)
        data += struct.pack(">I", crc)

        if self.flags & self.FLAG_AUTH_PRESENT and self.auth:
            data += self.auth[:16]

        return data

    @classmethod
    def from_bytes(cls, data: bytes) -> "Tile":
        """Deserialize tile from bytes (after FEC decode)."""
        if len(data) < 9:  # Minimum: 5 header + 4 CRC
            raise ValueError("Tile too short")

        b0, b1, stream_id, seq = struct.unpack(">BBHB", data[:5])
        msg_type = b0 >> 4
        flags = ((b0 & 0x0F) << 4) | (b1 >> 4)

        # Determine payload end based on auth flag
        if flags & cls.FLAG_AUTH_PRESENT:
            payload = data[5:-20]  # Exclude CRC (4) and AUTH (16)
            auth = data[-16:]
            crc_offset = -20
        else:
            payload = data[5:-4]   # Exclude CRC only
            auth = None
            crc_offset = -4

        # Verify CRC
        stored_crc = struct.unpack(">I", data[crc_offset:crc_offset+4])[0]
        computed_crc = _crc32(data[:crc_offset])
        if stored_crc != computed_crc:
            raise ValueError(f"CRC mismatch: {stored_crc:#x} != {computed_crc:#x}")

        return cls(
            msg_type=msg_type,
            stream_id=stream_id,
            seq=seq,
            payload=payload,
            flags=flags,
            auth=auth
        )


@dataclass
class Frame:
    """A complete CWIP frame with human-readable header/trailer."""

    mycall: str             # Sender callsign
    theircall: str          # Recipient callsign
    tiles: list[Tile]       # Tiles in this frame
    ip_version: int = 6     # IP digit (always 6)

    def to_morse_header(self) -> str:
        """Generate human-readable Morse header."""
        return f"CT DE {self.mycall} {self.theircall} KN BT IP {self.ip_version}"

    def to_morse_trailer(self) -> str:
        """Generate human-readable Morse trailer."""
        return "BT SK"


def _crc32(data: bytes) -> int:
    """IEEE 802.3 CRC-32."""
    import binascii
    return binascii.crc32(data) & 0xFFFFFFFF
