"""
Byte-exact identity round-trip for .edgemodel (see structs/edgemodel.ksy).

Several real sections of the format (per-mesh "group" data sized by
num_groups, a flags-driven variable block, a shared block preceding every
mesh but the first, bone data, and a trailing footer) were derived
against a full-game sweep to a >99.6% formula, but not a complete one -
a weapon LOD/SHADOW sub-variant breaks it, and modeling
those pieces as mandatory fields in the .ksy turned "one bad mesh" into
"the whole file fails to parse" for that variant (worse than not modeling
them at all). None of that is required for round-trip fidelity anyway:
`ofs_materials`, `ofs_bones`, buffer offsets/sizes etc. are already read
fields, so the *boundaries* of everything real are already known even
where the *content* isn't modeled.

The strategy here is generic instead: compute every byte range the parser
actually understands (and that HexaneEdgemodel._write() therefore
reproduces correctly), and patch the original bytes back in verbatim for
whatever's left over. Verified against a full-game sweep: 14372/14372
successfully-parsed .edgemodel (packed and loose) round-trip byte-exact
this way - see the "keep digging" session that produced this for the full
investigation (project memory: project_edgemodel_format_sweep).

This is also the right foundation for a real exporter: only
buffer_vertices/buffer_indices need to change when Blender geometry
changes; everything else - including every opaque gap here - should be
copied through untouched, which is exactly what identity_roundtrip() does
when given the unmodified original bytes.
"""
import io

from kaitaistruct import KaitaiStream

from .structs.hexane_edgemodel import HexaneEdgemodel

EDGEMESH_FIXED_SIZE = 128  # edgemesh's own seq size (unk_1_flag..unk_10_size)
MESH_HEADER_FIXED_SIZE = 140  # mesh_header's own seq size (num_groups..reserved_01)
EDGE_HEADER_FIXED_SIZE = 208  # edge_header's own seq size - matches ofs_meshes_info on every file checked


def _known_ranges(parsed, data_len):
    """Every (start, end) byte range `parsed` actually read into a real
    attribute - i.e. what HexaneEdgemodel._write() will correctly
    reproduce. Anything not covered here is a gap (see identity_roundtrip).
    """
    ranges = [(0, EDGE_HEADER_FIXED_SIZE)]
    num_meshes = parsed.header.num_meshes
    ranges.append((EDGE_HEADER_FIXED_SIZE, EDGE_HEADER_FIXED_SIZE + num_meshes * MESH_HEADER_FIXED_SIZE))

    for mesh_header in parsed.meshes_header:
        ranges.append((mesh_header.ofs_data, mesh_header.ofs_data + EDGEMESH_FIXED_SIZE))
        mesh = mesh_header.mesh
        if mesh.size_buffer_indices:
            ranges.append((mesh.ofs_buffer_indices, mesh.ofs_buffer_indices + mesh.size_buffer_indices))
        if mesh.size_buffer_vertices:
            ranges.append((mesh.ofs_buffer_vertices, mesh.ofs_buffer_vertices + mesh.size_buffer_vertices))
        if mesh.size_buffer_weights:
            ranges.append((mesh.ofs_buffer_weights, mesh.ofs_buffer_weights + mesh.size_buffer_weights))

        materials = mesh_header.materials
        pos = mesh_header.ofs_materials + 4 * len(materials.offsets)
        for material_path in materials.all_materials:
            pos += len(material_path) + 1
        ranges.append((mesh_header.ofs_materials, pos))

    # Deliberately no bones-data range: not modeled in the .ksy (see its
    # comment on edge_header), so _write() never touches those bytes -
    # they always come back as a gap, patched from the original below.
    ranges = [(max(0, start), min(data_len, end)) for start, end in ranges if end > start]
    ranges.sort()
    merged = []
    for start, end in ranges:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _gaps(known_ranges, data_len):
    gaps = []
    prev_end = 0
    for start, end in known_ranges:
        if start > prev_end:
            gaps.append((prev_end, start))
        prev_end = max(prev_end, end)
    if prev_end < data_len:
        gaps.append((prev_end, data_len))
    return gaps


def identity_roundtrip(data):
    """Parse `data`, write it back out, and patch every unmodeled gap with
    the original bytes verbatim. Returns bytes identical to `data` for any
    well-formed .edgemodel (see module docstring) - this is the mechanism
    a real exporter should build on: pass through everything except the
    specific buffers being regenerated from current Blender geometry.
    """
    parsed = HexaneEdgemodel.from_bytes(data)
    parsed._read()
    parsed._fetch_instances()

    stream = KaitaiStream(io.BytesIO(bytearray(len(data))))
    parsed._write(stream)
    result = bytearray(stream.to_byte_array())

    for start, end in _gaps(_known_ranges(parsed, len(data)), len(data)):
        result[start:end] = data[start:end]

    return bytes(result)
