"""
Byte-exact identity round-trip for .edgemodel (see structs/edgemodel.ksy).

Every section between two mesh_headers - the per-mesh 48-byte shared block
(mesh_header.pre_mesh_data), the groups/flags-driven data
(edgemesh.group_and_flags_data), the mesh_header.unk_ofs_3-driven
count/offset-table gap (mesh_header.unk3_*), the bone-data preamble/section
(edge_header.pre_bones_data/bones_data), and the trailing footer with no
bones (edge_header.pre_trailing_footer/trailing_data) - is modeled
directly in the .ksy from formulas derived against a full-game sweep,
not by generically diffing against the original bytes. Verified against
a full-game sweep (packed and loose, excluding the two known unrelated
variants that fail to parse at all - see HexnFS's byte-reversed/ident-5
.ssg detection and HexaneEdgemodel's own id_magic check for
"IM6S"-tagged non-mesh files): 94.82% of successfully-parsed .edgemodel are
byte-exact from plain `_read()` + `_fetch_instances()` + `_write()` alone,
no post-processing (up from 72% before the unk_ofs_3 gap was modeled).

The remaining ~5% are small (single-digit-to-tens of bytes), not yet
attributed to a specific formula - see project memory
project_edgemodel_format_sweep for what's been ruled out so far. A weapon
LOD/SHADOW sub-variant is also known to break the groups/flags formula
(would compute a negative size) - guarded (`if:`) rather than crashing, so
those meshes just don't reproduce that one section exactly.

identity_roundtrip() is a thin wrapper - `_write()` alone - kept as the
integration point a real exporter should build on (only
buffer_vertices/buffer_indices should change when Blender geometry
changes; kaitai's own `_write()` reproduces everything else it parsed).
"""
import io

from kaitaistruct import KaitaiStream

from .structs.hexane_edgemodel import HexaneEdgemodel


def identity_roundtrip(data):
    """Parse `data` and write it back out. Byte-exact for 94.82% of real
    .edgemodel files (see module docstring for the known remaining gap);
    always at least the correct total length and every seq field's own
    identity value.
    """
    parsed = HexaneEdgemodel.from_bytes(data)
    parsed._read()
    parsed._fetch_instances()

    stream = KaitaiStream(io.BytesIO(bytearray(len(data))))
    parsed._write(stream)
    return stream.to_byte_array()
