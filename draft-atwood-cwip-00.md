---
title: "CWIP: Human-Readable, Machine-Decodable IPv6 over Continuous Wave (and Flashing Lights)"
abbrev: "CWIP"
docname: draft-atwood-cwip-00
category: exp
ipr: trust200902
area: General
workgroup: Independent
keyword: Internet-Draft

stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

author:
  - ins: M. Atwood
    name: Mark Atwood
    email: mark@reviewcommit.com

normative:
  RFC2104:
  RFC2119:
  RFC5869:
  RFC6234:
  RFC8174:
  RFC8200:
  RFC6282:

informative:
  RFC8724:
  IEEE8023:
    title: "IEEE Std 802.3-2022, Clause 3 (CRC-32), Clauses 36/38 (8B/10B), Clause 49 (64B/66B)"
    author:
      org: IEEE
    date: 2022
    seriesinfo:
      IEEE: Std 802.3-2022
  IEEE802154:
    title: "IEEE Standard for Low-Rate Wireless Networks"
    author:
      org: IEEE
    date: 2020
    seriesinfo:
      IEEE: Std 802.15.4-2020
  CCSDS1301:
    title: "TM Synchronization and Channel Coding"
    author:
      org: Consultative Committee for Space Data Systems
    date: 2021-04
    seriesinfo:
      CCSDS: 131.0-B-4
    target: https://public.ccsds.org/Pubs/131x0b4.pdf
  CCSDS211:
    title: "Proximity-1 Space Link Protocol—Data Link Layer"
    author:
      org: Consultative Committee for Space Data Systems
    date: 2021-06
    seriesinfo:
      CCSDS: 211.0-B-6
  ITUO151:
    title: "Error Performance Measuring Equipment Operating at the Primary Rate and Above"
    author:
      org: International Telecommunication Union
    date: 1992
    seriesinfo:
      ITU-T: Recommendation O.151
  ICDGPS200:
    title: "Navstar GPS Space Segment/Navigation User Interfaces"
    author:
      org: GPS Directorate
    date: 2022-05
    seriesinfo:
      ICD: GPS-200 Rev N
  IARU:
    title: "IARU Region 1 VHF Managers Handbook: Maidenhead Locator System"
    author:
      org: International Amateur Radio Union
    target: https://www.iaru-r1.org/
  ITURM1545:
    title: "Recommendation ITU-R M.1545: Q Codes"
    author:
      org: International Telecommunication Union
    date: 2019
    seriesinfo:
      ITU-R: M.1545-1
  WSJTX:
    title: "WSJT-X User Guide"
    author:
      name: Joe Taylor
      ins: J. Taylor, K1JT
    date: 2023
    target: https://wsjt.sourceforge.io/wsjtx-doc/wsjtx-main-2.6.1.html
  LORA:
    title: "LoRaWAN Specification"
    author:
      org: LoRa Alliance
    date: 2020-10
    seriesinfo:
      Version: 1.0.4

--- abstract

This memo specifies a tile-framed, polarity-agnostic method to
carry IPv6 over continuous-wave keying and optical flashes. A human
can recognize and supervise transmissions via Morse, and a machine
can decode self-clocking, FEC-protected tiles that support
late-tune acquisition. It is suitable for radio and line-of-sight
optical links, works even in hostile channels, and is deliberately
amusing.

--- middle

# Introduction

CWIP carries IPv6 packets over continuous-wave (CW) keying, whether
radio frequency (RF) or optical flashes, while keeping the
transmission human-recognizable at the edges and machine-efficient
in the middle. The design uses Morse prosigns and characters so
operators can supervise and identify bursts, then switches to
machine-speed tiles with self-clocking line codes, forward error
correction (FEC), and interleaving. Each tile is independently
decodable, allowing late-tune receivers to lock mid-burst. The
protocol is polarity-agnostic: a receiver can decode even if the
entire signal is inverted.

This specification targets experimental and amateur use where
encryption is prohibited.

# Conventions and Terminology

{::boilerplate bcp14-tagged}

Human speed:
: Ordinary Morse timing (~20-25 WPM) for prosigns and callsigns.
  Receivers MUST accept 10-40 WPM (unit element 30-120 ms) for
  validation; transmitters SHOULD use 18-30 WPM.

Machine speed:
: Fixed unit T milliseconds for data symbols.

White/Black:
: The two polarities. On RF: 0/180 degree phase. On optical:
  bright/dim (or on/off).

Symbol:
: One of four marks: short-white, short-black, long-white, long-black.

Dibit:
: Two payload bits mapped onto one symbol.

Tile:
: An independently decodable machine-speed block with preamble,
  sync, header, payload, CRC, AUTH, and FEC parity.

Burst:
: A sequence of one or more tiles with human prosigns before and/or after.

Stream ID:
: A 32-bit value naming an address context for compression.

# Problem Statement

IP over HF has existed for decades (packet radio, PACTOR, Winlink).
CW-over-IP is trivial: send Morse as audio through an IP tunnel.
This specification addresses the inverse: IP over CW with
human-legible framing.

The challenge is reconciling two requirements. First, amateur radio
requires human-readable identification and prohibits encryption.
Second, modern data protocols demand robust transport with error
correction, timing recovery, and mid-stream join capability.

CWIP solves this by layering. The human layer uses Morse prosigns
(e.g., "IP" as start marker) and digits to announce message types.
The machine layer uses four-symbol keying to carry dibits, applies
self-clocking line codes for timing recovery and DC balance, and
wraps everything in independently decodable tiles with Reed-Solomon
FEC. A receiver can tune in late, acquire on any tile, and decode
without hearing the human preamble.

# Protocol Overview

## What Operators Hear and See

A CWIP burst begins with a human-speed Morse unit prosign "IP"
(letters I and P sent as a single unit with no inter-letter spacing:
di-dit-dah-dah-dit). This is followed by a single Morse digit (0-6)
announcing the message type:

| Digit | Meaning |
|-------|---------|
| 0 | Identity advertisement |
| 1 | ACK |
| 2 | NAK |
| 3 | DIAG (telemetry) |
| 4 | Reserved |
| 5 | CAP (capabilities) |
| 6 | Data (IPv6 packet) |

After the digit, transmission switches to machine speed: rapid
short and long marks in two polarities. Each tile has preamble,
sync, header, payload, CRC, AUTH, and FEC parity. The burst ends
with human-speed "BT" as tail prosign.

Periodically, operators SHOULD send callsigns: "IP DE \<callsign\> BT".

## Tiles and Late-Join

A tile is the fundamental unit. Each tile is independently
decodable with its own preamble, sync, header (25 bytes), payload,
CRC32, AUTH, and FEC parity. A receiver can tune in mid-burst, lock
onto any tile's preamble, and decode without prior context.

Preamble acquisition: The preamble consists of 16+ alternating
long-white and long-black symbols (each 3T duration). The preamble
MUST begin with long-white. A late-join receiver monitors for this
alternating pattern, detects it for 8-10 cycles, then awaits the
sync pattern marking header start.

Multiple tiles with the same pkt_id are reassembled into one IPv6
packet. The header includes tile_index and tile_count.

## Operating Profiles

Symbol unit T (machine speed):

| Mode | T | Throughput |
|------|---|------------|
| R0 (robust) | 2.0 ms | ~350-600 bps net |
| R1 (default) | 1.0 ms | ~600-1000 bps net |
| R2 (fast) | 0.5 ms | ~1.2-2 kbps net |

Line coding:

- Default: 64b/66b with scrambler (x^58 + x^39 + 1)
- Optional: 8b/10b with comma patterns (K28.5)

FEC modes (Reed-Solomon {{CCSDS1301}}):

| Mode | Parameters | Interleave Depth |
|------|------------|------------------|
| F0 (robust) | RS(255,191) | 16 |
| F1 (default) | RS(255,223) | 8 |
| F2 (clean) | RS(255,239) | 4 |

# Detailed Framing (Normative)

## Physical Symbol Mapping

Let T be the machine symbol unit (per R-mode).

- Short mark: Keyed "on" for 1T.
- Long mark: Keyed "on" for 3T.
- Inter-symbol gap: 1T "off" SHOULD be used. Receivers MUST accept
  gaps in the range 0.5T to 1.5T; transmitters SHOULD emit 1T +/- 10%.

White/Black polarities:

- RF: 0 vs 180 degree phase (BPSK-style); amplitude-only acceptable
- Optical: bright vs dim (or on vs off)

On/Off Keying Ambiguity: In purely on/off implementations,
consecutive black symbols create extended off periods with no
physical marker between boundaries. Decoders MUST use timing
analysis to resolve ambiguity by measuring off interval durations.

## Tile Structure

On-air logical order (before line coding):

| Field | Size | Description |
|-------|------|-------------|
| Preamble | 16+ symbols | Alternating long-white/long-black (AGC/PLL) |
| Sync | varies | Polarity-agnostic sync (line-code dependent) |
| Header | 25 B | Version/parameters and per-tile metadata |
| Payload | 0..N B | Message content |
| CRC32 | 4 B | Over Header &#124;&#124; Payload |
| AUTH | 0 or 16 B | OPTIONAL: HMAC-SHA-256 truncated to 16 bytes |
| FEC parity | varies | Reed-Solomon parity after interleaving |

## Header Format (25 Bytes)

Tile header multi-byte fields are little endian. Message payloads
(Identity, ACK, NAK, CAP, DIAG) use network byte order (big-endian)
for interoperability with standard network tooling.

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 1 | version | Protocol version (0x01) |
| 1 | 1 | r_mode | 0=R0, 1=R1, 2=R2 |
| 2 | 1 | line_code | 0=8b/10b, 1=64b/66b |
| 3 | 1 | fec_mode | 0=F0, 1=F1, 2=F2 |
| 4 | 2 | T_us | Symbol unit in microseconds |
| 6 | 1 | flags | See below |
| 7 | 2 | payload_len | Payload bytes (0..65535) |
| 9 | 4 | pkt_id | Packet identifier (groups tiles) |
| 13 | 2 | tile_index | 0..tile_count-1 |
| 15 | 2 | tile_count | Total tiles in this packet |
| 17 | 4 | tile_seq | Monotonic sequence for ACK/NAK |
| 21 | 4 | stream_id | Stream context for compression |

Flags (LSB first):

- bit0: reserved
- bit1: cap
- bit2: diag
- bit3: first tile
- bit4: last tile
- bit5: ack_req
- bit6: auth_present (1 = 16-byte AUTH field follows CRC32)
- bit7: reserved (transmit as 0, ignore on receive)

T_us: Transmitters SHOULD use predefined R-mode values (2000, 1000,
or 500 us). Arbitrary values in the range 100-10000 us are permitted
for experimentation; receivers MUST accept any value in this range.
The r_mode field indicates the closest standard profile for FEC/
interleave selection; T_us provides the actual timing.

pkt_id: SHOULD be initialized to a cryptographically random 32-bit
value for each new packet. Prevents predictability.

tile_seq: 32-bit counter incremented per tile, per stream_id.
SHOULD be initialized to a random value. ACK for sequence N
acknowledges all tiles with tile_seq <= N for that stream_id.

Invalid tile_index: If tile_index >= tile_count, the tile is
malformed. Receivers MUST discard such tiles and SHOULD increment
a diagnostic counter for malformed headers.

Unknown version: If the version field contains a value other than
0x01, the receiver MUST discard the tile. Receivers SHOULD NOT
attempt to interpret fields beyond the version byte for unknown
versions, as field layouts may differ. Implementations SHOULD log
or count unknown-version tiles for diagnostic purposes.

## Dibit Mapping

After line coding, bits are grouped into dibits:

| Dibit | Symbol |
|-------|--------|
| 00 | short-white |
| 01 | short-black |
| 10 | long-white |
| 11 | long-black |

## Sync Acceptance Under Inversion

Decoders MUST try both polarity hypotheses during sync:

- For 64b/66b: accept both 01 and 10 as valid sync headers
- For 8b/10b: accept both comma disparities

Lock the hypothesis with higher correlation. Report polarity_guess
in DIAG.

## Tile CRC and AUTH

CRC32: IEEE 802.3 CRC computed over Header || Payload (raw bytes,
before whitening and line coding). CRC32 is REQUIRED.

AUTH: OPTIONAL. When present, HMAC-SHA-256 truncated to 16 bytes,
computed over (Header || Payload || CRC32). Keying is out-of-band;
this provides integrity only (no confidentiality). If AUTH is
present and validation fails, discard tile.

AUTH presence is signaled by a flag in the header (see flags field,
bit 6). When auth_present=0, the tile contains no AUTH field and
proceeds directly from CRC32 to FEC parity. When auth_present=1,
the 16-byte AUTH field follows CRC32.

For amateur radio use where encryption is prohibited and key
distribution is impractical, AUTH SHOULD be omitted. AUTH is
intended for non-amateur applications (e.g., optical point-to-point
links) where integrity verification adds value.

## Reed-Solomon Interleaving {#reed-solomon}

Reed-Solomon encoding follows {{CCSDS1301}}. FEC parameters:

| Mode | n | k | Parity | Depth D |
|------|---|---|--------|---------|
| F0 | 255 | 191 | 64 | 16 |
| F1 | 255 | 223 | 32 | 8 |
| F2 | 255 | 239 | 16 | 4 |

Shortened codewords: If tile data (Header || Payload || CRC32 ||
AUTH if present) is less than k bytes, zero-pad for encoding,
transmit only actual data + parity. Receivers zero-pad before
decoding.

Multiple codewords: If data exceeds k bytes, divide into blocks
of <= k bytes. Number of blocks MUST NOT exceed D.

Interleaving: After RS encoding, interleave byte-wise round-robin.
For depth D, byte i goes to position (i mod D) * ceil(total/D) +
floor(i/D), where 'total' is the total number of bytes across all
RS codewords including parity.

Encoding steps:

1. Construct: Header || Payload || CRC32 || AUTH (if auth_present=1)
2. Divide into blocks <= k bytes
3. RS encode each block (shortened if needed)
4. Interleave across blocks
5. Apply whitening (PRBS-15 {{ITUO151}} for 8b/10b; native scrambler for 64b/66b)
6. Apply line coding
7. Map dibits to symbols

FEC decode failure: If any RS codeword in a tile cannot be
corrected (errors exceed t = (n-k)/2 symbols), the receiver MUST
discard the entire tile. The receiver SHOULD increment the
rs_failed_blocks counter in DIAG telemetry. The receiver SHOULD
NOT send a NAK for FEC failures (NAK is for missing tiles, not
corrupted ones). In half-duplex operation, the sender's repetition
policy ({{repetition-policy}}) handles recovery; in full-duplex, higher
layers may implement ARQ.

# Line Coding and Whitening

## 64b/66b (Default)

Each 66-bit block consists of a 2-bit sync header followed by a
64-bit payload, per IEEE 802.3 Clause 49 {{IEEE8023}}. The sync header is 01
for data blocks or 10 for control blocks; CWIP uses data blocks
only. Receivers MUST accept either sync header value (01 or 10)
as valid due to polarity-agnostic decoding; the inverted signal
swaps these values.

Block structure (66 bits total):

- Bit 0-1: Sync header (01 = data, 10 = control; accept either)
- Bit 2-65: Scrambled 64-bit payload

Self-synchronizing scrambler (x^58 + x^39 + 1) provides whitening
and is applied to the 64-bit payload only (not the sync header).

Scrambler SHOULD be reinitialized to seed 0x3FFFFFFFFFFFFFF at
start of each tile. Initialization occurs at bit 0 of the first
64-bit payload (immediately after the 2-bit sync header of the
first 66-bit block following preamble). This enables independent
tile decoding. Scrambler state runs continuously across all RS
blocks within a tile; do NOT reinitialize between RS blocks.

## 8b/10b (Optional)

Insert comma (K28.5) every 32 data bytes. Receivers MUST accept
either disparity. Fixed 32-bit comma precedes header.

Whitening: PRBS-15 (x^15 + x^14 + 1) over Header..AUTH.
Seed = ((pkt_id XOR tile_seq) & 0x7FFF); if 0, use 1.

## Line Code Detection

Late-join receivers SHOULD implement automatic detection:

1. After preamble, observe sync pattern characteristics
2. Try both 64b/66b and 8b/10b decoders in parallel
3. Lock onto whichever yields valid sync, header, and CRC32
4. Confirm with line_code field from decoded header

Minimum acquisition: Receivers need at least 3 consecutive valid
66-bit blocks (198 bits) for 64b/66b, or 4 valid 10-bit symbols
including one comma (40 bits) for 8b/10b, before reliable detection.
Implementations SHOULD NOT commit to a line code until the header
CRC32 validates.

# IPv6 Compression

Goal: Carry IPv6 packets of at least 1280-byte MTU {{RFC8200}} while
transmitting minimal bytes on air.

Design note: Implementers requiring more aggressive compression or
fragmentation for extremely constrained links may consider SCHC
(Static Context Header Compression) {{RFC8724}}, which provides
rule-based compression suitable for LPWAN environments. CWIP's P1
profile achieves similar efficiency for established flows via
stream_id context, while P2 uses RFC 6282 for compatibility with
existing 6LoWPAN tooling.

## P1 (Stream-ID Profile)

MUST be implemented. Omit IPv6 source and destination; use
stream_id in header; carry only compressed transport + payload.
Receiver looks up stream_id in its table.

Compressed transport header format: The tile payload begins with
a 1-byte Next Header field (values per IANA protocol numbers),
followed by the transport header compressed per RFC 6282 NHC
(Next Header Compression) encoding, followed by upper-layer
payload. For UDP, the NHC-encoded header is 1-7 bytes depending
on port elision. See RFC 6282 Section 4 for encoding details.

stream_id values SHOULD be cryptographically random. All values
(including zero if randomly selected) are valid.

Unknown stream_id handling: When a receiver encounters a Data tile
(digit 6) with a stream_id not present in its table, it MUST reject
the tile and SHOULD send a NAK with reason "unknown stream_id".
The sender MUST transmit an Identity (digit 0) to establish the
stream_id mapping before retransmitting data. Receivers MAY cache
rejected tiles briefly (recommended: 10 seconds) to allow
reassembly after Identity arrives.

### Stream-ID Table Management

Receivers MUST support at least 16 concurrent stream_id mappings.
Receivers SHOULD support at least 64 mappings. Implementations
MAY support more based on available memory.

Each table entry contains:

- stream_id (4 bytes)
- ipv6_source (16 bytes)
- ipv6_destination (16 bytes)
- lifetime_seconds (4 bytes, as received)
- created_time (timestamp when Identity received)
- last_activity (timestamp of last Data/ACK activity)
- link_layer_source (optional, for conflict detection)

When the table is full and a new Identity arrives, the receiver
MUST evict an existing entry using the following priority:

1. Expired entries (lifetime exceeded)
2. Oldest entry by last_activity time
3. Entry with lowest lifetime_seconds remaining

Receivers MUST NOT evict entries with active reassembly in progress
(i.e., partial tiles received but packet not yet complete).

### Lifetime Semantics

The lifetime_seconds field in Identity specifies how long the
mapping remains valid. The timer starts when Identity is received.
Receiving a new Identity for the same stream_id resets the timer.

Special values:

- 0x00000000: Delete mapping immediately (explicit teardown)
- 0xFFFFFFFF: No automatic expiry (persistent until evicted)

When lifetime expires:

- Receiver MUST delete the mapping
- Receiver MUST discard any incomplete reassembly for that stream_id
- Sender MUST transmit fresh Identity before sending more Data

Recommended default lifetime: 600 seconds. Senders MUST refresh
Identity before lifetime expires if stream remains active.
Recommended refresh: when 50% of lifetime has elapsed.

Last-activity tracking: Receivers SHOULD update last_activity when:

- Identity is received (creates or refreshes entry)
- Data tile is successfully processed for this stream_id
- ACK is sent for this stream_id

### Unknown Stream-ID Cache

When a Data tile arrives with unknown stream_id, receivers MAY
cache the tile pending Identity arrival. Cache parameters:

- Maximum cached tiles per unknown stream_id: 8
- Maximum distinct unknown stream_ids cached: 4
- Cache timeout: 10 seconds from first tile for that stream_id

If Identity arrives within timeout, process cached tiles in
tile_seq order. If timeout expires, discard cached tiles silently.

If cache limits are exceeded, evict oldest unknown stream_id's
tiles first (LRU by first-tile-arrival time).

### Stream-ID Quarantine

After a stream_id mapping is deleted (explicit teardown or expiry),
that stream_id value enters quarantine for 60 seconds. During
quarantine:

- Receivers MUST NOT create a new mapping for that stream_id
- Receivers MUST reject Identity messages for that stream_id
- Receivers SHOULD send NAK with reason "stream_id quarantined"

This prevents late-arriving packets from a previous session being
misattributed to a new session reusing the same stream_id.

Senders SHOULD NOT reuse a stream_id value within 120 seconds of
last use. Given 32-bit random selection, collision is negligible;
implementations SHOULD generate fresh random values rather than
tracking used IDs.

### Conflicting Identity Handling

If a receiver holds a valid (non-expired, non-quarantined) mapping
for stream_id X with addresses (A, B), and receives an Identity
for stream_id X with different addresses (C, D):

- If from same link-layer source: Replace mapping (sender changed
  addresses, e.g., roaming or address rotation)
- If from different link-layer source: Conflict detected

On conflict:

- Receiver MUST retain the original mapping
- Receiver MUST discard the conflicting Identity
- Receiver SHOULD log the event (potential attack or collision)
- Receiver MAY send NAK with reason "stream_id conflict"

Senders receiving "stream_id conflict" NAK MUST generate a new
random stream_id and retransmit Identity.

### Receiver-Initiated Identity Refresh

If a receiver needs to send traffic for a stream_id but has not
received any Identity or Data for that stream_id within 50% of
remaining lifetime, the receiver MAY request refresh.

ACK flags field (offset 40 in Identity, currently reserved):

- Bit 0: Request Identity refresh

When a sender receives an ACK with bit 0 set, it SHOULD retransmit
Identity within 5 seconds. This handles asymmetric paths where
Identity messages are lost but the return path works.

## P2 (RFC 6282 Subset)

RECOMMENDED for link-local/ULA when stream_id not yet established.
Use RFC 6282 compression. Implementations MUST support at minimum:
IPHC with SAC=0/DAC=0 (stateless), 64-bit inline addresses, and
UDP NHC. Context-based compression (SAC=1/DAC=1) is OPTIONAL;
if supported, context 0 MUST be the link-local prefix (fe80::/64).

## P3 (Full Headers)

MUST be implemented. Carry complete IPv6 header uncompressed for
bootstrap/fallback. The tile payload begins with the profile byte
(0x02), immediately followed by the 40-byte IPv6 header at offset 1,
then upper-layer data. Total payload: 1 + 40 + transport + data.

Packet reassembly: Concatenate tiles with same pkt_id in ascending
tile_index. flags.first and flags.last MUST be set appropriately.
Duplicate tiles MUST be ignored.

Conflicting flags: If a receiver sees multiple tiles with
flags.first=1 for the same pkt_id (i.e., tile_index=0 already
received), it MUST discard the later tile and retain the first.
Similarly for flags.last=1 conflicts. This prevents injection
attacks that attempt to corrupt reassembly by claiming boundary
positions.

Incomplete packets: If not all tiles arrive within timeout (at
least 3x repetition interval), discard. MUST NOT deliver incomplete
packets to IPv6 stack.

# Control Digits and Message Types

All message types except Data use TLV framing:

| Offset | Size | Field |
|--------|------|-------|
| 0 | 1 | type (TLV type code) |
| 1 | 1 | length (payload length, not including header) |
| 2.. | var | payload (type-specific data) |

Design note: Early versions left Identity (digit 0) without a TLV
type code. For consistency and extensibility, type 0x00 was
assigned. Implementations SHOULD include the TLV header for all
message types except Data (digit 6).

## Digit 0: Identity (Type 0x00)

Announces a stream_id mapping. TLV payload (41 bytes):

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | stream_id | 32-bit stream identifier |
| 4 | 16 | ipv6_source | Source IPv6 address |
| 20 | 16 | ipv6_destination | Destination IPv6 address |
| 36 | 4 | lifetime_seconds | Lifetime (0=delete, 0xFFFFFFFF=infinite) |
| 40 | 1 | flags | Reserved (transmit as 0, ignore) |

Total TLV: 2 (header) + 41 (payload) = 43 bytes.

Senders SHOULD transmit Identity at session start and every ~5
minutes or on stream_id change.

## Digit 1: ACK (Type 0xA1)

Acknowledges tiles. TLV payload (8 bytes):

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | stream_id | Stream being acknowledged |
| 4 | 4 | tile_seq | Highest acknowledged sequence |

Total TLV: 2 + 8 = 10 bytes.

Acknowledges all tiles with tile_seq <= N for that stream_id.

## Digit 2: NAK (Type 0xA2)

Requests retransmission. TLV payload (variable):

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | stream_id | Stream context |
| 4 | 4 | pkt_id | Packet with missing tiles |
| 8 | 2 | count | Number of missing indices |
| 10 | 2*N | indices[] | Missing tile_index values (2 bytes each) |

Total TLV: 2 + 10 + 2*count bytes.

## Digit 3: DIAG (Type 0xD1)

Receiver telemetry. See {{diag-tlv-structure}} for full structure.

Senders SHOULD emit DIAG on operator request, link problems, or
every 10-15 minutes.

## Digit 5: CAP (Type 0xC5)

Capabilities announcement. TLV payload (6+ bytes):

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 1 | r_modes | Bitmask: bit0=R0, bit1=R1, bit2=R2 |
| 1 | 1 | line_codes | Bitmask: bit0=8b/10b, bit1=64b/66b |
| 2 | 1 | fec_modes | Bitmask: bit0=F0, bit1=F1, bit2=F2 |
| 3 | 1 | features | Bitmask: bit1=ack/nak supported |
| 4 | 2 | max_tile_bytes | Maximum tile payload size |

Total TLV: 2 + 6 = 8 bytes minimum.

## Digit 6: Data

Carries IPv6 packet tiles. Payload is compressed per {{ipv6-compression}}.

Compression profile signaling: The first byte of the Data payload
indicates the compression profile:

| Value | Profile | Description |
|-------|---------|-------------|
| 0x00 | P1 | Stream-ID profile (lookup via stream_id) |
| 0x01 | P2 | RFC 6282 IPHC (inline dispatch byte follows) |
| 0x02 | P3 | Full uncompressed IPv6 header |

The remaining payload bytes follow immediately after the profile
byte. For P2, the RFC 6282 IPHC dispatch byte(s) follow. For P3,
the complete 40-byte IPv6 header follows.

## Digits 4 and 7-9: Reserved

Transmitters MUST NOT use. Reserved for future extensions.

Historical note: Digit 4 was originally allocated for IPv4 packet
transport. This allocation was removed; World IPv6 Launch Day was
2012-06-06 and there will be no IPv4 support in CWIP.

# Operations and Procedures

## Callsign Cadence

Operators SHOULD send callsign at human speed every 10 minutes:
"IP DE \<callsign\> BT". Confirm local regulations.

## Identity Cadence

Send digit 0 (Identity) at session start, every ~5 minutes, and on
stream_id change.

## Repetition Policy {#repetition-policy}

Senders SHOULD repeat data tiles 2x (randomized 5-15s gaps) if no
ACKs are heard. Keeps simplex operation simple.

## ACK/NAK

Optional. ACK acknowledges all tiles up to and including sequence N.
NAK requests retransmission of specific missing tiles.

Half-duplex timing: Senders SHOULD listen 5-15 seconds post-burst
for ACK/NAK responses. In strictly simplex operation, ACK/NAK
cannot be used; rely on repetition policy.

## CAP

Optional. Announces capabilities. Receivers that don't implement
CAP still decode tiles via per-tile header parameters.

## DIAG Fields

See {{diag-tlv-structure}}. Key fields: rx_time, snr, rssi, fec stats,
polarity_guess, clock_skew, optional comment.

## Packet Reassembly and Timeouts

Receivers MUST maintain reassembly buffer per pkt_id. Timeout
SHOULD be at least 3x tile repetition interval (30-60 seconds
typical). MUST NOT deliver incomplete packets. Limit concurrent
buffers to ~32 to prevent exhaustion.

## Human-Layer Session Semantics

The human layer uses standard Morse prosigns around machine-speed
tiles, allowing operators to identify transmissions and frame
sessions audibly.

### Prosigns

| Prosign | Meaning |
|---------|---------|
| CT | Session start |
| SK | Session end |
| BT | Block separator |
| KN | Over to named station |
| K | Over to any station |

### Session Framing

A session SHOULD be framed as:

~~~
CT DE <MYCALL> <THEIRCALL> KN
[Q-codes] BT
IP <digit>
<tiles>
BT
SK
~~~

If no tiles follow (human-only exchange), the IP line is omitted.

### Q-Code Usage

Operators MAY use standard Q-codes {{ITURM1545}} (QTH, QSY, QRK, QSX, etc.)
per normal amateur practice. Receivers SHOULD ignore unrecognized
tokens and continue parsing. Machine-parseable equivalents SHOULD
be sent in DIAG tiles ({{diag-tlv-structure}}) for automation.

### Example

~~~
CT DE K7ABC W1XYZ KN
QTH CN87 QSY 7055 BT
IP 6
<tiles>
BT
SK
~~~

Interpretation: K7ABC calling W1XYZ, located in CN87, moving to
7055 kHz, sending data tiles, end of session.

# Security Considerations

## No Encryption

This specification provides no confidentiality. Payload bits are
visible over the air. This is intentional for amateur radio
compliance.

## AUTH (HMAC)

AUTH is OPTIONAL. When enabled, HMAC-SHA-256 truncated to 16 bytes
provides integrity. Key management is out of scope. If AUTH is
present and validation fails, tile MUST be discarded.

For amateur radio deployments, AUTH SHOULD be omitted to reduce
overhead and avoid key management complexity. The CRC32 provides
sufficient corruption detection for most use cases.

## Replay Mitigation

Identifiers (pkt_id, tile_seq, stream_id) SHOULD be initialized to
cryptographically random values. Receivers MUST reject duplicate
(pkt_id, tile_index) pairs.

## Callsign Compliance

Operators SHOULD include periodic human-speed callsign bursts to
satisfy identification requirements.

## Amateur-Service Caveats

Operators MUST follow local regulations (third-party traffic,
bandwidth, duty cycle). Line codes and FEC are published; CWIP is
not intended to obscure meaning.

## Denial of Service Mitigation

Tile flooding: Receivers SHOULD rate-limit incoming tiles per
stream_id. A recommended limit is 100 tiles per second per
stream_id; excess tiles MAY be dropped silently.

Reassembly buffer exhaustion: Receivers MUST limit concurrent
reassembly buffers ({{packet-reassembly-and-timeouts}} recommends ~32). When the limit is
reached, the oldest incomplete packet SHOULD be discarded to make
room. Implementations SHOULD also enforce per-packet tile count
limits (e.g., 256 tiles maximum).

Rate limiting: Implementations SHOULD implement per-source rate
limiting when source identity can be established. In simplex or
broadcast scenarios where source identity is ambiguous, global
rate limits SHOULD be applied.

## Key Management

This section applies only when AUTH is enabled (auth_present=1).
For amateur radio deployments where AUTH is omitted, key management
is not required.

Why key exchange is out of scope: Establishing a shared secret
without prior coordination requires public-key cryptography
(e.g., Diffie-Hellman key exchange), which adds protocol complexity
inappropriate for CWIP's target use cases. Additionally, some
amateur radio regulatory environments may view key agreement
protocols as encryption-adjacent, even when no content is encrypted.
For point-to-point links, operators can exchange keys when
establishing the link. For group networks, a published "community
key" provides anti-forgery without pretending to be secure against
insiders. For most amateur deployments, omitting AUTH entirely is
the simplest and most appropriate choice.

When AUTH is used:

HMAC key derivation: Keys SHOULD be derived from a master secret
using a KDF (e.g., HKDF-SHA-256) with context binding to
stream_id and station identifiers.

Key rotation: Keys SHOULD be rotated periodically. A recommended
interval is 24 hours or 10,000 tiles, whichever comes first.
Both parties MUST agree on rotation schedule out-of-band.

Out-of-band requirements: Keys MUST be exchanged via a secure
out-of-band channel. Operators SHOULD NOT transmit keys over
the CWIP link itself.

### Callsign-Derived Keys

For group networks (clubs, emergency nets, repeater associations),
a single shared group secret can derive unique pairwise keys for
each station pair using HKDF {{RFC5869}}:

~~~
pairwise_key = HKDF-SHA-256(
    salt   = "CWIP-v1",
    IKM    = group_secret,
    info   = sort(callsign_A, callsign_B),
    L      = 32
)
~~~

Where:

- group_secret is the shared secret for the group (distributed
  out-of-band once per group)
- callsign_A and callsign_B are the two stations' callsigns,
  ASCII-encoded and uppercase
- sort() orders the callsigns lexicographically to ensure both
  directions derive the same key

This approach reduces key management from O(n²) pairwise secrets
to a single group secret while providing unique keys per station
pair. If one pairwise communication is observed, it does not
reveal the group secret or other pairwise keys.

Security considerations for callsign-derived keys:

- The group secret MUST still be distributed out-of-band
- If the group secret is compromised, all pairwise keys are
  compromised
- Callsigns are public information; the security rests entirely
  on the group secret
- No forward secrecy: past traffic can be verified if group
  secret later leaks
- Suitable for anti-spoofing on trusted group networks, not for
  adversarial environments

## Test Key Warning

This section applies only when AUTH is enabled.

The test key specified in {{test-key}} is for interoperability
testing only. Implementations using AUTH MUST NOT use the test key
(CWIP-TEST-KEY-0) in production deployments. Use of the test key
in production voids all integrity guarantees.

## Timing Attacks on HMAC Validation

When AUTH is enabled, HMAC comparison MUST use constant-time
comparison functions to prevent timing side-channels.
Implementations MUST NOT use early-exit string comparison
(e.g., strcmp, memcmp) for AUTH validation. A timing leak could
allow attackers to forge tiles by iteratively guessing AUTH bytes.

## Stream-ID Security

Stream-ID hijacking: An attacker can send a spoofed Identity
message to associate their addresses with a victim's stream_id.
Subsequent Data tiles for that stream_id would be delivered to
the attacker's addresses instead of the legitimate destination.

Mitigations:

- Link-layer source validation ({{conflicting-identity-handling}}): receivers
  reject Identity from different link-layer source than
  the original mapping
- HMAC authentication: if AUTH is enabled, spoofed Identity
  messages will fail validation
- Conflict detection: receivers log and reject conflicting
  Identity (see {{conflicting-identity-handling}})

Stream-ID table exhaustion: An attacker could flood Identity
messages with random stream_ids to fill the receiver's table,
causing legitimate mappings to be evicted.

Mitigations:

- Rate-limit Identity processing: receivers SHOULD accept
  at most 10 Identity messages per second globally
- Activity-based eviction: entries with recent activity
  are preserved over idle entries ({{stream-id-table-management}})
- Per-source limits: if link-layer source is available,
  receivers MAY limit stream_ids per source (e.g., 4)

Quarantine bypass: An attacker aware of a recently-deleted
stream_id might attempt to immediately claim it.

Mitigations:

- 60-second quarantine period ({{stream-id-quarantine}})
- Senders use fresh random stream_ids for new sessions

# Interoperability Test Plan

## Test Key {#test-key}

The following test vectors include AUTH fields to demonstrate the
optional integrity mechanism. For amateur radio deployments, AUTH
SHOULD be omitted (auth_present=0 in flags) and these AUTH fields
would not be present.

WARNING: The test key specified here is for interoperability testing
ONLY. Implementations MUST NOT use this key in production. Use of
the test key in production deployments voids all integrity
guarantees and may enable trivial forgery of tiles.

Test vectors use ASCII key "CWIP-TEST-KEY-0\x00" repeated to 32
bytes for HMAC-SHA-256. Production implementations using AUTH MUST
use properly generated keys.

## Test Vector 1: Identity Advertisement

R1 timing, 64b/66b, F1 FEC.

Header (25 bytes, hex):

~~~
01 01 01 01 E8 03 18 29 00 9D 79 B1 A3 00 00 01
00 57 52 68 46 DF 56 24 39
~~~

Fields: version=0x01, r_mode=1, line_code=1, fec_mode=1, T_us=1000,
flags=0x18 (first+last), payload_len=41, pkt_id=0xA3B1799D,
tile_index=0, tile_count=1, tile_seq=0x46685257,
stream_id=0x392456DF

Payload (41 bytes, hex):

~~~
DF 56 24 39                                     (stream_id)
20 01 0D B8 00 00 00 00 00 00 00 00 00 00 00 01 (ipv6_src)
20 01 0D B8 00 00 00 00 00 00 00 00 00 00 00 02 (ipv6_dst)
00 01 51 80                                     (lifetime=86400s)
00                                              (flags)
~~~

CRC32: 0x6B78EB3E (little-endian: 3E EB 78 6B)

AUTH: D7 EE B0 4F C0 BC 24 59 42 B7 C5 4F 4D 8D F4 31

Tile data before FEC: 25 + 41 + 4 + 16 = 86 bytes.
After RS(255,223) F1: 86 + 32 = 118 bytes (shortened codeword).
After 64b/66b: 118 * 8 * 66/64 = 974 bits ~ 122 bytes on wire.

## Test Vector 2: Small Data Tile

R1 timing, 64b/66b, F1 FEC.

Header (25 bytes, hex):

~~~
01 01 01 01 E8 03 18 20 00 34 24 9D 8B 00 00 01
00 69 84 2A 97 F3 E8 22 08
~~~

Fields: version=0x01, r_mode=1, line_code=1, fec_mode=1, T_us=1000,
flags=0x18 (first+last), payload_len=32, pkt_id=0x8B9D2434,
tile_index=0, tile_count=1, tile_seq=0x972A8469,
stream_id=0x0822E8F3

Payload (32 bytes, hex):

~~~
00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F
~~~

CRC32: 0x67BE7BF1 (little-endian: F1 7B BE 67)

AUTH: 41 9E 0C B7 44 5D E0 B8 D5 41 CB 6B AE 61 73 C4

Tile data before FEC: 25 + 32 + 4 + 16 = 77 bytes.
After RS(255,223) F1: 77 + 32 = 109 bytes.
After 64b/66b: 109 * 8 * 66/64 = 899 bits ~ 113 bytes on wire.

## Test Vector 3: Inverted Polarity

Same as Test Vector 2 but entire signal inverted (white\<-\>black).
64b/66b sync headers flip: 01\<-\>10. Receiver MUST decode correctly
and report polarity_guess=1 in DIAG.

Inversion transforms dibits as follows (XOR with 01):

| Normal | Inverted |
|--------|----------|
| 00 (SW) | 01 (SB) |
| 01 (SB) | 00 (SW) |
| 10 (LW) | 11 (LB) |
| 11 (LB) | 10 (LW) |

Example: First header byte 0x01 encodes as dibits 00 00 00 01.
After inversion: 01 01 01 00, which decodes as 0x54.

Inverted header (25 bytes, hex):

~~~
54 54 54 54 BD 56 4D 7C 55 C8 2C E4 D6 55 55 54
55 9C D1 7F C2 A6 BD 71 5D
~~~

Inverted payload (32 bytes, hex):

~~~
55 54 57 56 51 50 53 52 5D 5C 5F 5E 59 58 5B 5A
45 44 47 46 41 40 43 42 4D 4C 4F 4E 49 48 4B 4A
~~~

Inverted CRC32: A4 2E EB 92

Inverted AUTH: 14 CB 59 E2 11 08 B5 ED 80 14 9E 9E FB 94 26 91

Decoders MUST produce identical decoded output as Test Vector 2.

# IANA Considerations

This document has no IANA actions. Although the protocol defines
TLV type codes ({{control-digits-and-message-types}}, {{tlv-type-codes}}), control digits ({{control-digits-and-message-types}}),
R-modes ({{operating-profiles}}), line codes ({{line-coding-and-whitening}}), and FEC modes
({{reed-solomon-interleaving}}), this specification is published with Experimental
status for amateur and research use. The Experimental designation
exempts the protocol from IANA registry creation requirements.
Should the protocol advance to Standards Track, formal registries
for these code points would be established at that time.

--- back

# TLV Type Codes {#tlv-type-codes}

| Type | Digit | Message |
|------|-------|---------|
| 0x00 | 0 | Identity |
| 0xA1 | 1 | ACK |
| 0xA2 | 2 | NAK |
| 0xC5 | 5 | CAP |
| 0xD1 | 3 | DIAG |

Note: Data (digit 6) does not use TLV framing; it carries raw
tile payload. Digits 4 and 7-9 are reserved.

# DIAG TLV Structure (Type 0xD1) {#diag-tlv-structure}

TLV header: type=0xD1, length=variable.

Core fields (44 bytes):

| Field | Size | Description |
|-------|------|-------------|
| rx_time_ms_gnss | 8 | ms since GNSS epoch {{ICDGPS200}} (1980-01-06 UTC) |
| rx_freq_hz_est | 8 | Estimated RX center frequency (Hz) |
| snr_db_x10 | 2 | SNR * 10 dB |
| rssi_dbm_x10 | 2 | RSSI * 10 dBm |
| fec_mode | 1 | F0/F1/F2 |
| rs_blocks | 2 | RS blocks processed |
| rs_corrected_bytes | 4 | Total corrected bytes |
| rs_failed_blocks | 2 | Unrecoverable blocks |
| ber_x1e6 | 4 | Pre-RS BER (ppm) |
| clock_skew_ppm | 2 | RX vs symbol clock (signed) |
| polarity_guess | 1 | 0=normal, 1=inverted |
| line_code | 1 | 0=8b/10b, 1=64b/66b |
| T_us | 2 | Symbol unit in microseconds |
| freq_offset_hz | 4 | Offset from nominal (signed) |

Station fields (28 bytes):

| Field | Size | Description |
|-------|------|-------------|
| tx_freq_hz | 8 | Sender's TX frequency (Hz) |
| listen_freq_hz | 8 | Sender's RX frequency (Hz, 0=simplex) |
| grid | 8 | Maidenhead grid {{IARU}} (4-8 chars, null-padded) |
| qrk | 1 | Readability 1-5, 0=not assessed |
| qsb | 1 | Fading: 0=none, 1=slow, 2=fast, 0xFF=N/A |
| qrm | 1 | Interference 0-5, 0xFF=not assessed |
| qrn | 1 | Noise 0-5, 0xFF=not assessed |

Comment (variable):

| Field | Size | Description |
|-------|------|-------------|
| comment_len | 1 | ASCII comment length (0-255) |
| comment | var | Optional operator note |

Total: 73 bytes minimum (no comment) to 328 bytes maximum.

Field notes:

tx_freq_hz/listen_freq_hz:
: Enable split-frequency operation. When listen_freq_hz=0,
  station operates simplex on tx_freq_hz.

grid:
: Maidenhead locator (e.g., "CN87wk"). Shorter grids are
  null-padded. All-zeros means not reported.

qrk/qsb/qrm/qrn:
: Subjective RF assessment matching Q-code {{ITURM1545}} semantics.
  These are operator-assessed values, complementing the measured
  snr_db_x10 and rssi_dbm_x10.

Measurement conventions:

snr_db_x10:
: Signal-to-noise ratio in dB * 10. Implementations SHOULD follow
  {{WSJTX}} convention: SNR relative to noise power in a 2500 Hz
  reference bandwidth. Example: -15 dB SNR encodes as -150
  (0xFF6A as signed 16-bit).

rssi_dbm_x10:
: Received signal strength in dBm * 10. Follows {{LORA}} convention.
  Example: -110 dBm encodes as -1100.

qrk:
: Link quality indicator analogous to {{IEEE802154}} LQI, compressed
  to 1-5 scale per amateur Q-code convention.

rs_corrected_bytes, rs_failed_blocks:
: Reed-Solomon decoder statistics following {{CCSDS211}} telemetry
  conventions for reporting FEC performance on constrained links.

# Quick Reference Tables

R-modes:

| Mode | T | Throughput |
|------|---|------------|
| R0 | 2.0 ms | ~350-600 bps |
| R1 | 1.0 ms | ~600-1000 bps |
| R2 | 0.5 ms | ~1.2-2 kbps |

Line codes:

- 0 = 8b/10b (+PRBS-15)
- 1 = 64b/66b (native scrambler)

FEC modes:

| Mode | RS Parameters | Interleave Depth |
|------|---------------|------------------|
| F0 | RS(255,191) | 16 |
| F1 | RS(255,223) | 8 |
| F2 | RS(255,239) | 4 |

Control digits:

| Digit | Message |
|-------|---------|
| 0 | Identity |
| 1 | ACK |
| 2 | NAK |
| 3 | DIAG |
| 4 | Reserved |
| 5 | CAP |
| 6 | Data |
| 7-9 | Reserved |

Dibit mapping:

| Dibit | Symbol |
|-------|--------|
| 00 | short-white |
| 01 | short-black |
| 10 | long-white |
| 11 | long-black |

Header flags (byte 6):

- bit3 = first tile
- bit4 = last tile
- bit5 = ack_req
- bit6 = auth_present (0 = no AUTH, 1 = 16-byte AUTH after CRC32)

# FM Audio Transport {#fm-transport}

For FM transceivers lacking CW capability (e.g., MURS, business band,
amateur FM repeaters), CWIP symbols MAY be conveyed as audio tones.

Tone encoding:

| Symbol State | Audio |
|--------------|-------|
| Mark (1) | 1200 Hz tone |
| Space (0) | Silence |

The 1200 Hz frequency is chosen for compatibility with existing packet
radio equipment and the Bell 202 modem standard. Implementations MAY
use other frequencies (e.g., 800 Hz for CW sidetone compatibility)
provided both endpoints agree.

Symbol timing follows the same R-mode parameters as CW transport:
R1 mode uses 1.0 ms symbols, yielding ~1000 baud.

Detection: A Goertzel filter or equivalent single-frequency detector
at the agreed tone frequency, with threshold set to distinguish tone
presence from background noise.

FM channel considerations:

- Pre-emphasis/de-emphasis: Standard FM voice radios apply 6 dB/octave
  pre-emphasis. The 1200 Hz tone will be boosted ~6 dB relative to
  baseband. Receivers should account for this or use flat audio paths.

- Channel bandwidth: Narrowband FM (12.5 kHz) is sufficient for
  1200 Hz tone at 1000 baud.

- CTCSS/DCS: If the FM channel uses tone squelch, ensure the CWIP
  audio tone does not conflict with CTCSS frequencies (67-254 Hz)
  or DCS codes.

Regulatory notes:

- MURS (47 CFR 95 Subpart J): Permits data transmissions. No license
  required. Station identification not required.

- Business band (47 CFR 90): Data permitted on licensed frequencies.
  Check license conditions.

- Amateur FM: Permitted under Part 97. Standard identification
  requirements apply. The human-readable Morse header satisfies
  identification if sent at the required intervals.

# FEC Design Rationale {#fec-rationale}

This appendix explains the choice of Reed-Solomon forward error
correction rather than more modern codes.

Why not LDPC or turbo codes?

Modern weak-signal modes (FT8, FT4) use LDPC codes, achieving
approximately 6 dB better coding gain than Reed-Solomon at low SNR.
However, these gains assume soft-decision decoding, where the
demodulator provides likelihood ratios ("70% confident this is a 1")
rather than hard bits.

OOK (on-off keying) naturally produces hard decisions: the Goertzel
filter detects tone energy, which is thresholded to a 0 or 1. Soft
information can be extracted from energy levels, but awkwardly.
PSK and FSK modulations provide soft decisions more naturally, which
is why weak-signal modes use them.

Why Reed-Solomon fits OOK:

1. Works well with hard-decision decoding
2. Excels at burst errors (matches fading, static crashes, QRM)
3. Interleaving spreads bursts across codewords effectively
4. Simple to implement (single library dependency)
5. Space and broadcast heritage (CCSDS, DVB)

The CWIP channel model:

| Error Source | Pattern | RS Suitability |
|--------------|---------|----------------|
| Fading (QSB) | Burst erasures | Excellent |
| Static (QRN) | Impulse bursts | Excellent |
| QRM | Burst interference | Excellent |
| Thermal noise | Random bits | Adequate |

For predominantly burst-error channels with hard-decision demodulation,
Reed-Solomon with interleaving is arguably the correct choice, not
merely a compromise.

CWIP does not compete with weak-signal modes. It is designed to be
implementable, amusing, and functional over channels where operators
can actually hear the transmission. For stations pushing the limits
of propagation, FT8 exists and works well. CWIP targets a different
use case: human-supervised, machine-assisted communication at
practical signal levels.
