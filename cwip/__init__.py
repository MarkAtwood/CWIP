"""CWIP: IPv6 over Continuous Wave"""

from .framing import Tile, Frame
from .fec import encode_rs, decode_rs
from .linecode import encode_8b10b, decode_8b10b
from .ham64 import encode_callsign, decode_callsign, Ham64Address

__version__ = "0.1.0"
__all__ = [
    "Tile", "Frame",
    "encode_rs", "decode_rs",
    "encode_8b10b", "decode_8b10b",
    "encode_callsign", "decode_callsign", "Ham64Address",
]
