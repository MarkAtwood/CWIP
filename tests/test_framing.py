"""Tests for CWIP tile framing."""

import sys
sys.path.insert(0, '..')

from cwip.framing import Tile, Frame


class TestTile:
    """Test tile serialization."""

    def test_basic_roundtrip(self):
        """Test basic tile encode/decode."""
        tile = Tile(
            msg_type=1,
            stream_id=0x1234,
            seq=42,
            payload=b"Test payload",
            flags=Tile.FLAG_FIRST | Tile.FLAG_LAST
        )

        raw = tile.to_bytes()
        decoded = Tile.from_bytes(raw)

        assert decoded.msg_type == tile.msg_type
        assert decoded.stream_id == tile.stream_id
        assert decoded.seq == tile.seq
        assert decoded.payload == tile.payload

    def test_all_message_types(self):
        """Test all message types."""
        for msg_type in [0, 1, 2, 3, 5, 6]:
            tile = Tile(
                msg_type=msg_type,
                stream_id=0xABCD,
                seq=1,
                payload=b"X"
            )
            raw = tile.to_bytes()
            decoded = Tile.from_bytes(raw)
            assert decoded.msg_type == msg_type

    def test_empty_payload(self):
        """Test tile with empty payload."""
        tile = Tile(
            msg_type=2,  # Ack
            stream_id=0x0001,
            seq=0,
            payload=b""
        )
        raw = tile.to_bytes()
        decoded = Tile.from_bytes(raw)
        assert decoded.payload == b""

    def test_max_payload(self):
        """Test tile with maximum payload."""
        # Max payload depends on mode, but test a large one
        payload = bytes(range(256)) * 4  # 1024 bytes
        tile = Tile(
            msg_type=1,
            stream_id=0xFFFF,
            seq=255,
            payload=payload,
            flags=Tile.FLAG_FIRST | Tile.FLAG_LAST
        )
        raw = tile.to_bytes()
        decoded = Tile.from_bytes(raw)
        assert decoded.payload == payload

    def test_crc_validation(self):
        """Test that corrupted data is rejected."""
        tile = Tile(
            msg_type=1,
            stream_id=0x1234,
            seq=1,
            payload=b"Good data"
        )
        raw = bytearray(tile.to_bytes())

        # Corrupt a byte
        raw[5] ^= 0xFF

        try:
            Tile.from_bytes(bytes(raw))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "CRC" in str(e)

    def test_flags(self):
        """Test flag encoding."""
        tile = Tile(
            msg_type=1,
            stream_id=0x0001,
            seq=1,
            payload=b"X",
            flags=Tile.FLAG_FIRST | Tile.FLAG_LAST | Tile.FLAG_ACK_REQ
        )
        raw = tile.to_bytes()
        decoded = Tile.from_bytes(raw)

        assert decoded.flags & Tile.FLAG_FIRST
        assert decoded.flags & Tile.FLAG_LAST
        assert decoded.flags & Tile.FLAG_ACK_REQ


class TestFrame:
    """Test frame construction."""

    def test_morse_header(self):
        """Test Morse header generation."""
        frame = Frame(
            mycall="K7ABC",
            theircall="W1XYZ",
            tiles=[]
        )

        header = frame.to_morse_header()
        assert "K7ABC" in header
        assert "W1XYZ" in header
        assert "CT DE" in header
        assert "IP 6" in header

    def test_morse_trailer(self):
        """Test Morse trailer generation."""
        frame = Frame(
            mycall="K7ABC",
            theircall="W1XYZ",
            tiles=[]
        )

        trailer = frame.to_morse_trailer()
        assert "SK" in trailer


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
