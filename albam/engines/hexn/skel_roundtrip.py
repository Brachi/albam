"""
Byte-exact identity round-trip for the RE:ORC skeleton format (see
structs/skel.ksy).

Every section is modeled directly in the .ksy from formulas derived
against a full sweep of real dlc/pack1/Characters/skel/*.ssg files (not
just the committed samples) - outer/inner headers, the hierarchy array,
local bind-pose TRS array, name-offset table and name blob are all
attributed; a handful of regions (two per-node arrays around the TRS block,
and a trailing per-node array) are captured as opaque byte blobs whose
semantics aren't confirmed, same convention as edgemodel_roundtrip.py.

identity_roundtrip() is a thin wrapper - `_write()` alone, same shape as
edgemodel_roundtrip.identity_roundtrip().
"""
import io

from kaitaistruct import KaitaiStream

from .structs.hexane_skel import HexaneSkel


def identity_roundtrip(data):
    """Parse `data` and write it back out."""
    parsed = HexaneSkel.from_bytes(data)
    parsed._read()
    parsed._fetch_instances()

    stream = KaitaiStream(io.BytesIO(bytearray(len(data))))
    parsed._write(stream)
    return stream.to_byte_array()
