# CWIP: IPv6 over Continuous Wave

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CWIP** carries IPv6 packets over Morse code (CW keying), because why not.

The design keeps transmissions human-recognizable at the edges (Morse prosigns)
and machine-efficient in the middle (Reed-Solomon FEC, 8b/10b line coding).
Operators can supervise bursts via traditional Morse, while the payload
achieves ~1 kbps on a good day.

## Quick Start

```bash
# Install dependencies
pip install reedsolo numpy sounddevice

# Test the stack (no hardware needed)
python examples/loopback_demo.py

# Test audio (needs speakers/mic)
python examples/audio_loopback.py --test

# Run the monitor (pretty UI)
python tools/cwip_monitor.py --demo
```

## What's Here

```
cwip/
├── cwip/              # Core library
│   ├── framing.py     # Tile/frame construction
│   ├── fec.py         # Reed-Solomon FEC
│   ├── linecode.py    # 8b/10b, 64b/66b
│   ├── ham64.py       # Callsign→IPv6 encoding
│   └── modem.py       # OOK modulation/demodulation
├── rigs/              # Radio control
│   ├── ic7300.py      # Icom IC-7300 (CI-V)
│   └── hamlib.py      # Generic via Hamlib
├── examples/
│   ├── loopback_demo.py   # Test stack in memory
│   ├── audio_loopback.py  # Test with sound card
│   └── tun_bridge.py      # IPv6 ↔ radio bridge
├── tools/
│   └── cwip_monitor.py    # ncurses traffic display
└── tests/             # pytest tests
```

## Supported Radios

Any CW-capable radio works. Direct support for:

| Radio | Interface | Notes |
|-------|-----------|-------|
| Icom IC-7300 | USB (CI-V + audio) | One cable, no sound card |
| Icom IC-7610 | USB | Same as IC-7300 |
| Icom IC-705 | USB/Bluetooth | Portable |
| Yaesu FT-991A | Via Hamlib | USB CAT |
| Kenwood TS-890S | Via Hamlib | USB CAT |
| Any other | Via Hamlib | 200+ radios supported |

## Specifications

- [draft-atwood-cwip-00](https://gist.github.com/MarkAtwood/a3ac2b631dfc267dd3d271bd0f0c2343) - CWIP protocol
- [draft-atwood-ham64-00](https://gist.github.com/MarkAtwood/fba0d655efc76a6c8670a30fe09024b6) - Ham64 addressing

## Architecture

```
┌─────────────┐
│   IPv6      │ ← TUN device
├─────────────┤
│   CWIP      │ ← Tile framing, FEC
├─────────────┤
│  8b/10b     │ ← Line coding
├─────────────┤
│    OOK      │ ← On-off keying
├─────────────┤
│   Radio     │ ← CW mode, any band
└─────────────┘
```

## Contributing

1. Run the loopback demo first
2. Run the tests: `pytest tests/`
3. Pick an issue labeled "good first issue"

Areas that need work:
- [ ] Full 8b/10b lookup tables
- [ ] 64b/66b scrambler
- [ ] Live audio receive
- [ ] TUN bridge completion
- [ ] More rig drivers

## License

MIT

## FAQ

**Q: Why?**
A: Because CW is the oldest digital mode and IPv6 is... not. The juxtaposition is amusing.

**Q: What's the throughput?**
A: About 1 kbps in R1 mode. Enough for a ping.

**Q: Can I actually use this?**
A: On amateur bands where you're licensed, yes. Mind your identification requirements.

**Q: Is this an April 1 RFC?**
A: Perhaps.
