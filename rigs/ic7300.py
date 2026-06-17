"""Icom IC-7300 rig control via CI-V."""

import serial
from .base import Rig, RigConfig


class IC7300(Rig):
    """
    Icom IC-7300 control via CI-V protocol.

    The IC-7300 appears as a USB serial port AND a USB audio device.
    No external sound card needed.

    Default CI-V address: 0x94
    """

    def __init__(self, config: RigConfig = None):
        super().__init__(config)
        if self.config.address == 0x94:
            pass  # Default for IC-7300
        self.config.baud = 19200  # IC-7300 default

    def connect(self) -> bool:
        try:
            self._serial = serial.Serial(
                self.config.device,
                self.config.baud,
                timeout=1
            )
            return True
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        if self._serial:
            self._serial.close()
            self._serial = None

    def _send_civ(self, cmd: bytes) -> bytes:
        """Send CI-V command and read response."""
        # CI-V frame: FE FE <to> <from> <cmd...> FD
        frame = bytes([0xFE, 0xFE, self.config.address, 0xE0]) + cmd + bytes([0xFD])
        self._serial.write(frame)

        # Read response
        response = b""
        while True:
            b = self._serial.read(1)
            if not b:
                break
            response += b
            if b == b'\xFD':
                break

        return response

    def key_down(self):
        """Send CW key down command."""
        # CI-V: 1C 00 01 = Key on
        self._send_civ(b'\x1C\x00\x01')

    def key_up(self):
        """Send CW key up command."""
        # CI-V: 1C 00 00 = Key off
        self._send_civ(b'\x1C\x00\x00')

    def set_frequency(self, freq_hz: int):
        """Set VFO frequency."""
        # CI-V: 05 = Set frequency (BCD encoded, 5 bytes, 10 digits)
        # Format: 10Hz, 1Hz, 1kHz, 100Hz, 100kHz, 10kHz, 10MHz, 1MHz, 1GHz, 100MHz
        bcd = self._freq_to_bcd(freq_hz)
        self._send_civ(b'\x05' + bcd)

    def set_mode(self, mode: str):
        """Set operating mode."""
        modes = {
            "CW": b'\x03',
            "CW-R": b'\x07',
            "USB": b'\x01',
            "LSB": b'\x00',
            "AM": b'\x02',
            "FM": b'\x05',
        }
        if mode.upper() in modes:
            # CI-V: 06 = Set mode
            self._send_civ(b'\x06' + modes[mode.upper()])

    def _freq_to_bcd(self, freq_hz: int) -> bytes:
        """Convert frequency in Hz to CI-V BCD format."""
        # 5 bytes, each byte is 2 BCD digits, LSB first
        result = bytearray(5)
        for i in range(5):
            digit_low = freq_hz % 10
            freq_hz //= 10
            digit_high = freq_hz % 10
            freq_hz //= 10
            result[i] = (digit_high << 4) | digit_low
        return bytes(result)

    @property
    def audio_device(self) -> str:
        """IC-7300 USB audio device name."""
        # On Linux, typically appears as "USB Audio CODEC"
        # On macOS, appears as "USB Audio CODEC"
        return "USB Audio CODEC"


# Convenience for other Icom rigs with same CI-V protocol
class IC7610(IC7300):
    """Icom IC-7610 - same CI-V protocol, different default address."""

    def __init__(self, config: RigConfig = None):
        super().__init__(config)
        self.config.address = 0x98  # IC-7610 default


class IC705(IC7300):
    """Icom IC-705 - same CI-V protocol."""

    def __init__(self, config: RigConfig = None):
        super().__init__(config)
        self.config.address = 0xA4  # IC-705 default
