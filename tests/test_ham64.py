"""Test vectors from the Ham64 specification."""

import sys
sys.path.insert(0, '..')

from cwip.ham64 import Ham64Address, encode_identifier, SYMBOL_TO_VALUE


class TestHam64Vectors:
    """Test vectors from draft-atwood-ham64-00."""

    def test_callsign_k7abc(self):
        """Test Vector 1: K7ABC/TT"""
        addr = Ham64Address(
            prefix=b'\x20\x01',  # 2001:db8:6464 prefix
            version=1,
            id_type=0,  # Callsign
            a_kind=0,
            symbols=[20, 7, 10, 11, 12, 39, 29, 29, 63]  # K7ABC/TT + END
        )

        # Verify symbols
        assert addr.decode_identifier().rstrip('?') == "K7ABC/TT"

    def test_aircraft_n9748c(self):
        """Test Vector 2: N9748C (FAA reserved fictional)"""
        # N=23, 9=9, 7=7, 4=4, 8=8, C=12, END=63
        expected_symbols = [23, 9, 7, 4, 8, 12, 63]

        text = "N9748C"
        symbols = encode_identifier(text)

        assert symbols[:len(expected_symbols)] == expected_symbols

    def test_airport_ksea(self):
        """Test Vector 3: KSEA (ICAO)"""
        # K=20, S=28, E=14, A=10, END=63
        expected_symbols = [20, 28, 14, 10, 63]

        text = "KSEA"
        symbols = encode_identifier(text)

        assert symbols[:len(expected_symbols)] == expected_symbols

    def test_symbol_table(self):
        """Verify Ham64 symbol table."""
        # Digits
        for i in range(10):
            assert SYMBOL_TO_VALUE[str(i)] == i

        # Letters
        for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            assert SYMBOL_TO_VALUE[c] == 10 + i

        # Special
        assert SYMBOL_TO_VALUE[' '] == 36
        assert SYMBOL_TO_VALUE['.'] == 37
        assert SYMBOL_TO_VALUE['-'] == 38
        assert SYMBOL_TO_VALUE['/'] == 39

    def test_roundtrip(self):
        """Test encode/decode roundtrip for various identifiers."""
        test_cases = [
            "K7ABC",
            "W1XYZ/P",
            "VE3DEF",
            "N9748C",
            "G-XXXX",
            "KSEA",
            "CN87UM",
        ]

        for text in test_cases:
            addr = Ham64Address.from_callsign(text)
            ipv6 = addr.to_ipv6()
            decoded = Ham64Address.from_ipv6(str(ipv6))
            result = decoded.decode_identifier().rstrip('?')
            assert result == text.upper(), f"Failed for {text}: got {result}"


class TestHam64Encoding:
    """Test Ham64 bit-level encoding."""

    def test_header_bits(self):
        """Test header field encoding."""
        addr = Ham64Address(
            prefix=b'\x20\x01',
            version=1,      # 001
            id_type=5,      # 0101 (Maidenhead)
            a_kind=0,       # 00
            symbols=[12, 23, 8, 7]  # CN87
        )

        ipv6 = addr.to_ipv6()
        packed = ipv6.packed

        # Check header bits
        b0 = packed[2]  # First payload byte
        version = (b0 >> 5) & 0x07
        id_type = (b0 >> 1) & 0x0F

        assert version == 1
        assert id_type == 5


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
