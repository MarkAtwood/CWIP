"""OOK modem for CWIP - audio/GPIO keying and detection."""

import time
from typing import Iterator, Optional
from dataclasses import dataclass


@dataclass
class ModemConfig:
    """Modem timing configuration."""
    symbol_ms: float = 1.0      # Symbol duration in milliseconds (R1 mode)
    sample_rate: int = 48000    # Audio sample rate
    tone_freq: int = 800        # CW tone frequency for audio detection
    threshold: float = 0.5      # Detection threshold (0-1)


class OOKModulator:
    """On-off keying modulator."""

    def __init__(self, config: ModemConfig = None):
        self.config = config or ModemConfig()
        self.symbol_sec = self.config.symbol_ms / 1000.0

    def modulate(self, bits: bytes) -> Iterator[bool]:
        """
        Convert bytes to timed on/off states.

        Yields (state, duration_sec) tuples.
        """
        for byte in bits:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                yield bool(bit)

    def key_sequence(self, bits: bytes, key_func):
        """
        Key a transmitter with the bit sequence.

        key_func(state: bool) -> None: Called to set key state.
        """
        for state in self.modulate(bits):
            key_func(state)
            time.sleep(self.symbol_sec)
        key_func(False)  # Ensure key up at end


class OOKDemodulator:
    """On-off keying demodulator using Goertzel algorithm."""

    def __init__(self, config: ModemConfig = None):
        self.config = config or ModemConfig()
        self.samples_per_symbol = int(
            self.config.sample_rate * self.config.symbol_ms / 1000
        )

    def goertzel(self, samples, target_freq: int) -> float:
        """
        Single-frequency energy detector.

        Returns normalized energy at target frequency.
        """
        import math

        n = len(samples)
        k = int(0.5 + n * target_freq / self.config.sample_rate)
        w = 2 * math.pi * k / n
        coeff = 2 * math.cos(w)

        s0 = s1 = s2 = 0.0
        for sample in samples:
            s0 = sample + coeff * s1 - s2
            s2, s1 = s1, s0

        power = s1*s1 + s2*s2 - coeff*s1*s2
        return power / (n * n)  # Normalize

    def demodulate_chunk(self, samples) -> bool:
        """
        Demodulate one symbol period of audio samples.

        Returns True if tone detected, False otherwise.
        """
        energy = self.goertzel(samples, self.config.tone_freq)
        return energy > self.config.threshold

    def demodulate_stream(self, audio_stream) -> Iterator[int]:
        """
        Demodulate continuous audio stream to bits.

        audio_stream: Iterator yielding sample chunks.
        Yields: bytes as they're decoded.
        """
        bit_buffer = []

        for chunk in audio_stream:
            bit = 1 if self.demodulate_chunk(chunk) else 0
            bit_buffer.append(bit)

            if len(bit_buffer) == 8:
                byte = sum(b << (7-i) for i, b in enumerate(bit_buffer))
                yield byte
                bit_buffer = []


class AudioModem:
    """Complete audio modem using sounddevice."""

    def __init__(self, config: ModemConfig = None):
        self.config = config or ModemConfig()
        self.modulator = OOKModulator(config)
        self.demodulator = OOKDemodulator(config)

    def transmit(self, data: bytes, device: Optional[int] = None):
        """Transmit data as audio tones."""
        import numpy as np
        import sounddevice as sd

        # Generate tone for each bit
        samples_per_bit = self.demodulator.samples_per_symbol
        t = np.linspace(0, self.config.symbol_ms/1000, samples_per_bit, False)
        tone = np.sin(2 * np.pi * self.config.tone_freq * t).astype(np.float32)
        silence = np.zeros(samples_per_bit, dtype=np.float32)

        # Build waveform
        waveform = []
        for state in self.modulator.modulate(data):
            waveform.extend(tone if state else silence)

        # Play
        sd.play(np.array(waveform), self.config.sample_rate, device=device)
        sd.wait()

    def receive(self, duration_sec: float, device: Optional[int] = None) -> bytes:
        """Receive and demodulate audio for specified duration."""
        import numpy as np
        import sounddevice as sd

        samples = int(duration_sec * self.config.sample_rate)
        audio = sd.rec(samples, samplerate=self.config.sample_rate,
                       channels=1, dtype=np.float32, device=device)
        sd.wait()

        # Demodulate
        result = bytearray()
        chunk_size = self.demodulator.samples_per_symbol

        for i in range(0, len(audio) - chunk_size, chunk_size):
            chunk = audio[i:i+chunk_size, 0]
            for byte in self.demodulator.demodulate_stream([chunk]):
                result.append(byte)

        return bytes(result)
