"""Tests for Reed-Solomon FEC."""

import sys
sys.path.insert(0, '..')

from cwip.fec import encode_rs, decode_rs, interleave, deinterleave, FEC_MODES


class TestReedSolomon:
    """Test Reed-Solomon encoding/decoding."""

    def test_encode_decode_clean(self):
        """Test encoding and decoding without errors."""
        data = b"Hello, CWIP!"

        for mode in FEC_MODES:
            encoded = encode_rs(data, mode)
            decoded, errors = decode_rs(encoded, mode)

            assert decoded == data
            assert errors == 0

    def test_error_correction(self):
        """Test that errors are corrected."""
        data = b"The quick brown fox"

        for mode in FEC_MODES:
            params = FEC_MODES[mode]
            max_correctable = (params["n"] - params["k"]) // 2

            encoded = encode_rs(data, mode)

            # Corrupt up to max_correctable bytes
            corrupted = bytearray(encoded)
            for i in range(min(5, max_correctable)):
                corrupted[i * 3] ^= 0xFF

            decoded, errors = decode_rs(bytes(corrupted), mode)

            assert decoded == data
            assert errors > 0

    def test_too_many_errors(self):
        """Test that too many errors cause failure."""
        from reedsolo import ReedSolomonError

        data = b"Test data"
        encoded = encode_rs(data, "F2")  # F2 has least parity

        # Corrupt more bytes than can be corrected
        corrupted = bytearray(encoded)
        for i in range(20):  # Way more than F2 can handle
            corrupted[i] ^= 0xFF

        try:
            decode_rs(bytes(corrupted), "F2")
            assert False, "Should have raised ReedSolomonError"
        except ReedSolomonError:
            pass

    def test_modes_exist(self):
        """Verify all FEC modes are defined."""
        assert "F0" in FEC_MODES
        assert "F1" in FEC_MODES
        assert "F2" in FEC_MODES

        # F0 is most robust
        assert FEC_MODES["F0"]["parity"] > FEC_MODES["F1"]["parity"]
        # F2 is least robust
        assert FEC_MODES["F2"]["parity"] < FEC_MODES["F1"]["parity"]


class TestInterleaving:
    """Test byte interleaving."""

    def test_interleave_roundtrip(self):
        """Test interleave/deinterleave roundtrip."""
        blocks = [b"AAAA", b"BBBB", b"CCCC", b"DDDD"]
        depth = 4

        interleaved = interleave(blocks, depth)
        deinterleaved = deinterleave(interleaved, depth, 4)

        assert deinterleaved == blocks

    def test_interleave_single_block(self):
        """Test with single block (no-op)."""
        block = b"Hello"
        interleaved = interleave([block], 1)
        assert interleaved == block


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
