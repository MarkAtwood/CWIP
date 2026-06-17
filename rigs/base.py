"""Base rig interface for CWIP."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class RigConfig:
    """Rig connection configuration."""
    device: str = "/dev/ttyUSB0"    # Serial port
    baud: int = 19200               # Baud rate
    address: int = 0x94             # CI-V address (for Icom)


class Rig(ABC):
    """Abstract base class for rig control."""

    def __init__(self, config: RigConfig = None):
        self.config = config or RigConfig()
        self._serial = None

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the rig. Returns True on success."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the rig."""
        pass

    @abstractmethod
    def key_down(self):
        """Key the transmitter (start sending carrier)."""
        pass

    @abstractmethod
    def key_up(self):
        """Unkey the transmitter."""
        pass

    @abstractmethod
    def set_frequency(self, freq_hz: int):
        """Set operating frequency in Hz."""
        pass

    @abstractmethod
    def set_mode(self, mode: str):
        """Set operating mode (CW, USB, etc.)."""
        pass

    def key(self, state: bool):
        """Set key state."""
        if state:
            self.key_down()
        else:
            self.key_up()

    @property
    def audio_device(self) -> Optional[str]:
        """
        Return audio device name/ID for this rig's USB audio.
        Override in subclasses that have USB audio.
        """
        return None
