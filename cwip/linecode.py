"""8b/10b and 64b/66b line coding for CWIP."""

# 8b/10b encoding tables (subset - full table is 256 entries)
# Format: {byte: (RD-, RD+)} where RD is running disparity
# K28.5 comma character for sync

K28_5_RDN = 0b0011111010  # K28.5 with RD-
K28_5_RDP = 0b1100000101  # K28.5 with RD+

# Simplified 8b/10b - in practice you'd use a full lookup table
# This is a placeholder implementation


def encode_8b10b(data: bytes, insert_commas: bool = True) -> list[int]:
    """
    Encode bytes to 8b/10b symbols.

    Returns list of 10-bit values.
    In real implementation, use full IBM 8b/10b tables.
    """
    symbols = []
    rd = -1  # Running disparity, start negative

    if insert_commas:
        # Insert K28.5 comma at start for sync
        symbols.append(K28_5_RDN if rd < 0 else K28_5_RDP)
        rd = -rd  # Comma flips disparity

    for byte in data:
        # Placeholder: real implementation needs full 5b/6b + 3b/4b tables
        # For now, just pack with minimal disparity tracking
        symbol = _encode_byte_8b10b(byte, rd)
        symbols.append(symbol)
        rd = _update_disparity(symbol, rd)

    return symbols


def decode_8b10b(symbols: list[int]) -> bytes:
    """
    Decode 8b/10b symbols to bytes.

    Strips comma characters, returns data bytes.
    """
    data = []
    for symbol in symbols:
        # Skip comma characters
        if symbol in (K28_5_RDN, K28_5_RDP):
            continue
        byte = _decode_symbol_8b10b(symbol)
        if byte is not None:
            data.append(byte)
    return bytes(data)


def _encode_byte_8b10b(byte: int, rd: int) -> int:
    """Encode single byte to 10-bit symbol. Placeholder implementation."""
    # Real implementation: split into 5-bit and 3-bit, look up in tables
    # This is a stub that just packs the byte with padding
    # DO NOT USE IN PRODUCTION - need full 8b/10b tables
    return (byte << 2) | (0b01 if rd < 0 else 0b10)


def _decode_symbol_8b10b(symbol: int) -> int:
    """Decode 10-bit symbol to byte. Placeholder implementation."""
    # Real implementation: reverse lookup in tables
    return (symbol >> 2) & 0xFF


def _update_disparity(symbol: int, rd: int) -> int:
    """Update running disparity after symbol."""
    ones = bin(symbol).count('1')
    if ones > 5:
        return 1
    elif ones < 5:
        return -1
    return rd


# 64b/66b is simpler - just add 2-bit sync header
SYNC_DATA = 0b01
SYNC_CTRL = 0b10


def encode_64b66b(data: bytes) -> bytes:
    """
    Encode data with 64b/66b framing.

    Adds 01 sync header to each 8-byte block.
    Uses x^58 + x^39 + 1 scrambler.
    """
    output = bytearray()

    for i in range(0, len(data), 8):
        block = data[i:i+8].ljust(8, b'\x00')
        # Add sync header (01 for data)
        # In real impl, scramble the payload
        output.append(SYNC_DATA)
        output.extend(block)

    return bytes(output)


def decode_64b66b(data: bytes) -> bytes:
    """
    Decode 64b/66b framed data.

    Strips sync headers, descrambles.
    """
    output = bytearray()

    i = 0
    while i < len(data):
        if i + 9 > len(data):
            break
        sync = data[i]
        if sync not in (SYNC_DATA, SYNC_CTRL):
            i += 1  # Resync
            continue
        block = data[i+1:i+9]
        output.extend(block)
        i += 9

    return bytes(output)
