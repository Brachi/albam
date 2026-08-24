"""
Byte-exact identity round-trip for .anims.ssg (see structs/anims.ksy).

The outer container (32-byte header, per-entry file_info table, file_names,
raw buffer_chunks) is modeled directly in the .ksy and round-trips through
plain `_read()` + `_fetch_instances()` + `_write()` alone, the same way
hexane_ssg's own container does (see edgemodel_roundtrip.py for the
mesh-format precedent this mirrors). Every entry's own bytes inside
buffer_chunks are captured whole (file_info.size is the only thing needed
to slice them - see hexane_ssg.SsgFS for the same convention on the
regular, little-endian .ssg), so identity_roundtrip() below doesn't need to
understand a single clip's own internal layout at all to reproduce it
byte-exact - anims.ksy's own `AnimClip` type (magic + the full confirmed
EdgeAnimAnimation header + an opaque `body` tail) exists for
albam.engines.hexn.animation to use when it needs the *meaning* of a
clip's bytes, not for this round-trip.

Verified against the committed test dataset: files whose headers model
this .ksy directly (id_magic 5 or 6, size_chunks_info always 0) are 100%
byte-exact from `_write()` alone. A handful of leftover dev/test archives
have a garbage `size_chunks_info` far larger than the whole file and a
different file_info layout (their `reserved_01` is 1, not 0, on every
entry) - not modeled here, consistent with edgemodel's own precedent of
excluding a known-unrelated variant rather than force-fitting it (see
structs/anims.ksy's own module doc).
"""
import io

from kaitaistruct import KaitaiStream

from .structs.hexane_anims import HexaneAnims


def identity_roundtrip(data):
    """Parse `data` and write it back out. Byte-exact for every real
    *.anims.ssg checked except the known dev/test archives called out in
    the module docstring above (those fail to parse at all - id_magic is
    still 5/6 but size_chunks_info is corrupt, so `_read()` itself raises).
    """
    parsed = HexaneAnims.from_bytes(data)
    parsed._read()
    parsed._fetch_instances()

    stream = KaitaiStream(io.BytesIO(bytearray(len(data))))
    parsed._write(stream)
    return stream.to_byte_array()
