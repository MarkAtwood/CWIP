---
title: "IPv6-Embedded Human Identifier Encoding"
abbrev: "Ham64 over IPv6 /16"
docname: draft-atwood-ham64-00
category: exp
ipr: trust200902
area: Internet
workgroup: Network Working Group
keyword: Internet-Draft

stand_alone: yes
pi: [toc, sortrefs, symrefs]

author:
 -
    name: Mark Atwood
    email: mark@reviewcommit.com

normative:
  RFC2119:
  RFC8174:
  RFC4291:
  RFC5234:
  ISO3166-1:
    title: "ISO 3166-1:2020 Codes for the representation of names of countries and their subdivisions - Part 1: Country codes"
    author:
      org: International Organization for Standardization
    date: 2020
  ISO3166-2:
    title: "ISO 3166-2:2020 Codes for the representation of names of countries and their subdivisions - Part 2: Country subdivision code"
    author:
      org: International Organization for Standardization
    date: 2020

informative:
  RFC3596:
  RFC3849:
  RFC4193:
  RFC4301:
  RFC4941:
  RFC6890:
  RFC8200:
  RFC8446:
  ITURM1544:
    title: "Recommendation ITU-R M.1544: Minimum Requirements for Identifying Amateur Radio Stations"
    author:
      org: International Telecommunication Union
    date: 2023
    seriesinfo:
      ITU-R: M.1544-1
  IARU:
    title: "IARU Region 1 VHF Managers Handbook: Maidenhead Locator System"
    author:
      org: International Amateur Radio Union
    target: https://www.iaru-r1.org/
  ICAOANNEX7:
    title: "Annex 7 to the Convention on International Civil Aviation: Aircraft Nationality and Registration Marks"
    author:
      org: International Civil Aviation Organization
    date: 2012
    seriesinfo:
      ICAO: Annex 7, 6th Edition
  ICAODOC7910:
    title: "Doc 7910: Location Indicators"
    author:
      org: International Civil Aviation Organization
    date: 2022
  ISO11619:
    title: "ISO 11619: Small craft — Hull identification — Hull Identification Number (HIN)"
    author:
      org: International Organization for Standardization
    date: 2019
  E164:
    title: "Recommendation ITU-T E.164: The international public telecommunication numbering plan"
    author:
      org: International Telecommunication Union
    date: 2010
    seriesinfo:
      ITU-T: E.164

--- abstract

This document specifies an experimental encoding system for embedding short human-readable identifiers directly into IPv6 addresses using a dedicated /16 prefix and a compact 6-bit symbol alphabet called "Ham64". The encoding supports multiple identifier types including amateur radio callsigns, aircraft tail numbers, airport codes, vehicle license plates, boat hull identification numbers, Maidenhead grid locators, postal codes, telephone numbers, and generic identifiers. The system provides 112 bits of payload within the IPv6 address, accommodating up to 17 Ham64 symbols plus metadata including version, type, and optional geographic qualifiers.

--- middle

# Introduction

IPv6 addresses {{RFC4291}} provide 128 bits of address space, enabling novel uses beyond simple host identification. This specification defines an experimental encoding that embeds human-readable identifiers directly into IPv6 addresses, facilitating applications in IoT, mobile networks, amateur radio data networks, aviation tracking, maritime systems, and location-based services.

The encoding uses a fixed /16 prefix followed by 112 bits of structured payload. The payload contains a version field, an identifier type field, optional geographic metadata, and up to 17 symbols from a 6-bit alphabet optimized for alphanumeric identifiers common in transportation, communications, and location systems.

## Motivation

Many operational domains use short, standardized identifiers:

* Amateur radio operators use callsigns (e.g., K7ABC, G4XYZ/P)
* Aircraft use tail numbers (e.g., N9748C)
* Airports use ICAO and IATA codes (e.g., KSEA, SEA)
* Vehicles use license plates with regional variations
* Boats use Hull Identification Numbers (HIN)
* Radio operators use Maidenhead grid locators (e.g., CN87UM)
* Postal systems use postcodes with national formats

Embedding these identifiers in IPv6 addresses enables:

* Direct address-to-identity mapping without DNS or external databases
* Simplified routing and filtering based on identifier patterns
* Enhanced traceability in mobile and IoT deployments
* Integration with existing identifier ecosystems

## Scope

This specification defines:

* The bit-level structure of encoded IPv6 addresses
* The Ham64 6-bit symbol alphabet
* Encoding and decoding procedures
* Type-specific encoding rules for supported identifier classes
* Geographic prefix encoding for regional identifiers

This specification does not define:

* Routing protocols or policies for the special-use prefix
* Application-layer protocols using these addresses
* Registration or allocation procedures for identifiers

# Conventions and Definitions

{::boilerplate bcp14}

The following terms are used throughout this document:

* **Ham64**: The 6-bit symbol alphabet defined in {{ham64-symbol-table}}.
* **AUTH prefix**: An in-band issuing authority qualifier encoded using Ham64 symbols, identifying the jurisdiction that assigned the identifier.
* **END symbol**: A special Ham64 symbol (value 63) marking the end of the identifier.
* **Payload**: The 112 bits following the /16 prefix.
* **Symbol**: A single 6-bit encoded character from the Ham64 alphabet.

# Overview

## Address Structure

An encoded IPv6 address consists of:

~~~
+----------------+------------------------------------------+
|   /16 Prefix   |           112-bit Payload               |
+----------------+------------------------------------------+
~~~

The /16 prefix is a special-use IPv6 prefix allocated by IANA (see {{iana-considerations}}).

The 112-bit payload is structured as:

~~~
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| VERS  |  TYPE |A-K|         Symbol Stream (up to 102 bits)   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Symbol Stream (continued)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Symbol Stream (continued)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|      Symbol Stream (continued)      |P|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
~~~

Where:

* **VERS** (3 bits): Version field. Value `001` for this specification.
* **TYPE** (4 bits): Identifier type (see {{identifier-type-encoding-rules}}).
* **A-K** (2 bits): Airport kind subfield, used only when TYPE=2.
* **Symbol Stream** (up to 102 bits): Up to 17 six-bit Ham64 symbols.
* **P** (1 bit): Padding bit, always 0.

## Encoding Process

1. Normalize the identifier (uppercase, trim whitespace)
2. Construct the header (VERS, TYPE, A-KIND)
3. Prepend AUTH prefix if required by type or regional context
4. Encode identifier symbols using Ham64
5. Append END symbol if fewer than 17 symbols used
6. Pack bits MSB-first into the 112-bit payload
7. Pad remaining bits with zeros

## Decoding Process

1. Extract the 112-bit payload
2. Parse VERS, TYPE, and A-KIND from header
3. Extract symbol stream
4. Decode Ham64 symbols until END or 17 symbols reached
5. Process AUTH prefix if present
6. Reconstruct identifier string according to type rules

# Address Format

## Header Fields

### VERS Field

The VERS field occupies bits 0-2 of the payload. For this specification, VERS MUST be `001` (binary).

Implementations MUST reject addresses where VERS is not `001`. Such addresses are either malformed or encoded using a future version that is not compatible with this specification. Implementations SHOULD log unrecognized VERS values to aid debugging but MUST NOT attempt to decode the payload.

Future versions may define alternative encoding profiles using different VERS values.

### TYPE Field

The TYPE field occupies bits 3-6 of the payload and specifies the identifier class:

| Value | Identifier Type                    |
|-------|------------------------------------|
| 0     | Amateur radio callsign             |
| 1     | Aircraft tail number               |
| 2     | Airport code                       |
| 3     | Vehicle license plate              |
| 4     | Boat Hull Identification Number    |
| 5     | Maidenhead grid locator            |
| 6     | Generic identifier                 |
| 7     | Postal code                        |
| 8     | Telephone number (E.164)           |
| 9-15  | Reserved                           |

### A-KIND Field

The A-KIND field occupies bits 7-8 of the payload. It is used only when TYPE=2 (airport code):

| Value | Airport Code Type                  |
|-------|------------------------------------|
| 00    | ICAO (4-letter code)               |
| 01    | IATA (3-letter code)               |
| 10    | Local/National (requires AUTH)      |
| 11    | Reserved                           |

For all other TYPE values, A-KIND MUST be set to `00`.

## Symbol Stream

The symbol stream begins at bit 9 and continues for up to 102 bits (17 symbols × 6 bits). Symbols are packed MSB-first with no delimiters.

If the identifier requires fewer than 17 symbols, the stream MUST be terminated with an END symbol (value 63), and remaining bits MUST be zero.

If the identifier uses exactly 17 symbols, the END symbol is omitted.

## Local Extensions

Operators MAY append a slash (/) followed by a locally assigned short string to any identifier type. This pattern is commonly used to add context-specific qualifiers such as location, operator designation, or temporary status.

**Examples**:

* K7ABC/M (mobile operation)
* KSEA/TWR (tower frequency)
* 20500/WEST (building within postal area)

The slash and extension are encoded as part of the symbol stream using standard Ham64 encoding. Implementations SHOULD preserve the extension during decoding but are not required to interpret its meaning.

# Ham64 Symbol Table {#ham64-symbol-table}

The Ham64 alphabet encodes 64 distinct values in 6 bits:

| Value | Character | Value | Character | Value | Character | Value | Character |
|-------|-----------|-------|-----------|-------|-----------|-------|-----------|
| 0     | 0         | 16    | G         | 32    | W         | 48    | ?         |
| 1     | 1         | 17    | H         | 33    | X         | 49    | (rsv)     |
| 2     | 2         | 18    | I         | 34    | Y         | 50    | (rsv)     |
| 3     | 3         | 19    | J         | 35    | Z         | 51    | (rsv)     |
| 4     | 4         | 20    | K         | 36    | (space)   | 52    | (rsv)     |
| 5     | 5         | 21    | L         | 37    | .         | 53    | (rsv)     |
| 6     | 6         | 22    | M         | 38    | -         | 54    | (rsv)     |
| 7     | 7         | 23    | N         | 39    | /         | 55    | (rsv)     |
| 8     | 8         | 24    | O         | 40    | &         | 56    | (rsv)     |
| 9     | 9         | 25    | P         | 41    | @         | 57    | (rsv)     |
| 10    | A         | 26    | Q         | 42    | !         | 58    | (rsv)     |
| 11    | B         | 27    | R         | 43    | _         | 59    | (rsv)     |
| 12    | C         | 28    | S         | 44    | :         | 60    | (rsv)     |
| 13    | D         | 29    | T         | 45    | ,         | 61    | (rsv)     |
| 14    | E         | 30    | U         | 46    | +         | 62    | AUTH      |
| 15    | F         | 31    | V         | 47    | (rsv)     | 63    | END       |

## Character Classes

* **Digits** (0-9): Values 0-9
* **Letters** (A-Z): Values 10-35
* **Punctuation**: Values 36-46 and 48
* **Special Functions**: AUTH (62), END (63)
* **Reserved**: Values 47, 49-61

Reserved values MUST NOT be used in VERS=001 encodings. Implementations encountering reserved values MUST reject the address as invalid and MUST NOT attempt to decode or forward it.

## Special Symbols

### AUTH Symbol (Value 62)

The AUTH symbol introduces an in-band issuing authority prefix, identifying the jurisdiction that assigned the identifier. When present, it MUST be the first symbol in the stream (immediately following the header).

The AUTH prefix format is:

~~~
AUTHCC(space)
AUTHCCSS(space)
~~~

Where:

* **AUTH**: The AUTH symbol (value 62)
* **CC**: Two-letter country code conforming to [ISO3166-1] alpha-2
* **SS**: Optional two-letter subdivision code (state, province, region) conforming to [ISO3166-2]
* **(space)**: Mandatory space separator (value 36) terminating the AUTH prefix

Decoders read symbols after AUTH until encountering a space (value 36). The resulting 2 or 4 letters are interpreted as country alone or country plus subdivision.

Examples:

* `AUTHUS(space)` → "US" (4 symbols: AUTH + U + S + space)
* `AUTHUSDC(space)` → "USDC" (6 symbols: AUTH + U + S + D + C + space)
* `AUTHGB(space)` → "GB"
* `AUTHCABC(space)` → "CABC"

### END Symbol (Value 63)

The END symbol terminates the symbol stream when fewer than 17 symbols are used. It MUST be the last non-zero symbol in the stream.

If exactly 17 symbols are required, the END symbol is omitted.

**Multiple END symbols**: Decoders MUST stop at the first END symbol encountered. Any symbols following the first END (including additional END symbols) MUST be ignored. Encoders MUST NOT emit more than one END symbol. Addresses containing multiple END symbols are malformed but MAY be decoded leniently by treating the first END as authoritative.

# Identifier Type Encoding Rules {#identifier-type-encoding-rules}

## Type 0: Amateur Radio Callsign

Amateur radio callsigns follow international ITU {{ITURM1544}} patterns, typically 3-6 characters with optional suffixes.

**Format**: `[PREFIX]CALLSIGN[/SUFFIX]`

**Examples**:

* K7ABC
* G4XYZ/P
* VE3ABC/MM

**AUTH prefix**: NOT used. Country is implicit in callsign prefix.

**Encoding**:

1. Normalize to uppercase
2. Encode directly using Ham64 symbols
3. Append END if fewer than 17 symbols

## Type 1: Aircraft Tail Number

Aircraft registration numbers (tail numbers) {{ICAOANNEX7}} identify civil aircraft. Format varies by country but typically includes a country prefix and alphanumeric sequence.

**Format**: Country-specific, commonly `N12345` (US), `G-ABCD` (UK), `VH-ABC` (Australia)

**Examples** (fictional):

* N9748C (FAA reserved for film/fiction)
* G-XXXX (UK CAA disallows XXX combinations)
* VH-XXX (likewise invalid)

**AUTH prefix**: NOT used. Country is implicit in registration prefix.

**Encoding**:

1. Normalize to uppercase
2. Encode directly including hyphens if present
3. Append END if fewer than 17 symbols

## Type 2: Airport Code

Airports are identified by ICAO {{ICAODOC7910}} (4-letter), IATA (3-letter), or local codes.

**A-KIND values**:

* `00`: ICAO code (4 letters)
* `01`: IATA code (3 letters)
* `10`: Local/national code (requires AUTH prefix)

**Examples**:

* KSEA (ICAO, A-KIND=00)
* SEA (IATA, A-KIND=01)
* 0S9 (local, A-KIND=10, requires AUTH)

**AUTH prefix**: Required only for A-KIND=10.

**Encoding**:

1. Set A-KIND based on code type
2. Prepend AUTH if A-KIND=10
3. Encode code symbols
4. Append END if fewer than 17 symbols

## Type 3: Vehicle License Plate

Vehicle registration plates vary widely by jurisdiction. Encoding supports alphanumeric plates with common punctuation.

**Format**: Jurisdiction-specific

**Examples**:

* ABC-1234 (US)
* AB12 CDE (UK)
* 1ABC234 (Australia)

**AUTH prefix**: Optional but recommended for disambiguation.

**Encoding**:

1. Normalize to uppercase
2. Prepend AUTH if regional context needed
3. Encode plate characters
4. Append END if fewer than 17 symbols

## Type 4: Boat Hull Identification Number

Hull Identification Numbers (HIN) {{ISO11619}} uniquely identify boats. US HINs are 12 characters; other countries have similar systems.

**Format**: Typically 12 alphanumeric characters

**Example**: ABC12345D404 (ABC is USCG reserved example MIC)

**AUTH prefix**: REQUIRED. All HINs MUST include a country-level AUTH prefix.

**Length constraints**: A 12-character HIN uses 12 symbols. With a country-only AUTH prefix (4 symbols), the total is 16 symbols, which fits within the 17-symbol limit. Subdivision-level AUTH (6 symbols) plus a 12-character HIN would require 18 symbols, exceeding the limit. Implementations MUST use country-only AUTH prefixes for HINs.

**Encoding**:

1. Normalize to uppercase
2. Prepend country-level AUTH prefix
3. Encode HIN characters
4. Append END if fewer than 17 symbols

## Type 5: Maidenhead Grid Locator

Maidenhead locators {{IARU}} encode geographic positions using a hierarchical grid system. Standard precision is 6 characters; extended precision uses 8 or more.

**Format**: `AA##aa[##][aa]`

**Examples**:

* CN87UM
* FN31PR
* JO01/OP (with operator suffix)

**AUTH prefix**: NOT used. Location is encoded in the grid itself.

**Encoding**:

1. Normalize to uppercase
2. Encode grid characters
3. Append END if fewer than 17 symbols

**Note on case**: Traditional Maidenhead notation uses lowercase for subsquare letters (e.g., "CN87um" rather than "CN87UM") as a visual convention. However, Ham64 encoding normalizes all letters to uppercase since the 6-bit symbol alphabet does not distinguish case. Decoders MAY restore lowercase for subsquare positions (characters 5-6 and 9-10) when presenting Maidenhead locators for human display, but this is a presentation choice, not an encoding requirement.

## Type 6: Generic Identifier

Generic identifiers support arbitrary alphanumeric strings with Ham64-compatible punctuation.

**Format**: Unrestricted (within Ham64 character set)

**AUTH prefix**: Optional.

**Encoding**:

1. Normalize to uppercase
2. Prepend AUTH if needed
3. Encode identifier characters
4. Append END if fewer than 17 symbols

## Type 7: Postal Code

Postal codes (postcodes, ZIP codes) identify mail delivery areas. Formats vary by country. Encoding supports postal codes at any level of granularity, from broad postal areas to specific delivery points.

**Format**: Country-specific

**Examples**:

* 20500 (US 5-digit ZIP, White House)
* 20500-0003 (US ZIP+4, White House)
* 20500-0003-16-0 (US ZIP+4+2+1, delivery point)
* SW1A 1AA (UK postcode)
* K1A 0B1 (Canada)
* 100-0001 (Japan)

**AUTH prefix**: REQUIRED. Postal codes are meaningless without country context.

**Length constraints**: The AUTH prefix consumes 4 symbols (country only) or 6 symbols (country + subdivision), leaving 13 or 11 symbols respectively for the postal code itself. Postal codes exceeding this limit will be truncated per {{symbol-stream-construction}}. For jurisdictions with long postal codes where subdivision context is important, implementations SHOULD use country-only AUTH prefixes to maximize postal code capacity, relying on the postal code format itself to imply the subdivision.

**Encoding**:

1. Normalize to uppercase
2. Prepend AUTH with country (and optionally subdivision)
3. Encode postcode characters including hyphens and spaces
4. Append END if fewer than 17 symbols

## Type 8: Telephone Number (E.164)

Telephone numbers in E.164 {{E164}} format. E.164 numbers consist of a country code (1-3 digits) followed by a national number, with a maximum total length of 15 digits.

**Format**: `+[CC][NUMBER]` where CC is the country code

**Examples** (fictional):

* +15550100 (US, 555-0100 fictional exchange)
* +442079460123 (UK, fictional)

**AUTH prefix**: NOT used. Country code is explicit in E.164 format.

**Privacy warning**: Embedding telephone numbers in IPv6 addresses exposes them in packet headers, routing tables, and network logs. Operators should consider privacy implications before deployment.

**Encoding**:

1. Strip the leading `+` (not encoded)
2. Encode digits directly using Ham64 symbols 0-9
3. Append END if fewer than 17 symbols

**Note**: E.164 numbers are purely numeric, so this type does not leverage Ham64's alphanumeric capability. It is included for completeness and for scenarios where telephone-to-IP mapping is desired.

# Encoding Procedures

## Normalization

Before encoding, identifiers MUST be normalized:

1. Convert all letters to uppercase
2. Trim leading and trailing whitespace
3. Collapse multiple consecutive spaces to a single space; implementations MUST perform this normalization to ensure canonical encoding
4. Verify all characters exist in Ham64 alphabet

If normalization fails (invalid characters), the identifier cannot be encoded.

## Header Construction

1. Set VERS to `001` (binary)
2. Set TYPE based on identifier class ({{identifier-type-encoding-rules}})
3. Set A-KIND:
   * If TYPE=2, set based on airport code type
   * Otherwise, set to `00`

## Symbol Stream Construction {#symbol-stream-construction}

1. If AUTH prefix required:
   a. Append AUTH symbol (62)
   b. Append country code (2 letters)
   c. If subdivision needed, append subdivision (2 letters)
   d. Append space (36)

2. For each character in normalized identifier:
   a. Look up Ham64 value
   b. Append 6-bit value to stream

3. If fewer than 17 symbols total:
   a. Append END symbol (63)

4. If more than 17 symbols:
   a. Truncate to 17 symbols (END omitted)

## Bit Packing

1. Initialize 112-bit payload to all zeros
2. Write VERS (3 bits) at offset 0
3. Write TYPE (4 bits) at offset 3
4. Write A-KIND (2 bits) at offset 7
5. Write symbol stream MSB-first starting at offset 9
6. Leave remaining bits as zero (padding)

**Bit ordering within symbols**: Each 6-bit symbol is written with its most significant bit first. For a symbol with value V (0-63), bit 5 (weight 32) is written first, followed by bit 4 (weight 16), down to bit 0 (weight 1). For example, the letter 'K' (value 20 = 0b010100) is written as bits `0 1 0 1 0 0` in transmission order.

## Address Assembly

1. Take allocated /16 prefix
2. Append 112-bit payload
3. Result is complete 128-bit IPv6 address

# Pseudocode

## Encoding

~~~
function encode_identifier(prefix, type, identifier, geo):
    # Normalize
    id = identifier.upper().strip()
    id = collapse_spaces(id)
    
    # Validate characters
    for char in id:
        if char not in HAM64_ALPHABET:
            return ERROR
    
    # Build header
    vers = 0b001
    a_kind = 0b00
    
    if type == 2:  # Airport
        a_kind = determine_airport_kind(id, geo)
    
    # Build symbol stream
    symbols = []
    
    if geo is not None:
        symbols.append(62)  # AUTH
        symbols.extend(encode_auth_prefix(geo))
    
    for char in id:
        symbols.append(HAM64_LOOKUP[char])
    
    if len(symbols) < 17:
        symbols.append(63)  # END
    
    if len(symbols) > 17:
        symbols = symbols[:17]
    
    # Pack bits
    payload = (vers << 109) | (type << 105) | (a_kind << 103)
    
    bit_offset = 103
    for sym in symbols:
        bit_offset -= 6
        payload |= (sym << bit_offset)
    
    # Assemble address
    address = (prefix << 112) | payload
    
    return address

function encode_auth_prefix(auth):
    symbols = []
    symbols.append(HAM64_LOOKUP[auth.country[0]])
    symbols.append(HAM64_LOOKUP[auth.country[1]])

    if auth.subdivision:
        symbols.append(HAM64_LOOKUP[auth.subdivision[0]])
        symbols.append(HAM64_LOOKUP[auth.subdivision[1]])

    symbols.append(36)  # space terminator
    return symbols
~~~

## Decoding

~~~
function decode_identifier(address, prefix_len):
    # Extract payload
    payload = address & ((1 << 112) - 1)
    
    # Parse header
    vers = (payload >> 109) & 0b111
    type = (payload >> 105) & 0b1111
    a_kind = (payload >> 103) & 0b11
    
    if vers != 0b001:
        return ERROR
    
    # Extract symbols
    symbols = []
    bit_offset = 103
    
    for i in range(17):
        bit_offset -= 6
        sym = (payload >> bit_offset) & 0b111111
        
        if sym == 63:  # END
            break
        
        symbols.append(sym)
    
    # Decode symbols
    identifier = ""
    geo = None
    i = 0
    
    if symbols[0] == 62:  # AUTH
        i, geo = decode_auth_prefix(symbols, 1)
    
    for sym in symbols[i:]:
        identifier += HAM64_REVERSE[sym]
    
    return {
        "type": type,
        "a_kind": a_kind,
        "geo": geo,
        "identifier": identifier
    }

function decode_auth_prefix(symbols, start):
    # Read symbols until space (36)
    letters = []
    i = start
    while i < len(symbols) and symbols[i] != 36:
        letters.append(HAM64_REVERSE[symbols[i]])
        i += 1

    i += 1  # skip space

    # Interpret: 2 letters = country, 4 letters = country + subdivision
    country = letters[0] + letters[1]
    subdivision = None
    if len(letters) == 4:
        subdivision = letters[2] + letters[3]

    auth = {"country": country, "subdivision": subdivision}
    return i, auth
~~~

# Worked Examples

## Example 1: Amateur Radio Callsign K7ABC/TT

**Input**:

* TYPE: 0 (radio callsign)
* Identifier: "K7ABC/TT"
* AUTH: None

**Symbol Sequence**:

~~~
K  7  A  B  C  /  T  T  END
20 7  10 11 12 39 29 29 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0000, A-KIND=00
001 0000 00 | 010100 000111 001010 001011 001100 100111 011101 011101 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=0, A-KIND=0
* Symbols: [20, 7, 10, 11, 12, 39, 29, 29, 63]

**Payload (hex)**: `20283945993BAEFE000000000000`

## Example 2: Aircraft Tail Number N9748C

**Input**:

* TYPE: 1 (aircraft tail)
* Identifier: "N9748C"
* AUTH: None

**Symbol Sequence**:

~~~
N  9  7  4  8  C  END
23 9  7  4  8  12 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0001, A-KIND=00
001 0001 00 | 010111 001001 000111 000100 001000 001100 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=1, A-KIND=0
* Symbols: [23, 9, 7, 4, 8, 12, 63]

**Payload (hex)**: `222E48E21067E00000000000000000`

## Example 3: Airport Code KSEA (ICAO)

**Input**:

* TYPE: 2 (airport)
* A-KIND: 00 (ICAO)
* Identifier: "KSEA"
* AUTH: None

**Symbol Sequence**:

~~~
K  S  E  A  END
20 28 14 10 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0010, A-KIND=00
001 0010 00 | 010100 011100 001110 001010 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=2, A-KIND=0
* Symbols: [20, 28, 14, 10, 63]

**Payload (hex)**: `2428E1C57E000000000000000000`

## Example 4: Airport Code SEA (IATA)

**Input**:

* TYPE: 2 (airport)
* A-KIND: 01 (IATA)
* Identifier: "SEA"
* AUTH: None

**Symbol Sequence**:

~~~
S  E  A  END
28 14 10 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0010, A-KIND=01
001 0010 01 | 011100 001110 001010 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=2, A-KIND=1
* Symbols: [28, 14, 10, 63]

**Payload (hex)**: `24B8715F80000000000000000000`

## Example 5: Airport Code 0S9 (Local, with AUTH)

**Input**:

* TYPE: 2 (airport)
* A-KIND: 10 (local)
* Identifier: "0S9"
* AUTH: "US"

**Symbol Sequence**:

~~~
AUTHUS(space) 0 S 9 END
62 30 28  36  0 28 9 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0010, A-KIND=10
001 0010 10 | 111110 011110 011100 100100 000000 011100 001001 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=2, A-KIND=2
* Symbols: [62, 30, 28, 36, 0, 28, 9, 63]

**Payload (hex)**: `257CF39200E13F80000000000000`

## Example 6: Vehicle License Plate ABC-1234 (USDC)

**Input**:

* TYPE: 3 (vehicle)
* Identifier: "ABC-1234"
* AUTH: "USDC"

**Symbol Sequence**:

~~~
AUTHUSDC(space) A B C - 1 2 3 4 END
62 30 28 13 12 36 10 11 12 38 1 2 3 4 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0011, A-KIND=00
001 0011 00 | 111110 011110 011100 001101 001100 100100 001010 001011 001100 100110 000001 000010 000011 000100 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=3, A-KIND=0
* Symbols: [62, 30, 28, 13, 12, 36, 10, 11, 12, 38, 1, 2, 3, 4, 63]

**Payload (hex)**: `267CF386992145993021062FC000`

## Example 7: Maidenhead Grid CG52WK/OP

**Input**:

* TYPE: 5 (Maidenhead)
* Identifier: "CG52WK/OP" (Pitcairn Island)
* AUTH: None

**Symbol Sequence**:

~~~
C  G  5  2  W  K  /  O  P  END
12 16 5  2  32 20 39 24 25 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0101, A-KIND=00
001 0101 00 | 001100 010000 000101 000010 100000 010100 100111 011000 011001 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=5, A-KIND=0
* Symbols: [12, 16, 5, 2, 32, 20, 39, 24, 25, 63]

**Payload (hex)**: `2A10282052727199FC000000000000`

## Example 8: Postal Code 20500 (US 5-digit ZIP, White House)

**Input**:

* TYPE: 7 (postcode)
* Identifier: "20500"
* AUTH: "US"

**Symbol Sequence**:

~~~
AUTHUS(space) 2 0 5 0 0 END
62 30 28  36  2 0 5 0 0 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0111, A-KIND=00
001 0111 00 | 111110 011110 011100 100100 000010 000000 000101 000000 000000 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=7, A-KIND=0
* Symbols: [62, 30, 28, 36, 2, 0, 5, 0, 0, 63]

**Payload (hex)**: `2E7CF392020014003F8000000000`

## Example 9: Postal Code 20500-0003 (US ZIP+4, White House)

**Input**:

* TYPE: 7 (postcode)
* Identifier: "20500-0003"
* AUTH: "US"

**Symbol Sequence**:

~~~
AUTHUS(space) 2 0 5 0 0 - 0 0 0 3 END
62 30 28  36  2 0 5 0 0 38 0 0 0 3 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0111, A-KIND=00
001 0111 00 | 111110 011110 011100 100100 000010 000000 000101 000000 000000 100110 000000 000000 000000 000011 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=7, A-KIND=0
* Symbols: [62, 30, 28, 36, 2, 0, 5, 0, 0, 38, 0, 0, 0, 3, 63]

**Payload (hex)**: `2E7CF3920200140098000000FF00`

## Example 10: Postal Code 20500-0003-16-0 (US ZIP+4+2+1, White House)

**Input**:

* TYPE: 7 (postcode)
* Identifier: "20500-0003-16-0"
* AUTH: "US"

**Note**: This identifier with AUTH prefix requires 20 symbols but the maximum is 17. Per {{symbol-stream-construction}}, the stream is truncated to 17 symbols (END omitted), encoding "US 20500-0003-16".

**Symbol Sequence** (truncated to 17):

~~~
AUTHUS(space) 2 0 5 0 0 - 0 0 0 3 - 1 6
62 30 28  36  2 0 5 0 0 38 0 0 0 3 38 1 6
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0111, A-KIND=00
001 0111 00 | 111110 011110 011100 100100 000010 000000 000101 000000 000000 100110 000000 000000 000000 000011 100110 000001 000110 | 0
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=7, A-KIND=0
* Symbols: [62, 30, 28, 36, 2, 0, 5, 0, 0, 38, 0, 0, 0, 3, 38, 1, 6]

**Payload (hex)**: `2E7CF39202001400980000030C18`

## Example 11: Postal Code SW1A 1AA (GB)

**Input**:

* TYPE: 7 (postcode)
* Identifier: "SW1A 1AA"
* AUTH: "GB"

**Symbol Sequence**:

~~~
AUTHGB(space) S W 1 A (space) 1 A A END
62 16 11  36 28 32 1 10   36  1 10 10 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0111, A-KIND=00
001 0111 00 | 111110 010000 001011 100100 011100 100000 000001 001010 100100 000001 001010 001010 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=7, A-KIND=0
* Symbols: [62, 16, 11, 36, 28, 32, 1, 10, 36, 1, 10, 10, 63]

**Payload (hex)**: `2E7C81723900254809457E000000`

## Example 12: Postal Code 20500 (USDC with subdivision, White House)

**Input**:

* TYPE: 7 (postcode)
* Identifier: "20500"
* AUTH: "USDC"

**Symbol Sequence**:

~~~
AUTHUSDC(space) 2 0 5 0 0 END
62 30 28 13 12 36 2 0 5 0 0 63
~~~

**Bit Layout**:

~~~
VERS=001, TYPE=0111, A-KIND=00
001 0111 00 | 111110 011110 011100 001101 001100 100100 000010 000000 000101 000000 000000 111111
~~~

**Decimal Values**:

* Header: VERS=1, TYPE=7, A-KIND=0
* Symbols: [62, 30, 28, 13, 12, 36, 2, 0, 5, 0, 0, 63]

**Payload (hex)**: `2E7CF38699240200140003F80000`

# Interoperability Considerations

## Version Negotiation

Implementations MUST check the VERS field before decoding. Addresses with VERS != `001` use different encoding profiles and MUST NOT be decoded using this specification.

Future specifications may define additional VERS values for:

* Alternative symbol alphabets
* Different payload structures
* Extended identifier types

## Reserved Values

Symbol values 47 and 49-61 are reserved for future use. Implementations encountering these values in VERS=001 addresses SHOULD:

* Treat the address as invalid
* Log a warning
* Decline to route or process the address

## Type Extensibility

TYPE values 8-15 are reserved. Future specifications may allocate these for additional identifier classes such as:

* ISIN (securities)
* ISBN (books)
* IMEI (mobile devices)
* MAC addresses

## Issuing Authority Prefix Interoperability

The AUTH prefix identifies the jurisdiction that assigned an identifier, using [ISO3166-1] alpha-2 country codes and [ISO3166-2] subdivision codes. Implementations SHOULD perform two levels of validation:

1. **Structural validation** (MUST): Verify the AUTH prefix is well-formed: it begins with the AUTH symbol (62), followed by exactly two or four uppercase letters, terminated by a space (36). Two letters represent a country code; four letters represent country plus subdivision. Addresses with structurally malformed AUTH prefixes (e.g., containing digits, odd number of letters, or missing terminating space) MUST be rejected.

2. **Registry validation** (OPTIONAL): Implementations MAY check whether the country or subdivision code exists in current ISO 3166-1/2 registries. However, implementations MUST NOT reject addresses solely due to unrecognized codes. Unrecognized but structurally valid codes (e.g., "XX" as a country code) MUST be passed through, allowing forward compatibility with future ISO assignments, private use, and experimental deployments.

### AUTH Prefix in Unexpected Identifier Types

Certain identifier types (TYPE=0, TYPE=1, TYPE=5) embed geographic context within the identifier itself and do not use AUTH prefixes. If a decoder encounters an AUTH symbol as the first symbol in the stream for these types, implementations SHOULD:

* Treat the address as malformed
* Log a warning indicating unexpected AUTH prefix for the identifier type
* Reject the address or, if lenient parsing is enabled, attempt to decode the AUTH prefix and remaining identifier while flagging the anomaly

Encoders MUST NOT emit AUTH prefixes for TYPE=0 (amateur radio callsign), TYPE=1 (aircraft tail number), or TYPE=5 (Maidenhead grid locator).

## Truncation Behavior

Identifiers longer than 17 symbols are truncated. When truncation occurs, the END symbol is omitted because all 17 symbol positions are occupied by identifier data.

**Detecting truncation during decoding**: Decoders observing exactly 17 symbols with no END symbol MAY infer that truncation occurred during encoding. However, this heuristic is not definitive: an identifier may naturally be exactly 17 symbols without truncation. Applications requiring reliable truncation detection SHOULD use out-of-band signaling or application-layer metadata.

Applications SHOULD:

* Warn users when truncation occurs during encoding
* Use TYPE=6 (generic) with abbreviated identifiers when full encoding is impossible
* Consider alternative encoding schemes for long identifiers

# IANA Considerations {#iana-considerations}

This document is published with Experimental status. As such, no IANA allocations are requested at this time.

## Experimental Deployment {#experimental-deployment}

For experimental and testing purposes, implementations SHOULD use one of the following approaches:

1. **Documentation Prefix**: Use an address block within the IPv6 documentation prefix 2001:db8::/32 {{RFC3849}}, such as 2001:db8:ham6::/48. This prefix is reserved for documentation and example code and will not conflict with production networks. Implementations SHOULD use this prefix for all test vectors, unit tests, and example code. The recommended testing prefix is:

   * **2001:db8:6464::/48** - Suggested prefix for Ham64 testing ("6464" encodes "HAM" in the symbol stream for easy identification)

2. **Unique Local Addresses (ULA)**: Use a /48 or smaller block within the fc00::/7 ULA space. Implementers should generate a pseudo-random /48 per {{RFC4193}} to minimize collision risk in private deployments.

3. **Site-Local Experimentation**: Coordinate with local network administrators to allocate a suitable prefix for testing within existing address allocations.

## Future IANA Actions

Should this specification advance beyond Experimental status, the following IANA actions would be required:

### IPv6 Special-Purpose Address Registry

A /16 prefix from the IPv6 Special-Purpose Address Registry {{RFC6890}} for Ham64-encoded identifiers with the following properties:

* Name: Ham64 Human Identifier Encoding
* Source: True
* Destination: True
* Forwardable: True
* Global: True
* Reserved-by-Protocol: False

Note: While "Global: True" indicates these addresses are technically valid for global routing, operators SHOULD carefully consider the privacy implications discussed in {{privacy}} before enabling global reachability. In practice, many deployments will restrict these addresses to specific network segments or overlay networks where the embedded identifiers serve operational purposes and the privacy trade-offs are acceptable.

### Ham64 Identifier Type Registry

A new registry titled "Ham64 IPv6 Identifier Types" under the "Internet Protocol Version 6 (IPv6) Parameters" group would define the TYPE field values (0-15).

### Ham64 Symbol Alphabet Registry

A new registry titled "Ham64 Symbol Alphabet" would define the 6-bit symbol values for each encoding version (VERS field).

These registries would require an appropriate registration procedure (likely "IETF Review" or "Standards Action") to be determined during any future standards-track progression.

# Security Considerations

## Privacy {#privacy}

Embedding human-readable identifiers in IPv6 addresses creates privacy risks:

* **Tracking**: Addresses reveal identity, enabling correlation across networks and time.
* **Enumeration**: Attackers can scan address space to discover active identifiers.
* **Inference**: Identifier patterns may reveal location, organization, or activity.

Mitigations:

* Use temporary addresses {{RFC4941}} for privacy-sensitive applications
* Deploy firewall rules to limit external visibility
* Educate users about identifier exposure risks

## Spoofing

Addresses can be forged, enabling impersonation attacks:

* An attacker may claim another entity's callsign, tail number, or license plate
* Routing or filtering based solely on embedded identifiers is insecure

Mitigations:

* Use cryptographic authentication (IPsec {{RFC4301}}, TLS {{RFC8446}}) for identity verification
* Treat embedded identifiers as hints, not authoritative identity
* Implement out-of-band verification for high-assurance scenarios

## Denial of Service

Attackers may generate large numbers of addresses with valid-looking identifiers to:

* Exhaust routing tables
* Trigger expensive lookups or logging
* Flood monitoring systems

Mitigations:

* Rate-limit address generation and registration
* Use stateless filtering where possible
* Monitor for anomalous address patterns

## Regulatory and Legal

Embedding identifiers may have legal implications:

* **Amateur radio**: Callsign use is regulated; unauthorized use may violate national law
* **Aircraft**: Tail number misuse may violate aviation regulations
* **Vehicles**: License plate cloning is illegal in most jurisdictions

Implementations SHOULD include warnings about legal responsibilities.

## Validation

Implementations MUST validate:

* VERS field matches expected value
* TYPE field is within allocated range
* Reserved symbol values are not present
* AUTH prefix format is correct

Invalid addresses SHOULD be rejected or logged.

# Test Vectors

The following test vectors provide complete encodings for verification.

**Byte order convention**: All hexadecimal payload values are shown in network byte order (big-endian), with the most significant byte first. This matches the standard representation of IPv6 addresses. For example, a payload hex value of `20283945...` represents byte 0 = 0x20, byte 1 = 0x28, byte 2 = 0x39, and so on.

**Complete IPv6 addresses**: Each test vector includes a complete IPv6 address using the documentation prefix `2001:db8:6464::/48` (see {{experimental-deployment}}). The full address combines the /48 prefix with the 80-bit suffix derived from the payload. Production deployments would substitute an IANA-allocated or operator-assigned prefix.

## Test Vector 1: K7ABC/TT

* **Type**: 0 (radio callsign)
* **Identifier**: "K7ABC/TT"
* **AUTH**: None
* **VERS**: 001
* **TYPE**: 0000
* **A-KIND**: 00
* **Symbols**: [20, 7, 10, 11, 12, 39, 29, 29, 63]
* **Payload (hex)**: `20283945993BAEFE000000000000`
* **Full IPv6**: `2001:db8:6464:2028:3945:993b:aefe:0`

## Test Vector 2: N9748C

* **Type**: 1 (aircraft tail)
* **Identifier**: "N9748C"
* **AUTH**: None
* **VERS**: 001
* **TYPE**: 0001
* **A-KIND**: 00
* **Symbols**: [23, 9, 7, 4, 8, 12, 63]
* **Payload (hex)**: `222E48E21067E00000000000000000`
* **Full IPv6**: `2001:db8:6464:222e:48e2:1067:e000:0`

## Test Vector 3: KSEA

* **Type**: 2 (airport, ICAO)
* **Identifier**: "KSEA"
* **AUTH**: None
* **VERS**: 001
* **TYPE**: 0010
* **A-KIND**: 00
* **Symbols**: [20, 28, 14, 10, 63]
* **Payload (hex)**: `2428E1C57E000000000000000000`
* **Full IPv6**: `2001:db8:6464:2428:e1c5:7e00:0:0`

## Test Vector 4: SEA

* **Type**: 2 (airport, IATA)
* **Identifier**: "SEA"
* **AUTH**: None
* **VERS**: 001
* **TYPE**: 0010
* **A-KIND**: 01
* **Symbols**: [28, 14, 10, 63]
* **Payload (hex)**: `24B8715F80000000000000000000`
* **Full IPv6**: `2001:db8:6464:24b8:715f:8000:0:0`

## Test Vector 5: 0S9 (US)

* **Type**: 2 (airport, local)
* **Identifier**: "0S9"
* **AUTH**: "US"
* **VERS**: 001
* **TYPE**: 0010
* **A-KIND**: 10
* **Symbols**: [62, 30, 28, 36, 0, 28, 9, 63]
* **Payload (hex)**: `257CF39200E13F80000000000000`
* **Full IPv6**: `2001:db8:6464:257c:f392:00e1:3f80:0`

## Test Vector 6: ABC-1234 (USDC)

* **Type**: 3 (vehicle)
* **Identifier**: "ABC-1234"
* **AUTH**: "USDC"
* **VERS**: 001
* **TYPE**: 0011
* **A-KIND**: 00
* **Symbols**: [62, 30, 28, 13, 12, 36, 10, 11, 12, 38, 1, 2, 3, 4, 63]
* **Payload (hex)**: `267CF386992145993021062FC000`
* **Full IPv6**: `2001:db8:6464:267c:f386:9921:4599:3021`

## Test Vector 7: CN87UM/OP

* **Type**: 5 (Maidenhead)
* **Identifier**: "CN87UM/OP"
* **AUTH**: None
* **VERS**: 001
* **TYPE**: 0101
* **A-KIND**: 00
* **Symbols**: [12, 23, 8, 7, 30, 22, 39, 24, 25, 63]
* **Payload (hex)**: `2A18B903BCB4EC33F8000000000000`
* **Full IPv6**: `2001:db8:6464:2a18:b903:bcb4:ec33:f800`

## Test Vector 8: 20500 (US 5-digit ZIP, White House)

* **Type**: 7 (postcode)
* **Identifier**: "20500"
* **AUTH**: "US"
* **VERS**: 001
* **TYPE**: 0111
* **A-KIND**: 00
* **Symbols**: [62, 30, 28, 36, 2, 0, 5, 0, 0, 63]
* **Payload (hex)**: `2E7CF392020014003F8000000000`

## Test Vector 9: 20500-0003 (US ZIP+4, White House)

* **Type**: 7 (postcode)
* **Identifier**: "20500-0003"
* **AUTH**: "US"
* **VERS**: 001
* **TYPE**: 0111
* **A-KIND**: 00
* **Symbols**: [62, 30, 28, 36, 2, 0, 5, 0, 0, 38, 0, 0, 0, 3, 63]
* **Payload (hex)**: `2E7CF3920200140098000000FF00`

## Test Vector 10: 20500-0003-16-0 (US ZIP+4+2+1, White House)

* **Type**: 7 (postcode)
* **Identifier**: "20500-0003-16-0"
* **AUTH**: "US"
* **VERS**: 001
* **TYPE**: 0111
* **A-KIND**: 00
* **Symbols**: [62, 30, 28, 36, 2, 0, 5, 0, 0, 38, 0, 0, 0, 3, 38, 1, 6] (truncated to 17)
* **Payload (hex)**: `2E7CF39202001400980000030C18`

## Test Vector 11: SW1A 1AA (GB)

* **Type**: 7 (postcode)
* **Identifier**: "SW1A 1AA"
* **AUTH**: "GB"
* **VERS**: 001
* **TYPE**: 0111
* **A-KIND**: 00
* **Symbols**: [62, 16, 11, 36, 28, 32, 1, 10, 36, 1, 10, 10, 63]
* **Payload (hex)**: `2E7C81723900254809457E000000`

## Test Vector 12: 20500 (USDC with subdivision, White House)

* **Type**: 7 (postcode)
* **Identifier**: "20500"
* **AUTH**: "USDC"
* **VERS**: 001
* **TYPE**: 0111
* **A-KIND**: 00
* **Symbols**: [62, 30, 28, 13, 12, 36, 2, 0, 5, 0, 0, 63]
* **Payload (hex)**: `2E7CF38699240200140003F80000`

# ABNF Syntax

The following ABNF {{RFC5234}} defines the text syntax for identifiers before encoding:

~~~
identifier = callsign / tail-number / airport-code / 
             vehicle-plate / boat-hin / maidenhead / 
             generic-id / postcode

callsign = 1*6(ALPHA / DIGIT) ["/" suffix]
suffix = 1*4(ALPHA / DIGIT)

tail-number = 1*10(ALPHA / DIGIT / "-")

airport-code = icao-code / iata-code / local-code
icao-code = 4ALPHA
iata-code = 3ALPHA
local-code = 1*6(ALPHA / DIGIT)

vehicle-plate = 1*12(ALPHA / DIGIT / "-" / SP)

boat-hin = 12(ALPHA / DIGIT)

maidenhead = 2ALPHA 2DIGIT [2ALPHA [2DIGIT [2ALPHA]]] ["/" suffix]

generic-id = 1*17ham64-char

postcode = 1*12(ALPHA / DIGIT / SP / "-")

ham64-char = DIGIT / ALPHA / SP / "." / "-" / "/" / 
             "&" / "@" / "!" / "_" / ":" / "," / "+" / "?"

ALPHA = %x41-5A  ; A-Z (uppercase)
DIGIT = %x30-39  ; 0-9
SP = %x20        ; space
~~~

# Backward Compatibility

This specification defines a new encoding system with no backward compatibility requirements. However, implementations should consider:

## Coexistence with Standard IPv6

Ham64-encoded addresses are valid IPv6 addresses {{RFC8200}} and MUST be processed by standard IPv6 stacks. Routers and switches that do not recognize the special-use prefix will forward these addresses normally.

## Application Layer

Applications unaware of Ham64 encoding will treat these as opaque IPv6 addresses. This is acceptable and expected behavior.

## DNS

Ham64-encoded addresses MAY be registered in DNS {{RFC3596}}. Reverse DNS (ip6.arpa) MAY include identifier information in PTR records for human readability.

## Transition

No transition mechanism is required. Ham64 encoding is deployed incrementally as applications adopt it.

# Acknowledgments

The author thanks the amateur radio, aviation, and maritime communities for inspiration and feedback on identifier encoding requirements. Thanks also to the IETF community for guidance on IPv6 address structure and special-use prefix allocation.

--- back

# Implementation Notes

This appendix provides non-normative guidance for implementers.

## Efficient Symbol Lookup

Implementations may use lookup tables for O(1) character-to-value and value-to-character conversion:

~~~
HAM64_ENCODE = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14,
    'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19,
    'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24,
    'P': 25, 'Q': 26, 'R': 27, 'S': 28, 'T': 29,
    'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34,
    'Z': 35, ' ': 36, '.': 37, '-': 38, '/': 39,
    '&': 40, '@': 41, '!': 42, '_': 43, ':': 44,
    ',': 45, '+': 46, '?': 48
}

HAM64_DECODE = {v: k for k, v in HAM64_ENCODE.items()}
HAM64_DECODE[62] = 'AUTH'
HAM64_DECODE[63] = 'END'
~~~

## Validation Checklist

Before encoding, verify:

1. All characters are in Ham64 alphabet
2. Identifier length is reasonable for type
3. AUTH prefix is present when required
4. TYPE and A-KIND values are valid

After decoding, verify:

1. VERS == 001
2. TYPE is allocated (0-7)
3. No reserved symbol values present
4. AUTH prefix format is correct
5. END symbol appears before bit 103 or is omitted

## Performance Considerations

Encoding and decoding are computationally inexpensive (bit shifts and table lookups). Typical implementations should process thousands of addresses per second on modern hardware.

## Amateur Radio IPv6 Integration

Ham64 encoding offers potential integration with amateur radio IPv6 networking. Amateur radio operators have historically used various methods to derive IPv6 addresses for packet radio and mesh networking. Ham64 provides a standardized approach where an operator's callsign directly determines their IPv6 address.

Potential applications include:

* **AREDN/HamNet mesh networks**: Nodes could derive addresses from callsigns, enabling intuitive routing based on operator identity
* **AX.25 over IPv6**: Bridge legacy packet radio networks using callsign-derived addressing
* **Digital voice (D-STAR, DMR, System Fusion)**: Use Ham64 addresses for reflector and gateway identification
* **APRS-IS integration**: Map APRS stations to IPv6 addresses for bidirectional IP connectivity

Implementers exploring amateur radio integration should note that some amateur radio regulatory environments restrict the types of traffic permitted. Encryption may be prohibited in certain jurisdictions. Consult local regulations before deploying Ham64-addressed networks for amateur radio use.

## Example Implementation

A reference implementation in Python is available at:

https://github.com/example/ham64-ipv6

(Note: This is a placeholder; actual implementation would be developed separately.)

# Change Log

## draft-atwood-ham64-00

Initial version:

* Defined Ham64 symbol table with AUTH=62 and END=63
* AUTH prefix identifies "issuing authority" (jurisdiction that assigned identifier), not geographic location
* AUTH format: `AUTHCC(space)` or `AUTHCCSS(space)` - AUTH immediately followed by letters, space terminates
* Defined identifier types 0-7 including postal codes (TYPE=7) with mandatory AUTH
* Included worked examples for all identifier types
* Added complete test vectors with hexadecimal payloads
* Defined A-KIND usage for airport codes
* Added ABNF syntax definitions
* Included security considerations
* Provided pseudocode for encoding and decoding
* Defined local extension pattern with slash-suffix for all identifier types
* Covered US postal code formats including 5-digit, ZIP+4, and ZIP+4+2+1
* Added normative references to ISO 3166-1 and ISO 3166-2 for issuing authority codes

