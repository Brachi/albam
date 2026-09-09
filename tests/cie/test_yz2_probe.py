"""PROBE ONLY - NOT FOR MERGE.

Runs against the real RE4 UHD corpus (CI supplies it via
--game-dir=re4uhd::r2://<bucket>/re4uhd) and prints what is needed to
establish the YZ2 format. Ends in a deliberate failure so pytest surfaces
the captured output in the job log.

Nothing here prints a plaintext game asset path: archives are identified by
the same truncated-sha256 identity hash the committed catalogs use.
"""
import collections
import math
import os
import struct
import time

import pytest

from tests.cie.lfs_paths import find_lfs_archives
from tests.mtfw.scripts.catalog_paths import hash_identity

# The two archives tests/cie/datasets/udas_variant_hashes.json already
# records as the big-endian variant whose DAT block is a YZ2 stream.
BIG_ENDIAN_UDAS_HASHES = ("16751b2ceafb2bb9", "76e7d1b4720d91d4")

OUT = []


def say(line=""):
    OUT.append(str(line))


@pytest.fixture(scope="session")
def local_app_id():
    return "re4uhd"


def _first_chunk_bytes(path, limit=64):
    """The first `limit` bytes of an .lfs payload, decoding only chunk 0.

    A YZ2 header sits at the very start of the payload, so classifying a
    whole corpus never needs the rest of the archive - which is what makes
    counting every pack affordable at all.
    """
    from kaitaistruct import KaitaiStream

    from albam.engines.cie import lfs_decompress
    from albam.engines.cie.structs.lfs import Lfs

    with open(path, "rb") as handle:
        lfs = Lfs(KaitaiStream(handle))
        lfs._read()
        chunks = lfs.chunks
        if not chunks:
            return b""
        # chunk_sizes() needs the whole table: a chunk's real compressed
        # length is recovered from the distance to the *next* chunk, so
        # handing it a one-chunk slice would measure chunk 0 against the end
        # of the file and inflate its length.
        chunk = chunks[0]
        size = lfs_decompress.chunk_sizes(chunks, chunk._io.size())[0]
        chunk._io.seek(chunk.data_offset)
        raw = chunk._io.read_bytes(size)
        if not chunk.is_compressed:
            return bytes(raw[:limit])
        expected = (lfs_decompress.LFS_CHUNK_SIZE if chunk.size_decompressed == 0
                    else chunk.size_decompressed)
        out = bytearray(expected)
        state = lfs_decompress._LzxState(131072)
        lfs_decompress._lzx_inflate(state, bytearray(raw), 0, len(raw), out, 0, expected)
        return bytes(out[:limit])


def _payload(path):
    from albam.engines.cie.archive import _read_payload

    return _read_payload(path)[0]


def _yz2_sizes(head):
    """(compressed, decompressed) from a 32-byte YZ2 header, or None."""
    from albam.engines.cie.fs import YZ2_HEADER_PATTERN, YZ2_HEADER_SIZE

    block = head[:YZ2_HEADER_SIZE]
    if not YZ2_HEADER_PATTERN.match(block):
        return None
    try:
        compressed, decompressed = (int(v, 16) for v in block.split(b"\n")[0].split(b"\t"))
    except ValueError:
        return None
    return compressed, decompressed


def _entropy(data):
    if not data:
        return 0.0
    counts = collections.Counter(data)
    total = len(data)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _dump(label, data, head=1024, tail=128):
    say(f"--- {label}: {len(data)} bytes, entropy {_entropy(data):.3f}, "
        f"distinct {len(set(data))}")
    if len(data) <= head + tail:
        say(f"    all: {data.hex()}")
        return
    say(f"    head[{head}]: {data[:head].hex()}")
    say(f"    tail[{tail}]: {data[-tail:].hex()}")


def _name_kind(name):
    lowered = name.lower()
    if lowered.endswith(".pack.yz2.lfs"):
        return "pack.yz2"
    if lowered.endswith(".pack.lfs"):
        return "pack"
    if lowered.endswith(".udas.lfs"):
        return "udas"
    return "other"


def test_probe_yz2(game_root):
    started = time.time()
    archives = find_lfs_archives(game_root)
    say(f"corpus: {len(archives)} .lfs archives under the --game-dir root")

    total_bytes = 0
    by_kind = collections.Counter()
    sized = []
    for identity, path in archives:
        size = os.path.getsize(path)
        total_bytes += size
        kind = _name_kind(os.path.basename(identity))
        by_kind[kind] += 1
        sized.append((size, kind, hash_identity(identity), path))
    say(f"corpus bytes: {total_bytes}")
    say(f"by name kind: {dict(by_kind)}")
    say()

    # ---------------------------------------------------------------- packs
    # Whether a pack carries a YZ2 layer is decided by the first 32 bytes of
    # its payload, so chunk 0 alone answers it for the whole corpus.
    say("=== pack classification (chunk 0 only) ===")
    packs = [row for row in sized if row[1] in ("pack", "pack.yz2")]
    packs.sort()
    counts = collections.Counter()
    failures = collections.Counter()
    specimens = []
    budget = 900
    examined = 0
    for size, kind, identity_hash, path in packs:
        if time.time() - started > budget:
            say(f"!! budget exhausted after {examined} packs")
            break
        examined += 1
        try:
            head = _first_chunk_bytes(path)
        except Exception as error:
            failures[f"{kind}:{type(error).__name__}"] += 1
            continue
        sizes = _yz2_sizes(head)
        if sizes is None:
            counts[f"{kind}:plain"] += 1
            if counts[f"{kind}:plain"] <= 4:
                say(f"  plain {kind} {identity_hash} lfs={size} head={head[:32].hex()}")
        else:
            counts[f"{kind}:yz2"] += 1
            specimens.append((sizes[0], sizes[1], identity_hash, path, kind))
    say(f"examined {examined} of {len(packs)} pack archives")
    say(f"counts: {dict(counts)}")
    say(f"failures: {dict(failures)}")
    say()

    # ---------------------------------------------------------------- udas
    say("=== big-endian udas ===")
    from albam.engines.cie.fs import read_udas_block_table, udas_byte_order

    wanted = set(BIG_ENDIAN_UDAS_HASHES)
    for _size, kind, identity_hash, path in sized:
        if identity_hash not in wanted:
            continue
        payload = _payload(path)
        order = udas_byte_order(payload)
        say(f"  {identity_hash}: payload={len(payload)} byte_order={order!r}")
        blocks = read_udas_block_table(payload, order) if order else None
        say(f"    blocks: {blocks}")
        if not blocks:
            continue
        _type, block_size, offset = blocks[0]
        header = payload[offset:offset + 32]
        say(f"    block0 header raw: {header!r}")
        sizes = _yz2_sizes(header)
        say(f"    yz2 sizes: {sizes}  block_size={block_size}")
        if sizes:
            stream = payload[offset + 32:offset + 32 + sizes[0]]
            _dump(f"udas {identity_hash} stream", stream, head=2048, tail=256)
    say()

    # ------------------------------------------------------- yz2 specimens
    say("=== smallest yz2 streams (hand-decodable specimens) ===")
    specimens.sort()
    for compressed, decompressed, identity_hash, path, kind in specimens[:6]:
        payload = _payload(path)
        stream = payload[32:32 + compressed]
        say(f"  {identity_hash} kind={kind} csize={compressed} dsize={decompressed} "
            f"payload={len(payload)} ratio={decompressed / max(compressed, 1):.2f}")
        say(f"    header raw: {payload[:32]!r}")
        say(f"    trailing after stream: {payload[32 + compressed:][:32].hex()!r} "
            f"({len(payload) - 32 - compressed} bytes)")
        _dump(f"stream {identity_hash}", stream, head=3072, tail=256)
    say()

    # ------------------------------------- known-plaintext crib: plain packs
    say("=== plain pack payload prefixes (expected shape of decoded yz2) ===")
    shown = 0
    for size, kind, identity_hash, path in packs:
        if shown >= 4:
            break
        try:
            head = _first_chunk_bytes(path, limit=96)
        except Exception:
            continue
        if _yz2_sizes(head) is not None:
            continue
        shown += 1
        words = struct.unpack_from("<8I", head, 0)
        say(f"  {identity_hash} kind={kind}: {head[:96].hex()}")
        say(f"    as u4: {words}")

    say()
    say(f"elapsed {time.time() - started:.1f}s")
    pytest.fail("PROBE\n" + "\n".join(OUT))
