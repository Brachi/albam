"""
Pure-Python LZX / LFS decompressor for RE4 UHD
Drop-in replacement for xcompress.py - no DLL dependency.
Based on lfs_decompress.h by kreed
"""

import struct

# LZX constants
LZX_MIN_MATCH = 2
LZX_NUM_CHARS = 256
LZX_NUM_SECONDARY_LENGTHS = 249
LZX_BLOCKTYPE_VERBATIM = 1
LZX_BLOCKTYPE_ALIGNED = 2
LZX_BLOCKTYPE_UNCOMPRESSED = 3
LZX_LEAF_MARKER = 0x7FFFFFFF
LZX_MAX_NODES = 4096

EXTRA_BITS = [
    0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10,
    11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17,
]
POSITION_BASE = [
    0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512,
    768, 1024, 1536, 2048, 3072, 4096, 6144, 8192, 12288, 16384, 24576, 32768,
    49152, 65536, 98304, 131072, 196608, 262144, 393216, 524288, 655360, 786432,
    917504, 1048576, 1179648, 1310720, 1441792, 1572864, 1703936, 1835008,
    1966080, 2097152, 2228224,
]

LFS_MAGIC1 = 0x584C4452
LFS_CHUNK_SIZE = 0x10000


class _BitReader:
    __slots__ = ("data", "sz", "pos", "buf", "bl")

    def __init__(self, data, offset, size):
        self.data = data
        self.sz = offset + size
        self.pos = offset
        self.buf = 0
        self.bl = 0

    def read(self, n):
        if n == 0:
            return 0
        while self.bl < n:
            if self.pos + 1 < self.sz:
                w = self.data[self.pos] | (self.data[self.pos + 1] << 8)
                self.pos += 2
                self.buf = ((self.buf << 16) | w) & 0xFFFFFFFF
                self.bl += 16
            elif self.pos < self.sz:
                self.buf = ((self.buf << 8) | self.data[self.pos]) & 0xFFFFFFFF
                self.pos += 1
                self.bl += 8
            else:
                break
        v = (self.buf >> (self.bl - n)) & ((1 << n) - 1)
        self.bl -= n
        return v


def _build_tree(lens, num_symbols):
    """Build a canonical Huffman tree. Returns list of (child0, child1) nodes."""
    tree = [[0, 0]]  # node 0 = root
    counts = [0] * 17
    starts = [0] * 17

    for i in range(num_symbols):
        if 0 < lens[i] <= 16:
            counts[lens[i]] += 1

    starts[1] = 0
    for i in range(1, 16):
        starts[i + 1] = (starts[i] + counts[i]) << 1

    for sym in range(num_symbols):
        length = lens[sym]
        if length <= 0 or length > 16:
            continue
        code = starts[length]
        starts[length] += 1
        if code >= (1 << length):
            return None

        node = 0
        for i in range(length - 1, -1, -1):
            bit = (code >> i) & 1
            if i == 0:
                if len(tree) >= LZX_MAX_NODES:
                    return None
                leaf_idx = len(tree)
                tree.append([sym, LZX_LEAF_MARKER])
                tree[node][bit] = leaf_idx
            else:
                child = tree[node][bit]
                if child == 0:
                    if len(tree) >= LZX_MAX_NODES:
                        return None
                    child = len(tree)
                    tree.append([0, 0])
                    tree[node][bit] = child
                node = child
    return tree


def _huffman_decode(br, tree):
    """Decode one Huffman symbol."""
    node = 0
    for _ in range(32):
        bit = br.read(1)
        if node >= len(tree):
            return -1
        child = tree[node][bit]
        if child == 0 or child >= len(tree):
            return -1
        if tree[child][1] == LZX_LEAF_MARKER:
            return tree[child][0]
        node = child
    return -1


def _read_lengths(br, lens, first, last, pt_work_lens):
    """Read Huffman code lengths using a pre-tree."""
    pt_lens = [0] * 20
    for i in range(20):
        pt_lens[i] = br.read(4)
    pt_tree = _build_tree(pt_lens, 20)
    if pt_tree is None:
        return False

    x = first
    while x < last:
        z = _huffman_decode(br, pt_tree)
        if z < 0:
            return False
        if z == 17:
            run = br.read(4) + 4
            for _ in range(run):
                if x >= last:
                    break
                lens[x] = 0
                x += 1
        elif z == 18:
            run = br.read(5) + 20
            for _ in range(run):
                if x >= last:
                    break
                lens[x] = 0
                x += 1
        elif z == 19:
            run = br.read(1) + 4
            delta = _huffman_decode(br, pt_tree)
            if delta < 0:
                return False
            d = (lens[x] - delta) % 17
            for _ in range(run):
                if x >= last:
                    break
                lens[x] = d
                x += 1
        else:
            d = (lens[x] - z) % 17
            lens[x] = d
            x += 1
    return True


def _apply_e8(data, offset, size, filesize):
    """Apply E8 (x86 CALL) transform."""
    if size <= 10:
        return
    end = size - 10
    i = 0
    while i < end:
        if data[offset + i] == 0xE8:
            abs_off = (data[offset + i + 1] | (data[offset + i + 2] << 8) |
                       (data[offset + i + 3] << 16) | (data[offset + i + 4] << 24))
            abs_off &= 0xFFFFFFFF
            if abs_off < filesize:
                rel_off = (abs_off - (offset + i)) & 0xFFFFFFFF
            elif abs_off >= 0x80000000 and abs_off < 0x80000000 + filesize:
                rel_off = (abs_off + filesize) & 0xFFFFFFFF
            else:
                i += 1
                continue
            data[offset + i + 1] = rel_off & 0xFF
            data[offset + i + 2] = (rel_off >> 8) & 0xFF
            data[offset + i + 3] = (rel_off >> 16) & 0xFF
            data[offset + i + 4] = (rel_off >> 24) & 0xFF
            i += 5
        else:
            i += 1


class _LzxState:
    __slots__ = ("win_sz", "wmask", "window", "num_off",
                 "R0", "R1", "R2", "block_rem", "block_type", "block_len",
                 "header_read", "win_pos", "frame",
                 "MT_len", "LEN_len", "AL_len",
                 "mt_tree", "lt_tree", "al_tree",
                 "LEN_empty", "intel_filesize", "intel_active", "intel_offset",
                 "out", "out_pos", "out_sz")

    def __init__(self, window_size):
        self.win_sz = window_size
        self.wmask = window_size - 1
        self.window = bytearray(window_size)
        self.num_off = 34
        self.MT_len = [0] * 720
        self.LEN_len = [0] * 320
        self.AL_len = [0] * 12
        self.mt_tree = None
        self.lt_tree = None
        self.al_tree = None
        self.LEN_empty = True
        self.R0 = self.R1 = self.R2 = 1
        self.block_rem = self.block_type = self.block_len = 0
        self.header_read = 0
        self.win_pos = self.frame = 0
        self.intel_filesize = 0x00FFFFFF
        self.intel_active = 0
        self.intel_offset = 0
        self.out = None
        self.out_pos = 0
        self.out_sz = 0


def _lzx_decode_frame(st, br, uncomp_sz):
    R0, R1, R2 = st.R0, st.R1, st.R2
    wp = st.win_pos
    wm = st.wmask
    window = st.window
    out = st.out
    frame_start = st.out_pos
    target = min(st.out_pos + uncomp_sz, st.out_sz)

    if st.header_read:
        if br.read(1):
            hi = br.read(16)
            lo = br.read(16)
            st.intel_filesize = (hi << 16) | lo
            st.intel_active = 1
        st.header_read = 0

    while st.out_pos < target:
        if st.block_rem == 0:
            st.block_type = br.read(3)
            st.block_rem = st.block_len = br.read(24)
            if st.block_type < 1 or st.block_type > 3:
                return -1

            if st.block_type == LZX_BLOCKTYPE_ALIGNED:
                for i in range(8):
                    st.AL_len[i] = br.read(3)
                st.al_tree = _build_tree(st.AL_len, 8)
                if st.al_tree is None:
                    return -1
                # fall through to VERBATIM
                if not _read_lengths(br, st.MT_len, 0, 256, None):
                    return -1
                if not _read_lengths(br, st.MT_len, 256, 256 + st.num_off * 8, None):
                    return -1
                st.mt_tree = _build_tree(st.MT_len, 256 + st.num_off * 8)
                if st.mt_tree is None:
                    return -1
                if not _read_lengths(br, st.LEN_len, 0, LZX_NUM_SECONDARY_LENGTHS, None):
                    return -1
                st.lt_tree = _build_tree(st.LEN_len, LZX_NUM_SECONDARY_LENGTHS)
                st.LEN_empty = st.lt_tree is None

            elif st.block_type == LZX_BLOCKTYPE_VERBATIM:
                if not _read_lengths(br, st.MT_len, 0, 256, None):
                    return -1
                if not _read_lengths(br, st.MT_len, 256, 256 + st.num_off * 8, None):
                    return -1
                st.mt_tree = _build_tree(st.MT_len, 256 + st.num_off * 8)
                if st.mt_tree is None:
                    return -1
                if not _read_lengths(br, st.LEN_len, 0, LZX_NUM_SECONDARY_LENGTHS, None):
                    return -1
                st.lt_tree = _build_tree(st.LEN_len, LZX_NUM_SECONDARY_LENGTHS)
                st.LEN_empty = st.lt_tree is None
                st.AL_len = [0] * 12
                st.al_tree = _build_tree(st.AL_len, 8)

            elif st.block_type == LZX_BLOCKTYPE_UNCOMPRESSED:
                if br.bl & 15:
                    br.read(br.bl & 15)
                R0 = br.read(16) | (br.read(16) << 16)
                R1 = br.read(16) | (br.read(16) << 16)
                R2 = br.read(16) | (br.read(16) << 16)

        if st.block_type == LZX_BLOCKTYPE_UNCOMPRESSED:
            if br.bl == 16:
                c = br.buf & 0xFF
                br.buf >>= 8
                br.bl -= 8
            elif br.bl == 8:
                c = br.buf & 0xFF
                br.buf = 0
                br.bl = 0
            else:
                if br.pos >= br.sz:
                    return -1
                c = br.data[br.pos]
                br.pos += 1
            window[wp] = c
            wp = (wp + 1) & wm
            out[st.out_pos] = c
            st.out_pos += 1
            st.block_rem -= 1
            if st.block_rem == 0:
                if br.bl & 15:
                    br.bl = 0
                    br.buf = 0
                if br.pos & 1:
                    br.pos += 1
        else:
            me = _huffman_decode(br, st.mt_tree)
            if me < 0:
                return -1
            if me < LZX_NUM_CHARS:
                window[wp] = me
                wp = (wp + 1) & wm
                out[st.out_pos] = me
                st.out_pos += 1
                st.block_rem -= 1
            else:
                me -= LZX_NUM_CHARS
                ml = me & 7
                if ml == 7:
                    if st.LEN_empty:
                        return -1
                    ex = _huffman_decode(br, st.lt_tree)
                    if ex < 0:
                        return -1
                    ml += ex
                ml += LZX_MIN_MATCH

                slot = me >> 3
                if slot == 0:
                    mo = R0
                elif slot == 1:
                    mo = R1
                    R1 = R0
                    R0 = mo
                elif slot == 2:
                    mo = R2
                    R2 = R0
                    R0 = mo
                else:
                    ex_bits = 17 if slot >= 50 else EXTRA_BITS[slot]
                    mo = POSITION_BASE[slot] - 2
                    if ex_bits >= 3 and st.block_type == LZX_BLOCKTYPE_ALIGNED:
                        if ex_bits > 3:
                            mo += br.read(ex_bits - 3) << 3
                        aligned_sym = _huffman_decode(br, st.al_tree)
                        if aligned_sym < 0:
                            return -1
                        mo += aligned_sym
                    elif ex_bits > 0:
                        mo += br.read(ex_bits)
                    R2 = R1
                    R1 = R0
                    R0 = mo

                while ml > 0 and st.out_pos < target:
                    c = window[(wp - mo) & wm]
                    window[wp] = c
                    wp = (wp + 1) & wm
                    out[st.out_pos] = c
                    st.out_pos += 1
                    st.block_rem -= 1
                    ml -= 1

    if st.intel_active and st.out_pos > frame_start:
        _apply_e8(out, frame_start, st.out_pos - frame_start, st.intel_filesize)

    st.intel_offset += st.out_pos - frame_start
    st.win_pos = wp
    st.R0 = R0
    st.R1 = R1
    st.R2 = R2
    return 0


def _lzx_inflate(st, data, offset, comp_size, out, out_offset, decomp_size):
    """Decompress one LZX stream into out[out_offset:]."""
    st.out = out
    st.out_sz = out_offset + decomp_size
    st.out_pos = out_offset
    st.header_read = 1
    st.intel_active = 0
    st.intel_offset = 0
    st.MT_len = [0] * 720
    st.LEN_len = [0] * 320
    st.AL_len = [0] * 12
    st.R0 = st.R1 = st.R2 = 1

    ip = offset
    end = offset + comp_size
    while ip < end and st.out_pos < st.out_sz:
        if data[ip] == 0xFF:
            if ip + 5 > end:
                break
            us = (data[ip + 1] << 8) | data[ip + 2]
            cs = (data[ip + 3] << 8) | data[ip + 4]
            ip += 5
        else:
            if ip + 2 > end:
                break
            us = 32768
            cs = (data[ip] << 8) | data[ip + 1]
            ip += 2
        if cs == 0 or ip + cs > end:
            break
        br = _BitReader(data, ip, cs)
        if _lzx_decode_frame(st, br, us) < 0:
            raise RuntimeError("LZX decompression failed")
        ip += cs

    return st.out_pos - out_offset


# ============================================================================
# LFS public API — drop-in replacement for xcompress.py
# ============================================================================

def is_lfs(data):
    """Check if data starts with the LFS magic."""
    if len(data) < 20:
        return False
    magic = struct.unpack_from("<I", data, 0)[0]
    return magic == LFS_MAGIC1


def lfs_decompress(data):
    """
    Decompress an LFS file (RE4 UHD format).
    Accepts bytes or bytearray. Returns bytearray.
    """
    if isinstance(data, (bytes, memoryview)):
        data = bytearray(data)

    if len(data) < 20:
        raise RuntimeError("Data too small for LFS header")

    magic, _, size_decompressed, _, num_chunks = struct.unpack_from("<5I", data, 0)
    if magic != LFS_MAGIC1:
        raise RuntimeError(f"Invalid LFS magic: 0x{magic:08X}")
    if num_chunks == 0 or num_chunks > 0x10000:
        raise RuntimeError(f"Invalid chunk count: {num_chunks}")

    header_size = 20
    chunk_table_offset = header_size
    # Each chunk entry: u16 size_compressed, u16 size_decompressed, u32 offset
    chunk_entry_size = 8
    chunks_base = chunk_table_offset

    out = bytearray(size_decompressed)
    out_pos = 0
    st = _LzxState(131072)

    for i in range(num_chunks):
        entry_offset = chunks_base + i * chunk_entry_size
        c_sz, d_sz, offset = struct.unpack_from("<HHI", data, entry_offset)

        comp_data_offset = chunks_base + (offset & ~1)
        comp_size = c_sz if c_sz != 0 else LFS_CHUNK_SIZE
        decomp_size = d_sz if d_sz != 0 else LFS_CHUNK_SIZE

        if out_pos + decomp_size > size_decompressed:
            decomp_size = size_decompressed - out_pos

        if not (offset & 1):
            # Uncompressed chunk
            out[out_pos:out_pos + comp_size] = data[comp_data_offset:comp_data_offset + comp_size]
            out_pos += comp_size
        else:
            # LZX compressed chunk
            written = _lzx_inflate(st, data, comp_data_offset, comp_size,
                                   out, out_pos, decomp_size)
            out_pos += written

    return out[:out_pos]


def xcompress_decompress_re4hd(file_entries):
    """
    Drop-in replacement for xcompress.xcompress_decompress_re4hd.
    Takes the same LFS file_entries (with .raw_data, .size_compressed,
    .size_decompressed, .offset attributes) and returns decompressed bytearray.
    """
    dec_data = bytearray()
    st = _LzxState(131072)

    for i, fe in enumerate(file_entries):
        src_size = LFS_CHUNK_SIZE if fe.size_compressed == 0 else fe.size_compressed
        expected_size = LFS_CHUNK_SIZE if fe.size_decompressed == 0 else fe.size_decompressed

        if fe.offset != 0:
            # Compressed chunk
            raw = fe.raw_data if isinstance(fe.raw_data, (bytes, bytearray)) else bytes(fe.raw_data)
            chunk_out = bytearray(expected_size)
            written = _lzx_inflate(st, bytearray(raw), 0, src_size,
                                   chunk_out, 0, expected_size)
            if written != expected_size:
                raise RuntimeError(
                    f"Chunk {i} output size mismatch (got {written}, expected {expected_size})")
            dec_data.extend(chunk_out[:expected_size])
        else:
            # Uncompressed chunk
            dec_data.extend(fe.raw_data)

    return dec_data
