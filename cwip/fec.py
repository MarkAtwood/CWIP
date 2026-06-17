"""Reed-Solomon forward error correction for CWIP."""

from typing import Tuple
from reedsolo import RSCodec, ReedSolomonError

# FEC modes per spec
FEC_MODES = {
    "F0": {"n": 255, "k": 191, "parity": 64, "depth": 16},  # Robust
    "F1": {"n": 255, "k": 223, "parity": 32, "depth": 8},   # Default
    "F2": {"n": 255, "k": 239, "parity": 16, "depth": 4},   # Clean channel
}

DEFAULT_MODE = "F1"


def get_codec(mode: str = DEFAULT_MODE) -> RSCodec:
    """Get RS codec for specified mode."""
    params = FEC_MODES[mode]
    nsym = params["n"] - params["k"]  # Number of parity symbols
    return RSCodec(nsym)


def encode_rs(data: bytes, mode: str = DEFAULT_MODE) -> bytes:
    """
    Encode data with Reed-Solomon FEC.

    Returns data + parity bytes.
    """
    codec = get_codec(mode)
    return bytes(codec.encode(data))


def decode_rs(data: bytes, mode: str = DEFAULT_MODE) -> Tuple[bytes, int]:
    """
    Decode Reed-Solomon encoded data.

    Returns (decoded_data, errors_corrected).
    Raises ReedSolomonError if uncorrectable.
    """
    codec = get_codec(mode)
    decoded, _, errata_pos = codec.decode(data)
    return bytes(decoded), len(errata_pos)


def interleave(blocks: list[bytes], depth: int) -> bytes:
    """
    Interleave multiple RS codewords byte-wise round-robin.

    Per spec: byte i goes to position (i mod D) * ceil(total/D) + floor(i/D)
    """
    if not blocks:
        return b""

    # Flatten all blocks
    flat = b"".join(blocks)
    total = len(flat)

    # Interleave
    out = bytearray(total)
    for i, byte in enumerate(flat):
        pos = (i % depth) * ((total + depth - 1) // depth) + (i // depth)
        if pos < total:
            out[pos] = byte

    return bytes(out)


def deinterleave(data: bytes, depth: int, block_size: int) -> list[bytes]:
    """
    Reverse interleaving to recover RS codewords.
    """
    total = len(data)
    num_blocks = (total + block_size - 1) // block_size

    # De-interleave
    flat = bytearray(total)
    for i in range(total):
        pos = (i % depth) * ((total + depth - 1) // depth) + (i // depth)
        if pos < total:
            flat[i] = data[pos]

    # Split into blocks
    blocks = []
    for i in range(num_blocks):
        start = i * block_size
        end = min(start + block_size, total)
        blocks.append(bytes(flat[start:end]))

    return blocks
