"""A RE4UHD mesh .bin built in memory.

Every other RE4UHD test reads a shipped model, which is the right way to
check albam against the format. It cannot pin down a case the shipped data
only sometimes contains, though, and a test that skips unless the archive it
was handed happens to hold one proves nothing on the day it skips. A bone
table naming the same id twice is such a case: 69 of 738 models have one, and
none of them is in a dataset a CI run can reach.

Built from the generated struct classes (albam/engines/cie/structs), so what
this writes is the format definition's own idea of a .bin rather than a
second, hand-rolled one that could drift from it. The block layout is
albam's, which is fine: every offset is explicit in the header, so a reader
is told where each block is rather than assuming.
"""
from albam.engines.cie import mesh
from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

# One triangle strip of four corners: a quad, the smallest thing that still
# has two triangles, a UV layer and a weight index per corner.
POSITIONS = [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (0.0, 100.0, 0.0), (100.0, 100.0, 0.0)]
UVS = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
NORMAL = (0.0, 0.0, 1.0)
NO_TEXTURE = 0xFF
FTYPE_TRIANGLE_STRIP = 6


def build_mesh_bin(bones, weights, weight_indices):
    """The bytes of a one-quad mesh .bin carrying exactly this bone table.

    `bones` is [(bone_id, parent, x, y, z)] as the file stores them, repeated
    ids included; `weights` is [(bone_ids, percents, count)]; and
    `weight_indices` is one index into `weights` per corner.
    """
    assert len(weight_indices) == len(POSITIONS)

    dst_bin = Re4UhdBin()
    dst_bin.header = dst_bin.UhdBinHeader(_parent=dst_bin, _root=dst_bin._root)
    for attribute in ("offset_bones", "unk_00", "unk_01", "offset_vertex_colors",
                      "offset_vertex_texcoord", "offset_weights", "num_weights",
                      "num_bones", "num_materials", "offset_materials",
                      "flags", "num_tpl", "vertex_scale", "unk_02", "num_weights2",
                      "offset_morphs", "offset_vertex_position", "offset_vertex_normals",
                      "num_vertices", "num_vertex_normals", "version_flags",
                      "offset_bonepairs", "offset_adjacents", "offset_index_buffer",
                      "offset_index_buffer2"):
        setattr(dst_bin.header, attribute, 0)

    dst_bin.bones = [_bone(dst_bin, *entry) for entry in bones]
    dst_bin.weights = [_weight(dst_bin, *entry) for entry in weights]
    dst_bin.vertex_positions = mesh._serialize_vec3s(dst_bin, POSITIONS)
    dst_bin.normals = mesh._serialize_normals(dst_bin, [NORMAL] * len(POSITIONS))
    dst_bin.texcoords = mesh._serialize_uvs(dst_bin, UVS)
    dst_bin.vertex_colors = mesh._serialize_colors(dst_bin, len(POSITIONS))
    dst_bin.indexes = list(weight_indices)
    dst_bin.indexes2 = list(weight_indices)
    dst_bin.materials = [_material(dst_bin, len(POSITIONS))]
    return mesh._layout_and_write(dst_bin, len(POSITIONS))


def bone_table(bin_bytes):
    """[(bone id, parent, (x, y, z))] in the order the file writes them."""
    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()
    return [(bone.bone_id, bone.parent, (bone.x, bone.y, bone.z)) for bone in parsed.bones]


def _bone(dst_bin, bone_id, parent, x, y, z):
    dst_bone = dst_bin.Bone(_parent=dst_bin, _root=dst_bin._root)
    dst_bone.bone_id, dst_bone.parent = bone_id, parent
    dst_bone.x, dst_bone.y, dst_bone.z = x, y, z
    dst_bone.filler = 0
    dst_bone._check()
    return dst_bone


def _weight(dst_bin, bone_ids, percents, count):
    dst_weight = dst_bin.FmtbinWeight(_parent=dst_bin, _root=dst_bin._root)
    dst_weight.bone_ids = list(bone_ids)
    dst_weight.weights = list(percents)
    dst_weight.count = count
    dst_weight.unk00 = 0
    dst_weight._check()
    return dst_weight


def _material(dst_bin, corners):
    dst_material = dst_bin.Material(_parent=dst_bin, _root=dst_bin._root)
    for attribute in mesh._MATERIAL_BYTE_FIELDS:
        setattr(dst_material, attribute, 0)
    for attribute in mesh._MATERIAL_NO_TEXTURE_FIELDS:
        setattr(dst_material, attribute, NO_TEXTURE)

    dst_face_index = dst_bin.FaceIndex(_parent=dst_material, _root=dst_bin._root)
    strip = dst_bin.Strip(_parent=dst_face_index, _root=dst_bin._root)
    strip.ftype, strip.fcount = FTYPE_TRIANGLE_STRIP, corners
    strip._check()
    dst_face_index.strip_count = 1
    dst_face_index.strips = [strip]
    dst_face_index.num_triangles = corners - 2
    # buffer_size is measured from the strip_count word and padded to 16.
    dst_face_index.buffer_size = mesh._align(8)
    dst_face_index.padding = b"\x00" * (dst_face_index.buffer_size - 8)
    dst_face_index._check()

    dst_material.face_index = dst_face_index
    dst_material._check()
    return dst_material
