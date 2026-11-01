"""Decoder for YZ2, the compression two RE4UHD room archives hold their DAT
block in (see fs.py).

YZ2 is not a Capcom format: it is yz2, YAMAZAKI Satoshi's 2002 open source
compressor, which the game's tools used as-is. A block opens with a 32-byte
ASCII header, "<compressed size hex>\\t<decompressed size hex>\\n" zero
padded, and the rest is yz2's own stream: an LZ77 variant whose matches are
addressed through per-byte dictionaries rather than by distance, with every
symbol range coded against an adaptive frequency table.

Ported from yz2's C++ source as JADERLINK's RE4_DASYZ2_TOOL ships it
(https://github.com/JADERLINK/RE4_DASYZ2_TOOL, YZ2_TOOLS/YZ2/yz2Code), which
decodes these same blocks. Only the decoder is ported, and only the mode the
game uses (yz2's optional PPM model is off). Behaviour is kept bit for bit,
quirks included: the coder works in 32-bit words, and a dictionary entry
records the length of the token that closed it, not of the string it points
at. Both decide what later symbols mean, so "fixing" either would garble the
output.

yz2 carries this notice, which applies to the code below as a port of it:

    Copyright(c) YAMAZAKI Satoshi 2002. All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

    Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
    OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
    SUCH DAMAGE.

Pure Python, like the LZX decoder: about a second per megabyte of output.
"""
import re
from bisect import bisect_right
from itertools import accumulate

YZ2_HEADER_SIZE = 32
YZ2_HEADER_PATTERN = re.compile(rb"^([0-9a-f]+)\t([0-9a-f]+)\n\x00*$")

# Range coder precision: frequency tables always sum to 1 << RANGE_BITS.
RANGE_BITS = 15
RANGE_TOTAL = 1 << RANGE_BITS
WORD_MASK = 0xFFFFFFFF
# The coder takes in another byte whenever its width drops to this.
RANGE_REFILL = 0x80000000 >> 8

# Each first byte ("key") gets a ring of this many earlier strings that
# followed it, and a match names one by its position in the ring.
DICTIONARY_SIZE = 512
# Symbols of the main table: below DICTIONARY_SIZE a match with an explicit
# length, below LITERAL_BASE a match reusing the length the ring recorded,
# and from there on a literal byte.
LITERAL_BASE = DICTIONARY_SIZE * 2
CODE_SYMBOLS = LITERAL_BASE + 256
LENGTH_SYMBOLS = 256


def parse_header(block):
    """(compressed size, decompressed size) from a YZ2 block's header, or
    None when `block` does not open with one."""
    match = YZ2_HEADER_PATTERN.match(bytes(block[:YZ2_HEADER_SIZE]))
    if match is None:
        return None
    return int(match.group(1), 16), int(match.group(2), 16)


class _FrequencyTable:
    """yz2's adaptive model (Frequency4Tbl): per-symbol counts, and the
    ranges the coder reads against, which are only recomputed at set points.

    Until the counts sum to RANGE_TOTAL, the ranges are redrawn from them
    (scaled up) each time the sum reaches the next power of two. After that,
    they are redrawn whenever the sum reaches RANGE_TOTAL again, and the
    counts are halved to make room. In between, symbols are counted but the
    ranges stay as they were.
    """

    def __init__(self, size):
        # The ranges used before anything is counted: RANGE_TOTAL dealt out
        # round robin, which is not the same as the counts it starts from.
        base, extra = divmod(RANGE_TOTAL, size)
        self._set_ranges([base + 1] * extra + [base] * (size - extra))
        self.counts = [1] * size
        self.total = size
        self.bits = 0
        while self.bits < RANGE_BITS and self.total >= 1 << self.bits:
            self.bits += 1

    def _set_ranges(self, widths):
        self.widths = widths
        self.lows = [0, *accumulate(widths)][:-1]

    def count(self, symbol):
        self.counts[symbol] += 1
        self.total += 1
        if self.bits < RANGE_BITS:
            if self.total == 1 << self.bits:
                scale = 1 << (RANGE_BITS - self.bits)
                self._set_ranges([count * scale for count in self.counts])
                self.bits += 1
        elif self.total >= RANGE_TOTAL:
            self._set_ranges(self.counts)
            self.counts = [count >> 1 or 1 for count in self.counts]
            self.total = sum(self.counts)


def decompress(block):
    """The decompressed bytes of a whole YZ2 block, header included.

    Raises ValueError for a block without a YZ2 header, or whose stream
    refers outside the output, which is what corrupt input comes out as.
    """
    sizes = parse_header(block)
    if sizes is None:
        raise ValueError("not a YZ2 block: no '<hex>\\t<hex>\\n' header")
    compressed_size, out_size = sizes
    data = bytes(block[YZ2_HEADER_SIZE:YZ2_HEADER_SIZE + compressed_size])
    data_size = len(data)

    codes = _FrequencyTable(CODE_SYMBOLS)
    lengths = _FrequencyTable(LENGTH_SYMBOLS)

    # Range decoder state. Reading past the end of the input yields zeros,
    # as yz2's input buffer does.
    width = 1 << 7
    low = data[0] if data else 0
    read = 1

    def decode_symbol(table):
        nonlocal width, low, read
        while width <= RANGE_REFILL:
            low = ((low << 8) | (data[read] if read < data_size else 0)) & WORD_MASK
            width = (width << 8) & WORD_MASK
            read += 1
        width >>= RANGE_BITS - 1
        point = low // width
        if point >= RANGE_TOTAL:
            raise ValueError("YZ2 stream is corrupt: range decoder out of bounds")
        symbol = bisect_right(table.lows, point) - 1
        low = (low - width * table.lows[symbol]) & WORD_MASK
        width = ((width * table.widths[symbol]) & WORD_MASK) >> 1
        table.count(symbol)
        return symbol

    def decode_length():
        # 3 and up is the length itself (minus 3); 0, 1 and 2 escape to a
        # big-endian value in the next 4, 3 or 2 symbols.
        length = decode_symbol(lengths)
        if length < 3:
            value = 0
            for _ in range(4 - length):
                value = (value << 8) | decode_symbol(lengths)
            length = value
        return length - 3

    out = bytearray(out_size)
    # Per key: the ring of (output offset, length) entries, and where the
    # next one goes. Offsets stand in for yz2's pointers into the output.
    ring_offsets = [[None] * DICTIONARY_SIZE for _ in range(256)]
    ring_lengths = [[0] * DICTIONARY_SIZE for _ in range(256)]
    ring_next = [0] * 256

    pos = 0
    # The byte whose ring the next match is looked up in, and the next string
    # registered under: the last byte of the previous token.
    key_pos = 0
    while pos < out_size:
        code = decode_symbol(codes)
        size = 1
        if code >= LITERAL_BASE:
            out[pos] = code - LITERAL_BASE
            pos += 1
        else:
            key = out[key_pos]
            slot = (code + ring_next[key]) % DICTIONARY_SIZE
            if code < DICTIONARY_SIZE:
                size = decode_length() + 2
            else:
                size = ring_lengths[key][slot]
            source = ring_offsets[key][slot]
            if pos + size > out_size:
                raise ValueError("YZ2 stream is corrupt: a match runs past the output")
            if source is None or source >= out_size:
                raise ValueError("YZ2 stream is corrupt: a match refers to nothing")
            if source + size <= pos:
                out[pos:pos + size] = out[source:source + size]
            else:
                # Overlapping its own output, which a byte-wise copy repeats.
                for i in range(size):
                    out[pos + i] = out[source + i]
            pos += size

        if key_pos < pos - 1:
            key = out[key_pos]
            slot = ring_next[key]
            ring_offsets[key][slot] = key_pos + 1
            ring_lengths[key][slot] = size
            ring_next[key] = (slot + 1) % DICTIONARY_SIZE
            key_pos = pos - 1
    return bytes(out)
