"""Generic rig control via Hamlib."""

import subprocess
from .base import Rig, RigConfig


class HamlibRig(Rig):
    """
    Generic rig control using Hamlib's rigctl command.

    Requires hamlib to be installed: apt install libhamlib-utils

    This provides support for 200+ radios via a common interface.
    See: https://hamlib.github.io/
    """

    def __init__(self, config: RigConfig = None, model: int = 1):
        """
        Initialize Hamlib rig.

        model: Hamlib rig model number. Run 'rigctl -l' to list.
               Common models:
               - 1 = Dummy (for testing)
               - 3073 = Icom IC-7300
               - 3085 = Icom IC-7610
               - 1035 = Yaesu FT-991A
               - 2028 = Kenwood TS-890S
        """
        super().__init__(config)
        self.model = model
        self._rigctld = None

    def connect(self) -> bool:
        """Start rigctld daemon."""
        try:
            self._rigctld = subprocess.Popen([
                "rigctld",
                "-m", str(self.model),
                "-r", self.config.device,
                "-s", str(self.config.baud),
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            print("Error: rigctld not found. Install hamlib: apt install libhamlib-utils")
            return False

    def disconnect(self):
        if self._rigctld:
            self._rigctld.terminate()
            self._rigctld.wait()
            self._rigctld = None

    def _rigctl(self, *args) -> str:
        """Run rigctl command."""
        result = subprocess.run(
            ["rigctl", "-m", "2"] + list(args),  # Model 2 = NET rigctl
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def key_down(self):
        """Key transmitter via PTT."""
        self._rigctl("T", "1")

    def key_up(self):
        """Unkey transmitter."""
        self._rigctl("T", "0")

    def set_frequency(self, freq_hz: int):
        """Set frequency."""
        self._rigctl("F", str(freq_hz))

    def set_mode(self, mode: str):
        """Set mode."""
        self._rigctl("M", mode.upper(), "0")


# Model numbers for common rigs
HAMLIB_MODELS = {
    "dummy": 1,
    "ic7300": 3073,
    "ic7610": 3085,
    "ic705": 3086,
    "ft991a": 1035,
    "ft891": 1036,
    "ts890s": 2028,
    "ts590sg": 2026,
}


def create_rig(name: str, device: str = "/dev/ttyUSB0") -> HamlibRig:
    """Create a Hamlib rig by name."""
    model = HAMLIB_MODELS.get(name.lower(), 1)
    config = RigConfig(device=device)
    return HamlibRig(config, model=model)
