"""MT Framework .mod files to and from albam.lib.scene, with no Blender.

`mod_to_scene` decodes a parsed .mod into a Scene: one mesh node per .mod
mesh under a root node, the bones as a joint hierarchy with a skin, and the
.mod's own records in the `ALBAM` extras of the level they belong to.
`scene_to_mod` writes a Scene back into a .mod of the same version as the
source file, deriving everything the format needs that the scene does not
carry (bone palettes, weight bounds, strips, offsets).

Coordinates: the file is Y up in centimetres, the scene is Y up in metres,
so the only conversion is the factor of 100 and nothing swaps axes.
"""
from binascii import crc32
from collections import OrderedDict, namedtuple
import ctypes
from dataclasses import dataclass
from io import BytesIO
from itertools import chain
import math
from struct import pack, unpack

from kaitaistruct import KaitaiStream
import numpy as np

from ...exceptions import AlbamCheckFailure
from ...lib.kaitai_utils import adopt, check_recursive
from ...lib.scene import EXTRAS_KEY, VERTEX_ATTRIBUTE, Material, Mesh, Node, Primitive, Scene, Skin
from ...lib.tristrips import strip_triangles_to_triangles_list, triangles_list_to_triangles_strip
from .structs.mod_153 import Mod153
from .structs.mod_156 import Mod156
from .structs.mod_21 import Mod21


# Scene metres to file centimetres
SCALE = 100

# The vertex-color attribute name the scene carries .mod colors in. Not
# COLOR_0: Blender's glTF importer stores COLOR_0 as a BYTE_COLOR attribute,
# whose sRGB conversion loses 73 of the 256 byte values the file can hold,
# while a custom float attribute lands as FLOAT_COLOR and keeps byte / 255
# exactly. Export reads COLOR_0 too, which is what Blender's exporter emits.
COLOR_ATTRIBUTE = "_ALBAM_COLOR"

MOD_CLASS_MAPPER = {
    153: Mod153,
    156: Mod156,
    210: Mod21,
    211: Mod21,
    212: Mod21,
}
APPID_CLASS_MAPPER = {
    "re0": Mod21,
    "re1": Mod21,
    "re5": Mod156,
    "re6": Mod21,
    "rev1": Mod21,
    "rev2": Mod21,
    "dd": Mod21,
    "dmc4": Mod153,
    "umvc3": Mod21,
}

MOD_VERSION_APPID_MAPPER = {
    153: {"dmc4"},
    156: {"re5"},
    210: {"re0", "re1", "rev1", "rev2"},
    211: {"re6", "umvc3"},
    212: {"dd"},
}

DEFAULT_VERTEX_FORMAT_SKIN = 0x14D40020
DEFAULT_VERTEX_FORMAT_NONSKIN = 0xa7d7d036

VERTEX_FORMATS_MAPPER = {
    0x0: Mod156.VfSkin,
    0x1: Mod156.VfSkinEx,
    0x2: Mod156.VfNonSkin,
    0x3: Mod156.VfNonSkinCol,
    0x4: Mod156.VfSkin,  # placeholder shape
    0x5: Mod156.VfSkin,  # placeholder skin_col
    # 0x4325a03e: Mod21.Vertex4325,  # IANonSkinTBN_4M shape keys not implemented yet
    # 0x2f55c03d: Mod21.Vertex2f55,  # IASkinOTB_4WT_4M shape keys not implemented yet
    0xa14e003c: Mod21.VertexA14e,  # IANonSkinBCA
    0x2082f03b: Mod21.Vertex2082,  # IANonSkinBLA
    0xc66fa03a: Mod21.VertexC66f,  # IANonSkinBA
    0xd1a47038: Mod21.VertexD1a4,  # IANonSkinBL
    0x207d6037: Mod21.Vertex207d,  # IANonSkinBC
    0xa7d7d036: Mod21.VertexA7d7,  # IANonSkinB
    0x37a4e035: Mod21.Vertex37a4,  # IANonSkinTBNLA
    0xb6681034: Mod21.VertexB668,  # IANonSkinTBNCA
    0x9399c033: Mod21.Vertex9399,  # IANonSkinTBCA
    0x12553032: Mod21.Vertex1255,  # IANonSkinTBLA
    0x747d1031: Mod21.Vertex747d,  # IANonSkinTBNA
    0x63b6c02f: Mod21.Vertex63b6,  # IANonSkinTBNL vertex alpha
    0x926fd02e: Mod21.Vertex926f,  # IANonSkinTBNC
    0xafa6302d: Mod21.VertexAfa6,  # IANonSkinTBA
    0x5e7f202c: Mod21.Vertex5e7f,  # IANonSkinTBN
    0xb86de02a: Mod21.VertexB86d,  # IANonSkinTBL vertex alpha
    0x49b4f029: Mod21.Vertex49b4,  # IANonSkinTBC
    0xd8297028: Mod21.Vertex8297,  # IANonSkinTB
    0xcbcf7027: Mod21.VertexCbcf,  # IASkinTBNLA8wt
    0xd84e3026: Mod21.VertexD84e,  # IASkinTBC8wt
    0x75c3e025: Mod21.Vertex75c3,  # IASkinTBN8wt
    0xbb424024: Mod21.VertexBb42,  # IASkinTB8wt
    0x64593023: Mod21.Vertex6459,  # IASkinTBNLA4wt
    0x77d87022: Mod21.Vertex77d8,  # IASkinTBC4wt
    0xdA55a021: Mod21.VertexDa55,  # IASkinTBN4wt
    0x14d40020: Mod21.Vertex14d4,  # IASkinTB4wt
    0xb392101f: Mod21.VertexB392,  # IASkinTBNLA2wt
    0xa013501e: Mod21.VertexA013,  # IASkinTBC2wt
    0xd9e801d: Mod21.VertexD9e8,  # IASkinTBN2wt
    0xc31f201c: Mod21.VertexC31f,  # IASkinTB2wt
    0xd877801b: Mod21.VertexD877,  # IASkinTBNLA1wt
    0xcbf6c01a: Mod21.VertexCbf6,  # IASkinTBC1wt
    0x667b1019: Mod21.Vertex667b,  # IASkinTBN1wt
    0xa8fab018: Mod21.VertexA8fa,  # IASkinTB1wt
    0xa320c016: Mod21.VertexA320,  # IASkinBridge8wt
    0xcb68015: Mod21.VertexCb68,  # IASkinBridge4wt
    0xdb7da014: Mod21.VertexDb7d,  # IASkinBridge2wt
    0xb0983013: Mod21.VertexB098,  # IASkinBridge1wt
}

VERTEX_FORMATS_RGBA = (
    0x3,
    0xa14e003c,
    0x207d6037,
    0xb6681034,
    0x9399c033,
    0x926fd02e,
    0x49b4f029,
    0xd84e3026,
    0x77d87022,
    0xa013501e,
    0xcbf6c01a,
)

VERTEX_FORMATS_VERTEX_ALPHA = (
    0x63b6c02f,
    0xb86de02a,
)

VERTEX_FORMATS_TANGENT = (
    0x0,
    0x2,
    0x3,
    0x4,
    0x5,
    0x4325a03e,
    0x2f55c03d,
    0x37a4e035,
    0xb6681034,
    0x9399c033,
    0x12553032,
    0x747d1031,
    0x63b6c02f,
    0x926fd02e,
    0xafa6302d,
    0x5e7f202c,
    0xb86de02a,
    0x49b4f029,
    0xd8297028,
    0xcbcf7027,
    0xd84e3026,
    0x75c3e025,
    0xbb424024,
    0x64593023,
    0x77d87022,
    0xdA55a021,
    0x14d40020,
    0xb392101f,
    0xa013501e,
    0xd9e801d,
    0xc31f201c,
    0xd877801b,
    0xcbf6c01a,
    0x667b1019,
    0xa8fab018,
)

VERTEX_FORMATS_UV2 = (
    0x0,
    0x2,
    0x3,
    0x4,
    0x5,
    0x4325a03e,
    0xa14e003c,
    0x2082f03b,
    0xc66fa03a,
    0xd1a47038,
    0x37a4e035,
    0xb6681034,
    0x9399c033,
    0x12553032,
    0x747d1031,
    0x63b6c02f,
    0x926fd02e,
    0xafa6302d,
    0x5e7f202c,
    0xb86de02a,
    0xcbcf7027,
    0x75c3e025,
    0x64593023,
    0xdA55a021,
    0xb392101f,
    0xd877801b,
    0x667b1019,
)

VERTEX_FORMATS_UV3 = (
    0x2,
    0x2082f03b,
    0x37a4e035,
    0xb6681034,
    0x12553032,
    0x747d1031,
    0x63b6c02f,
    0xcbcf7027,
    0x64593023,
    0xb392101f,
    0xd877801b,
)

VERTEX_FORMATS_UV4 = (
    0x37a4e035,
    0xcbcf7027,
    0x64593023,
    0xb392101f,
    0xd877801b,
)

VERTEX_FORMATS_BRIDGE = (
    0xa320c016,
    0xcb68015,
    0xdb7da014,
    0xb0983013,
)

VERTEX_FORMATS_NORMAL4 = (
    0xa14e003c,
    0x2082f03b,
    0xc66fa03a,
    0xd1a47038,
    0x207d6037,
    0xa7d7d036,
    0xa320c016,
    0xcb68015,
    0xdb7da014,
    0xb0983013,
)
VERTEX_FORMATS_BONE_LIMIT = {
    0x1: 8,
    0x0: 4,
    0x4: 4,
    0x5: 4,
    0xcbcf7027: 8,  # IASkinTBNLA8wt
    0xd84e3026: 8,  # IASkinTBC8wt
    0x75c3e025: 8,  # IASkinTBN8wt
    0xbb424024: 8,  # IASkinTB8wt
    0x64593023: 4,  # IASkinTBNLA4wt
    0x77d87022: 4,  # IASkinTBC4wt
    0xdA55a021: 4,  # IASkinTBN4wt
    0x14d40020: 4,  # IASkinTB4wt
    0xb392101f: 2,  # IASkinTBNLA2wt
    0xa013501e: 2,  # IASkinTBC2wt
    0xd9e801d: 2,  # IASkinTBN2wt
    0xc31f201c: 2,  # IASkinTB2wt
    0xd877801b: 1,  # IASkinTBNLA1wt
    0xcbf6c01a: 1,  # IASkinTBC1wt
    0x667b1019: 1,  # IASkinTBN1wt
    0xa8fab018: 1,  # IASkinTB1wt
    0xa320c016: 8,  # IASkinBridge8wt
    0xcb68015: 4,  # IASkinBridge4wt
    0xdb7da014: 2,  # IASkinBridge2wt
    0xb0983013: 1,  # IASkinBridge1wt
}

VERTEX_FORMAT_POS3S2 = [
    0xd877801b,
    0xcbf6c01a,
    0x667b1019,
    0xb0983013,
    0xa8fab018,
]

BBOX_AFFECTED = [
    0x667B1019,
    0xCBF6C01A,
    0xB0983013,
    0xA8FAB018,
    0xD877801B,
]

VERSIONS_USE_BONE_PALETTES = {153, 156}
VERSIONS_BONES_BBOX_AFFECTED = {210, 211, 212}
VERSIONS_USE_TRISTRIPS = {153, 156, 212}
# The versions mod-21.ksy covers, which size their index buffer as
# num_indices * 2 rather than (num_indices * 2) - 2.
VERSIONS_MOD_21 = {210, 211, 212}

MAIN_LODS = {
    "re0": [1, 255],
    "re1": [1, 255],
    "re5": [1, 255],
    "re6": [1, 3, 255],
    "rev1": [1, 255],
    "rev2": [1, 255],
    "dd": [1, 255],
    "dmc4": [1, 255],
    "umvc3": [255],  # its models ship a single LOD, always 255
}

# What bone_map holds for an animation id no bone answers to. A model can
# never have a bone at index 255 - idx_parent is a u1 and 255 is its "no
# parent" - so the index space has a spare value to say "unmapped".
UNMAPPED_ANIM_ID = 255

# What idx_parent holds for a bone with no parent, and idx_mirror for a bone
# with no mirror. A bone that mirrors *itself* is spelled differently, with its
# own index, and the two are not interchangeable.
NO_PARENT = 255
NO_MIRROR = 255

# The fourth byte of the bone record is alignment padding, not a field: the
# struct is three u1 then a f4, so the compiler leaves a byte spare. Capcom's
# exporter wrote uninitialised heap into it - its most common value across a
# large sample is 0xCD, which is MSVC's fill for exactly that - so there is
# nothing to carry across and a defined value is written instead.
BONE_RECORD_PADDING = 0

# The most bones a model can hold. idx_parent and idx_mirror are each a u1 and
# spend 255 on "none", so 255 is the first index neither can name. num_bones is
# a u2 and is not the limit.
MAX_ADDRESSABLE_BONES = 255

MAX_BONE_PALETTE_SIZE = 32

# The mesh record fields a modder edits, per format: what the scene's
# `mesh_props` extras carry and what Blender shows as custom properties.
# Everything else in the record is derived on export.
MESH_PROPS_156 = (
    "level_of_detail", "idx_group", "alpha_priority", "shape", "reserved2_flag_1",
    "reserved2_flag_2", "env", "refrect", "shadow_cast", "shadow_receive", "sort",
    "vdeclbase", "vdecl", "rcn_base", "boundary",
)
MESH_PROPS_21 = (
    "level_of_detail", "draw_mode", "idx_group", "disp", "shape", "sort", "alpha_priority",
    "topology", "binormal_flip", "bridge", "bone_id_start", "connect_id", "boundary",
    "vertex_format",
)


def mesh_props_fields(mod_version):
    return MESH_PROPS_156 if mod_version in (153, 156) else MESH_PROPS_21


# num_vertices and last_index are each a u2 on every mod version (mod_21,
# mod_153, mod_156). last_index is current_vertex_position (the running
# total across every mesh sharing one vertex block, see no_vf_grouping
# below) plus this mesh's own count minus one, so it overflows when meshes
# add up; num_vertices overflows on its own for a single mesh of exactly
# 65536 vertices, where last_index still fits. Either way Kaitai's
# write_u2le would raise a bare struct.error naming neither the mesh nor
# the field.
MAX_MESH_U2 = 0xFFFF


def _validate_app_id_for_mod(app_id, mod_bytes):
    if len(mod_bytes) < 5:
        raise AlbamCheckFailure(
            "This .mod file appears to be truncated or corrupted",
            details=f"File is only {len(mod_bytes)} bytes long, too short to contain a valid header",
            solution="Re-extract this file from the game's archive and try importing it again"
        )
    mod_version = mod_bytes[4]
    expected_app_ids = MOD_VERSION_APPID_MAPPER.get(mod_version)
    if expected_app_ids is None:
        raise AlbamCheckFailure(
            "The file to import doesn't seem to be valid for "
            "the selected App",
            details=f"Unknown mod version: {mod_version}",
            solution="Double check that you selected the correct App and re-import"
        )
    if app_id not in expected_app_ids:
        if not (mod_version == 211 and app_id == "umvc3"):
            raise AlbamCheckFailure(
                "The file to import doesn't seem to be valid for "
                "the selected App",
                details=f"mod version {mod_version} doesn't match app_id {app_id}",
                solution="Double check that you selected the correct App and re-import"
            )


# ---------------------------------------------------------------------------
# Reading: .mod records to arrays

BboxData = namedtuple(
    "BboxData",
    (
        "min_x", "min_y", "min_z",
        "max_x", "max_y", "max_z",
        "width", "height", "depth",
        "dimension",
    ),
)


def _create_bbox_data(mod):
    min_length = abs(min(mod.bbox_min.x, mod.bbox_min.y, mod.bbox_min.z))
    max_length = max(abs(mod.bbox_max.x), abs(mod.bbox_max.y), abs(mod.bbox_max.z))
    dimension = min_length + max_length

    return BboxData(
        min_x=mod.bbox_min.x,
        min_y=mod.bbox_min.y,
        min_z=mod.bbox_min.z,
        max_x=mod.bbox_max.x,
        max_y=mod.bbox_max.y,
        max_z=mod.bbox_max.z,
        width=mod.bbox_max.x - mod.bbox_min.x,
        height=mod.bbox_max.y - mod.bbox_min.y,
        depth=mod.bbox_max.z - mod.bbox_min.z,
        dimension=dimension,
    )


def _to_matrix(m):
    """The file's row-vector (DirectX style) matrix as a column-vector one."""
    rows = np.array([
        (m.row_1.x, m.row_1.y, m.row_1.z, m.row_1.w),
        (m.row_2.x, m.row_2.y, m.row_2.z, m.row_2.w),
        (m.row_3.x, m.row_3.y, m.row_3.z, m.row_3.w),
        (m.row_4.x, m.row_4.y, m.row_4.z, m.row_4.w),
    ], dtype=np.float64)
    return rows.T


def _rotation_part(matrix):
    """The rotation a 4x4 matrix carries, with its scale divided out."""
    axes = matrix[:3, :3]
    norms = np.linalg.norm(axes, axis=0)
    norms[norms == 0] = 1
    rotation = np.eye(4)
    rotation[:3, :3] = axes / norms
    return rotation


def _get_parents(mod, bone):
    parents = []
    current_parent_id = bone.idx_parent

    while current_parent_id != NO_PARENT:
        parent = mod.bones_data.bones_hierarchy[current_parent_id]
        parents.append(current_parent_id)
        current_parent_id = parent.idx_parent
    parents.reverse()
    return parents


def _transform_parent_matrix(mod, bone_index):
    """A bone's rest position in model space, in file units, walking the
    parent-space matrices down from the root."""
    bone = mod.bones_data.bones_hierarchy[bone_index]
    parents = _get_parents(mod, bone)
    local_matrices = [mod.bones_data.parent_space_matrices[pi] for pi in parents]
    local_matrices.append(mod.bones_data.parent_space_matrices[bone_index])

    world_matrix = np.eye(4)
    for m in local_matrices:
        world_matrix = world_matrix @ _to_matrix(m)
    return world_matrix[:3, 3]


def _transform_inverse_bind_matrix(mod, matrix, bbox_data):
    """A bone's rest position in model space, in file units, from its
    inverse bind matrix - which the 21 versions store in bbox space."""
    bl_matrix = _to_matrix(matrix)

    if mod.header.version in VERSIONS_BONES_BBOX_AFFECTED:
        # bbox-space to global-space
        scale_matrix = np.diag([bbox_data.dimension] * 3 + [1.0])
        # a translation that doesn't affect the scale component
        translation_matrix = np.zeros((4, 4))
        translation_matrix[:3, 3] = (bbox_data.min_x, bbox_data.min_y, bbox_data.min_z)
        rotation_matrix = _rotation_part(bl_matrix)
        bl_matrix = bl_matrix @ np.linalg.inv(scale_matrix) @ np.linalg.inv(rotation_matrix)
        bl_matrix = bl_matrix - translation_matrix

    return np.linalg.inv(bl_matrix)[:3, 3]


def bone_heads(app_id, mod, bbox_data):
    """Every bone's rest position in model space, in file units."""
    heads = []
    for i in range(len(mod.bones_data.bones_hierarchy)):
        if app_id == "umvc3":
            # umvc3's inverse bind matrices don't survive the bbox transform
            # every other version-21x app needs: past the first two bones the
            # positions they produce drift off the skeleton entirely, while
            # walking the parent-space matrices down the hierarchy lands every
            # bone where the mesh expects it.
            heads.append(_transform_parent_matrix(mod, i))
        else:
            heads.append(_transform_inverse_bind_matrix(
                mod, mod.bones_data.inverse_bind_matrices[i], bbox_data))
    return np.array(heads, dtype=np.float64)


def _vertex_position(mod_version, mesh, vertex, bbox_data):
    x = vertex.position.x
    y = vertex.position.y
    z = vertex.position.z

    w = getattr(vertex.position, "w", None)
    if w is not None and mod_version in (153, 156):
        x = x / 32767 * bbox_data.width + bbox_data.min_x
        y = y / 32767 * bbox_data.height + bbox_data.min_y
        z = z / 32767 * bbox_data.depth + bbox_data.min_z

    elif (w is not None and mod_version in (210, 211, 212)) or (
            mod_version in (210, 211, 212) and mesh.vertex_format in BBOX_AFFECTED):
        x = x / 32767 * bbox_data.dimension + bbox_data.min_x
        y = y / 32767 * bbox_data.dimension + bbox_data.min_y
        z = z / 32767 * bbox_data.dimension + bbox_data.min_z

    return (x, y, z)


def _vertex_normal(vertex):
    # from [0, 255] to [-1, 1]
    return (
        ((vertex.normal.x / 255) * 2) - 1,
        ((vertex.normal.y / 255) * 2) - 1,
        ((vertex.normal.z / 255) * 2) - 1,
    )


def _fix_nan_uv(u, v):
    if u != u or v != v:
        return 0.0, 0.0
    return u, v


def _vertex_uv(uv):
    u = unpack("e", bytes(uv.u))[0]
    v = unpack("e", bytes(uv.v))[0]
    return _fix_nan_uv(u, v)


def _vertex_color(vertex):
    b = vertex.rgba.x / 255
    g = vertex.rgba.y / 255
    r = vertex.rgba.z / 255
    a = vertex.rgba.w / 255
    return (r, g, b, a)


def _get_bone_indices(mod, mesh, bone_indices):
    mapped_bone_indices = []

    if mod.header.version in VERSIONS_USE_BONE_PALETTES:
        bone_palette = mod.bones_data.bone_palettes[mesh.idx_bone_palette]
        for bi, bone_index in enumerate(bone_indices):
            if bone_index >= bone_palette.unk_01:
                real_bone_index = mod.bones_data.bone_map[bone_index]
            else:
                try:
                    real_bone_index = mod.bones_data.bone_palettes[
                        mesh.idx_bone_palette].indices[bone_index]
                except IndexError:
                    # Behaviour not observed in original files so far
                    real_bone_index = bone_index
            mapped_bone_indices.append(real_bone_index)
    elif mesh.vertex_format in (
        0xC31F201C,
        0xB392101F,
    ):
        b1 = int(unpack("e", bone_indices[0])[0])
        b2 = int(unpack("e", bone_indices[1])[0])
        mapped_bone_indices.extend((b1, b2))
    elif mesh.vertex_format == 0xdb7da014:
        b1 = bone_indices[0]
        b2 = bone_indices[2]
        mapped_bone_indices.extend((b1, b2))
    else:
        mapped_bone_indices = bone_indices

    return mapped_bone_indices


def _get_weights(mod, mesh, vertex):
    if mod.header.version in (153, 156) or mesh.vertex_format in (0xCB68015, 0xa320c016):
        return tuple([w / 255 for w in vertex.weight_values])

    # Assuming all vertex formats share this pattern.
    # TODO: verify
    if len(vertex.bone_indices) == 1:
        return (1.0,)
    # 2w
    elif mesh.vertex_format in (
        0xC31F201C,
        0xDB7DA014,
        0xb392101f,
    ):
        w1 = vertex.position.w / 32767
        w2 = 1.0 - w1
        return (w1, w2)
    # 4w
    elif mesh.vertex_format in (
        0x14D40020,
        0x2F55C03D,
        0x64593023,
        0xDA55A021,
        0x77D87022,
    ):
        w1 = vertex.position.w / 32767
        w2 = unpack("e", bytes(vertex.weight_values[0]))[0]
        w3 = unpack("e", bytes(vertex.weight_values[1]))[0]
        w4 = round(1.0 - w1 - w2 - w3, 3)
        return (w1, w2, w3, w4)
    # 8w
    elif mesh.vertex_format in (
        0x75C3E025,
        0xCBCF7027,
        0xBB424024,
        0xD84E3026,
    ):
        w1 = vertex.position.w / 32767
        w2 = vertex.weight_values[0] / 255
        w3 = vertex.weight_values[1] / 255
        w4 = vertex.weight_values[2] / 255
        w5 = vertex.weight_values[3] / 255
        w6 = unpack("e", bytes(vertex.weight_values2[0]))[0]
        w7 = unpack("e", bytes(vertex.weight_values2[1]))[0]
        w8 = 1.0 - w1 - w2 - w3 - w4 - w5 - w6 - w7
        return (w1, w2, w3, w4, w5, w6, w7, w8)
    else:
        print(
            f"Can't get weights for vertex_format '{hex(mesh.vertex_format)}'")
        return (0, 0, 0, 0)


def _get_material_hash(mod, mesh, app_id):
    material_hash = None
    if mod.header.version in (153, 156):
        material_hash = mesh.idx_material
    elif mod.header.version == 210 or mod.header.version == 212 or app_id == "umvc3":
        material_name = mod.materials_data.material_names[mesh.idx_material]
        material_hash = crc32(material_name.encode()) ^ 0xFFFFFFFF
    elif mod.header.version == 211:
        material_hash = mod.materials_data.material_hashes[mesh.idx_material]
    return material_hash


def _record_fields(record):
    """A kaitai record's scalar fields, JSON-ready."""
    fields = {}
    for key, value in vars(record).items():
        if key.startswith("_"):
            continue
        if isinstance(value, (bool, int, float)):
            fields[key] = value
    return fields


def decode_mesh(app_id, mod, mesh, bbox_data):
    """The glTF-named attribute arrays and triangle list of one .mod mesh."""
    mod_version = mod.header.version
    positions = []
    normals = []
    uvs = [[], [], [], []]
    colors = []
    influences = []  # per vertex: [(bone_index, weight), ...]
    max_influences = 0

    for vertex in mesh.vertices:
        positions.append(_vertex_position(mod_version, mesh, vertex, bbox_data))
        if hasattr(vertex, "normal"):
            normals.append(_vertex_normal(vertex))
        for slot, attr in enumerate(("uv", "uv2", "uv3", "uv4")):
            if hasattr(vertex, attr):
                uvs[slot].append(_vertex_uv(getattr(vertex, attr)))
        if hasattr(vertex, "rgba"):
            colors.append(_vertex_color(vertex))
        if hasattr(vertex, "bone_indices"):
            bone_indices = _get_bone_indices(mod, mesh, vertex.bone_indices)
            weights = _get_weights(mod, mesh, vertex)
            pairs = [(int(bi), float(w)) for bi, w in zip(bone_indices, weights) if w]
            max_influences = max(max_influences, len(pairs))
            influences.append(pairs)

    attributes = {"POSITION": (np.array(positions, dtype=np.float64) / SCALE).astype(np.float32)}
    if normals:
        n = np.array(normals, dtype=np.float32)
        norms = np.linalg.norm(n, axis=1, keepdims=True)
        np.divide(n, norms, out=n, where=norms != 0)
        attributes["NORMAL"] = n
    for slot, slot_uvs in enumerate(uvs):
        if slot_uvs:
            attributes[f"TEXCOORD_{slot}"] = np.array(slot_uvs, dtype=np.float32)
    if colors:
        attributes[COLOR_ATTRIBUTE] = np.array(colors, dtype=np.float32)
    if influences and max_influences:
        slots = 8 if max_influences > 4 else 4
        joints = np.zeros((len(influences), slots), dtype=np.uint16)
        weights = np.zeros((len(influences), slots), dtype=np.float32)
        for vertex_index, pairs in enumerate(influences):
            for slot, (bone_index, weight) in enumerate(pairs[:slots]):
                joints[vertex_index, slot] = bone_index
                weights[vertex_index, slot] = weight
        for k in range(slots // 4):
            attributes[f"JOINTS_{k}"] = joints[:, 4 * k:4 * k + 4]
            attributes[f"WEIGHTS_{k}"] = weights[:, 4 * k:4 * k + 4]

    if not positions:
        raise AlbamCheckFailure(
            "This .mod file has a mesh with no vertices",
            solution="Re-extract this file from the game's archive and try importing it again",
        )
    indices = list(mesh.indices)
    if mod_version in VERSIONS_USE_TRISTRIPS:
        indices = strip_triangles_to_triangles_list(indices)
    if indices and min(indices) >= mesh.first_index:  # backwards compability workaround
        # convert indices for this mesh only, so they start at zero
        indices = [tri_idx - mesh.first_index for tri_idx in indices]
    if indices and min(indices) < 0:
        raise AlbamCheckFailure(
            "This .mod file has a mesh with bad face indices",
            details=f"a face index falls before the mesh's first vertex ({mesh.first_index})",
            solution="Re-extract this file from the game's archive and try importing it again",
        )
    indices = np.array(indices, dtype=np.uint32)
    # whole triangles only, the way Blender's from_pydata reads them
    indices = indices[:len(indices) - len(indices) % 3]
    return attributes, indices


def mod_to_scene(app_id, mod, name, lods=None):
    """The Scene of a parsed .mod. `lods` keeps only the meshes with those
    `level_of_detail` values; None keeps every mesh."""
    scene = Scene(generator="albam mtfw")
    bbox_data = _create_bbox_data(mod)
    header = mod.header

    root_extras = {
        "app_id": app_id,
        "format": "mod",
        "version": header.version,
        "bbox_min": [mod.bbox_min.x, mod.bbox_min.y, mod.bbox_min.z],
        "bbox_max": [mod.bbox_max.x, mod.bbox_max.y, mod.bbox_max.z],
    }
    root = scene.add_node(Node(name=name, extras={EXTRAS_KEY: root_extras}))

    skin = None
    if header.num_bones:
        heads = bone_heads(app_id, mod, bbox_data)
        bones = mod.bones_data.bones_hierarchy
        joint_nodes = []
        for i, bone in enumerate(bones):
            parent_head = heads[bone.idx_parent] if bone.idx_parent != NO_PARENT else np.zeros(3)
            extras = {
                "idx_anim_map": bone.idx_anim_map,
                "idx_mirror": bone.idx_mirror,
                "anim_retarget": str(bone.idx_anim_map),
                # The format spells this three ways and all three have to
                # survive: 255 for a bone with no mirror at all, the bone's
                # own index for one that mirrors itself, and another index
                # for a real pair. Empty carries the first; the other two are
                # just the name of the bone pointed at.
                "mirror": "" if bone.idx_mirror >= len(bones) else str(bone.idx_mirror),
                "furthest_vertex_distance": bone.furthest_vertex_distance,
                "parent_distance": bone.parent_distance,
            }
            node = Node(name=str(i), translation=(heads[i] - parent_head) / SCALE,
                        extras={EXTRAS_KEY: extras})
            parent = root if bone.idx_parent == NO_PARENT else joint_nodes[bone.idx_parent]
            joint_nodes.append(scene.add_node(node, parent=parent))
        inverse_bind_matrices = np.tile(np.eye(4, dtype=np.float32), (len(bones), 1, 1))
        inverse_bind_matrices[:, :3, 3] = -heads / SCALE
        skin = scene.add_skin(Skin(joints=joint_nodes, inverse_bind_matrices=inverse_bind_matrices,
                                   skeleton=root, name=name))

    materials_by_hash = {}
    for i, mesh in enumerate(mod.meshes_data.meshes):
        if lods is not None and mesh.level_of_detail not in lods:
            continue
        material_hash = _get_material_hash(mod, mesh, app_id)
        if material_hash not in materials_by_hash:
            materials_by_hash[material_hash] = scene.add_material(Material(
                name=f"{name}_material_{material_hash}",
                extras={EXTRAS_KEY: {"material_hash": material_hash}}))
        attributes, indices = decode_mesh(app_id, mod, mesh, bbox_data)
        mesh_extras = _record_fields(mesh)
        mesh_extras["material_hash"] = material_hash
        mesh_extras["mesh_index"] = i
        mesh_extras["mesh_props"] = {
            field: getattr(mesh, field)
            for field in mesh_props_fields(header.version) if hasattr(mesh, field)}
        if header.version in (153, 156):
            material = mod.materials_data.materials[mesh.idx_material]
            mesh_extras["material_props"] = {
                "vtype": hex(material.vtype), "func_skin": hex(material.func_skin)}
        mesh_name = f"{name}_{str(i).zfill(4)}"
        mesh_index = scene.add_mesh(Mesh(
            name=mesh_name,
            primitives=[Primitive(attributes=attributes, indices=indices,
                                  material=materials_by_hash[material_hash])],
            extras={EXTRAS_KEY: mesh_extras},
        ))
        node = Node(name=mesh_name, mesh=mesh_index, skin=skin if "JOINTS_0" in attributes else None,
                    extras={EXTRAS_KEY: {"mesh_index": i}})
        scene.add_node(node, parent=root)
    return scene


# ---------------------------------------------------------------------------
# Writing: arrays to .mod records

@dataclass
class ExportSettings:
    export_bones: bool = True
    no_vf_grouping: bool = False
    force_lod255: bool = False
    force_max_num_weights: bool = False


@dataclass
class MeshInput:
    """One mesh of the scene as the writer reads it: the primitive's arrays
    plus what the scene's extras say about it."""
    name: str
    primitive: object
    # name of the material, as the material serializer maps it
    material_name: str
    # the mesh record's custom properties, already in the file's types
    mesh_props: dict
    # the material's vtype/func_skin on the 156 versions, as hex strings
    material_props: dict
    skinned: bool
    # per vertex: [(bone_index, weight), ...] with weight > 0
    influences: list


def _clean_uv(uv_x, uv_y):
    """Replace the -0.0 the half float format forbids."""
    return (0.0 if uv_x == -0.0 else uv_x, 0.0 if uv_y == -0.0 else uv_y)


def _normalize_uv(uv_x, uv_y):
    """Flip UV for .dds and replace forbidden for half float -0.0 values"""
    uv_y *= -1
    uv_y += 1
    uv_y = 0.0 if uv_y == -0.0 else uv_y
    uv_x = 0.0 if uv_x == -0.0 else uv_x
    return uv_x, uv_y


def _check_uv_range(mesh_name, uvs, layer_index):
    """Refuse a UV layer with a coordinate too large to pack as a half float.

    Every UV slot stores u and v with pack('e', ...), which raises
    OverflowError from a magnitude of 65520 (the largest finite half float is
    65504; values in between round down to it). Packing the layer's most
    extreme coordinate once tells whether any of them overflows, with pack
    itself as the authority on the limit.
    """
    if uvs is None or not len(uvs):
        return
    magnitudes = np.abs(uvs).max(axis=1)
    u, v = (float(c) for c in uvs[int(magnitudes.argmax())])
    try:
        pack('ee', u, v)
    except OverflowError:
        raise AlbamCheckFailure(
            message=f"Mesh {mesh_name!r} has a UV coordinate too large to export",
            details=(f"UV slot {layer_index + 1} has a vertex at "
                     f"({u}, {1 - v}), the half-float format UVs are stored in only holds "
                     "values up to about 65504"),
            solution="Scale that UV map back into a normal range (close to 0-1) before exporting",
        )


def _apply_bbox_transforms(xyz_tuple, dst_mod, bbox_data):
    x, y, z = xyz_tuple

    if dst_mod.header.version in (153, 156):

        x -= dst_mod.bbox_min.x
        x /= (dst_mod.bbox_max.x - dst_mod.bbox_min.x)
        x *= 32767

        y -= dst_mod.bbox_min.y
        y /= (dst_mod.bbox_max.y - dst_mod.bbox_min.y) or 1
        y *= 32767

        z -= dst_mod.bbox_min.z
        z /= (dst_mod.bbox_max.z - dst_mod.bbox_min.z) or 1
        z *= 32767

    elif dst_mod.header.version in (210, 211, 212):
        x -= bbox_data.min_x
        x /= bbox_data.dimension
        x *= 32767

        y -= bbox_data.min_y
        y /= bbox_data.dimension
        y *= 32767

        z -= bbox_data.min_z
        z /= bbox_data.dimension
        z *= 32767

    return (round(x), round(y), round(z))


def _weight_export_params(dst_mod, vertex_format):
    """
    The per-vertex bone limit and weight encoding `_export_vertices` uses
    for `vertex_format`. Shared with the weight bound filter so it mirrors
    whichever branch the exporter actually takes (see issue #253).
    """
    max_bones_per_vertex = VERTEX_FORMATS_BONE_LIMIT.get(vertex_format, 4)
    half_float = (dst_mod.header.version in VERSIONS_MOD_21 and
                  vertex_format not in VERTEX_FORMATS_BRIDGE)
    return max_bones_per_vertex, half_float


def _truncate_and_normalize_weights(influence_list, max_bones_per_vertex):
    """
    Keep a vertex's `max_bones_per_vertex` strongest influences and
    normalize them to sum to 1. Returns (bone_indices, weights), both
    ordered by descending weight.
    """
    # limit max bones
    if len(influence_list) > max_bones_per_vertex:
        influence_list = sorted(
            influence_list, key=lambda t: t[1])[-max_bones_per_vertex:]

    weight_data = {t[0]: t[1] for t in influence_list}
    wd_sorted = {k: v for k, v in sorted(weight_data.items(), key=lambda item: item[1], reverse=True)}
    bone_indices = [bi for bi in wd_sorted.keys()]
    weights = [w for w in wd_sorted.values()]
    # normalize
    total_weight = sum(weights)
    if total_weight:
        weights = [round((w / total_weight), 4) for w in weights]
    return bone_indices, weights


def _check_weights(weights, max_weights):
    _weights = []
    i = max_weights - 4
    weights.extend([0] * (max_weights - len(weights)))
    if max_weights in [1, 2]:
        return weights
    _weights.append(round(weights[0] * 32767) / 32767)
    if max_weights == 8:
        _weights.append(round(weights[1] * 255) / 255)
        _weights.append(round(weights[2] * 255) / 255)
        _weights.append(round(weights[3] * 255) / 255)
        _weights.append(round(weights[4] * 255) / 255)
    _weights.append(unpack("e", pack("e", weights[i + 1]))[0])
    _weights.append(unpack("e", pack("e", weights[i + 2]))[0])
    _weights.append(weights[i + 3])
    return _weights


def _process_vertex_weights(influence_list, max_bones_per_vertex, half_float):
    """
    The (bone_index, weight) pairs `_export_vertices` serializes for a
    single vertex, or None when the byte path is left with nothing to write.
    """
    bone_indices, weights = _truncate_and_normalize_weights(
        influence_list, max_bones_per_vertex)
    if half_float:
        weights = _check_weights(weights, max_bones_per_vertex)
    else:
        # can't have zero values
        weights = [round(w * 255) or 1 for w in weights]
        if not weights:
            # XXX vertex_position_2 research, beware
            return None
        # correct precision
        excess = sum(weights) - 255
        if excess:
            max_index, _ = max(enumerate(weights), key=lambda p: p[1])
            weights[max_index] -= excess

    return list(zip(bone_indices, weights))


def _encode_half_float_weight_slots(weight_values, max_bones_per_vertex):
    """
    Encode a vertex's weights into the fields the mod-21 non-bridge vertex
    formats serialize: (position.w, weight_values, weight_values2), each
    None for a slot group the format doesn't carry. The last slot is never
    written: the game reconstructs it as one minus the rest, the way
    `_get_weights` does on import.
    """
    match max_bones_per_vertex:
        case 2:
            return round(weight_values[0] * 32767), None, None
        case 4:
            return (round(weight_values[0] * 32767),
                    [pack("e", weight_values[1]), pack("e", weight_values[2])],
                    None)
        case 8:
            return (round(weight_values[0] * 32767),
                    [round(weight_values[i] * 255) for i in range(1, 5)],
                    [pack("e", weight_values[5]), pack("e", weight_values[6])])
    return None, None, None


def _reconstruct_half_float_weights(weight_values, max_bones_per_vertex):
    """
    The weight each slot ends up with once a vertex encoded by
    `_encode_half_float_weight_slots` is read back, per format, exactly the
    way `_get_weights` reconstructs it. Every one of these formats derives
    its last slot from the remainder rather than a written field, and a
    1-weight format has no weight field at all, so its single slot is a
    full weight.
    """
    if max_bones_per_vertex == 1:
        return [1.0]
    position_w, packed_weights, packed_weights_2 = _encode_half_float_weight_slots(
        weight_values, max_bones_per_vertex)
    weights = [position_w / 32767]
    if max_bones_per_vertex == 8:
        weights.extend(w / 255 for w in packed_weights)
        weights.extend(unpack("e", w)[0] for w in packed_weights_2)
        weights.append(1.0 - sum(weights))
    elif max_bones_per_vertex == 4:
        weights.extend(unpack("e", w)[0] for w in packed_weights)
        weights.append(round(1.0 - sum(weights), 3))
    else:
        weights.append(1.0 - weights[0])
    return weights


def _bones_with_exported_weight(influence_list, max_bones_per_vertex, half_float):
    """
    The bone indices the exported vertex data really skins a vertex to.

    A vertex counts towards a bone's weight bound exactly when the game
    ends up with a non-zero weight for that bone, so this runs the
    exporter's own truncate/normalize/quantize and then reads the result
    back the way `_get_weights` does, instead of testing the raw
    vertex-group weight: normalizing can lift a weight far below one
    quantization step into a substantial exported one, and quantizing can
    drop a small one to nothing (see issue #253).
    """
    weights_data = _process_vertex_weights(
        influence_list, max_bones_per_vertex, half_float)
    if not weights_data:
        return set()
    if not half_float:
        return {bone_index for bone_index, weight in weights_data if weight > 0}

    weight_values = [w for _, w in weights_data]
    weight_values.extend([0] * (max_bones_per_vertex - len(weight_values)))
    reconstructed = _reconstruct_half_float_weights(weight_values, max_bones_per_vertex)
    return {
        bone_index
        for (bone_index, _), weight in zip(weights_data, reconstructed)
        if weight > 0
    }


def _process_weights_for_export(weights_per_vertex, max_bones_per_vertex=4, half_float=False):
    """
    Given a dict `weights_per_vertex` with vertex_indices as keys and
    a list of tuples (bone_index, weight_value), iterate over values
    and process them to make them mtframework friendly:
    1) Limit bone weights: keep only up to `max_bones` elements, discarding the pairs that have the
       lowest influence. This is actually a limitation in albam for lack of
       understanding on how the engine treats vertices with more than 4 bone influencing it
    2) Normalize weights: make all weights sum up 1
    3) float to byte: convert the (-1.0, 1.0) to (0, 255)
    """
    new_weights_per_vertex = {}
    for vertex_index, influence_list in weights_per_vertex.items():
        weights_data = _process_vertex_weights(
            influence_list, max_bones_per_vertex, half_float)
        if weights_data is None:
            continue
        new_weights_per_vertex[vertex_index] = weights_data

    return new_weights_per_vertex


def _vec4(mod_cls, parent, x, y, z, w):
    v = mod_cls.Vec4(_parent=parent, _root=parent._root)
    v.x, v.y, v.z, v.w = x, y, z, w
    return v


def _matrix4x4(mod_cls, parent, rows):
    m = mod_cls.Matrix4x4(_parent=parent, _root=parent._root)
    m.row_1 = _vec4(mod_cls, m, *rows[0])
    m.row_2 = _vec4(mod_cls, m, *rows[1])
    m.row_3 = _vec4(mod_cls, m, *rows[2])
    m.row_4 = _vec4(mod_cls, m, *rows[3])
    return m


def _weight_bound(dst_mod, meshes_data, bone_id, positions_cm):
    """A weight bound record over `positions_cm`, an (N, 3) array of file-space
    positions already relative to the bone (or to the model for bone 255)."""
    mins = positions_cm.min(axis=0)
    maxs = positions_cm.max(axis=0)
    lengths = (maxs - mins) / 2
    center = (mins + maxs) / 2
    radius = float(np.sqrt(((positions_cm - center) ** 2).sum(axis=1)).max())

    wb = dst_mod.WeightBound(_parent=meshes_data, _root=meshes_data._root)
    wb.bone_id = bone_id
    wb.padding = dst_mod.Vec3(_parent=wb, _root=wb._root)
    wb.padding.x = wb.padding.y = wb.padding.z = 0.0
    wb.bsphere = _vec4(dst_mod, wb, float(center[0]), float(center[1]), float(center[2]), radius)
    wb.bbox_min = _vec4(dst_mod, wb, float(mins[0]), float(mins[1]), float(mins[2]), 0.0)
    wb.bbox_max = _vec4(dst_mod, wb, float(maxs[0]), float(maxs[1]), float(maxs[2]), 0.0)
    # TODO: calculate oabb
    # I spotted disappearing meshes (e.g. hands) in some cut-scenes (re5-> "The Wetlands")
    # References:
    # - https://github.com/patmo141/object_bounding_box
    # - https://github.com/AsteriskAmpersand/Mod3-MHW-Importer/tree/master/boundingbox
    # thanks to AsteriskAmpersand for math help
    wb.oabb = _matrix4x4(dst_mod, wb, (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (float(center[0]), float(center[1]), float(center[2]), 1),
    ))
    # TODO: dimension/length is wrongly calculated in vertex groups?
    wb.oabb_dimension = _vec4(dst_mod, wb, float(lengths[0]), float(lengths[1]), float(lengths[2]), 0.0)
    wb._check()
    return wb


def _calculate_weight_bounds(dst_mod, meshes_data, positions, influences, bone_heads_cm,
                             max_bones_per_vertex, half_float):
    """The weight bounds of one mesh: one per bone the exported weights skin
    it to, from the vertices in that bone's space, or a single bone-255 bound
    over the whole mesh when there is no armature.

    `positions` is (N, 3) in scene metres, `influences` the per-vertex
    [(bone_index, weight), ...] lists, `bone_heads_cm` bone index -> rest
    position in file units, or None for a static model.
    """
    positions_cm = np.asarray(positions, dtype=np.float64) * SCALE
    if bone_heads_cm is None:
        return [_weight_bound(dst_mod, meshes_data, 255, positions_cm)]

    vertices_per_bone = {}
    for vertex_index, influence_list in enumerate(influences):
        if not influence_list:
            continue
        for bone_index in _bones_with_exported_weight(influence_list, max_bones_per_vertex, half_float):
            vertices_per_bone.setdefault(bone_index, []).append(vertex_index)

    weight_bounds = []
    for bone_index in sorted(vertices_per_bone):
        if bone_index not in bone_heads_cm:
            continue
        in_bone_space = positions_cm[vertices_per_bone[bone_index]] - bone_heads_cm[bone_index]
        weight_bounds.append(_weight_bound(dst_mod, meshes_data, bone_index, in_bone_space))
    return weight_bounds


def create_bone_palettes(mod_version, bone_sets):
    """The 153/156 bone palettes for meshes whose bones are `bone_sets`,
    one set of bone indices per mesh in export order: meshes are packed
    into palettes of at most 32 bones, in order. Returns
    {frozenset(mesh indices): sorted bone indices}, empty on other versions.
    """
    if mod_version not in VERSIONS_USE_BONE_PALETTES:
        return {}
    bone_palette_dicts = []

    bone_palette = {'mesh_indices': set(), 'bone_indices': set()}
    for i, (mesh_name, bone_indices) in enumerate(bone_sets):
        if len(bone_indices) > MAX_BONE_PALETTE_SIZE:
            raise AlbamCheckFailure(
                message=f"Mesh {mesh_name!r} is influenced by too many bones",
                details=(f"its vertex groups reference {len(bone_indices)} distinct bones, "
                         f"the format allows at most {MAX_BONE_PALETTE_SIZE} per mesh"),
                solution=(f"Split the mesh so each piece uses at most {MAX_BONE_PALETTE_SIZE} "
                          "bones, or merge some of its vertex groups"),
            )

        current = bone_palette['bone_indices']
        potential = current.union(bone_indices)
        if len(potential) > MAX_BONE_PALETTE_SIZE:
            bone_palette_dicts.append(bone_palette)
            bone_palette = {'mesh_indices': {i},
                            'bone_indices': set(bone_indices)}
        else:
            bone_palette['mesh_indices'].add(i)
            bone_palette['bone_indices'].update(bone_indices)

    bone_palette_dicts.append(bone_palette)

    return OrderedDict([(frozenset(bp['mesh_indices']), sorted(bp['bone_indices']))
                        for bp in bone_palette_dicts])


def _raise_vertex_count_failure(mesh_name, num_vertices, vertex_position):
    if vertex_position:
        details = (f"it starts at vertex index {vertex_position} of a block it shares with "
                   f"the meshes before it of the same vertex format, and its {num_vertices} "
                   f"vertices would take that block past index {MAX_MESH_U2}")
        solution = ("Enable \"Don't group meshes by vertex format\" in the export settings so "
                    "each mesh gets its own vertex block, or split the meshes into smaller pieces")
    else:
        details = (f"it has {num_vertices} vertices after splitting at UV seams and hard "
                   f"edges, the format allows at most {MAX_MESH_U2} per mesh")
        solution = "Split the mesh into smaller pieces"
    raise AlbamCheckFailure(
        message=f"Mesh {mesh_name!r} has too many vertices for the format",
        details=details,
        solution=solution,
    )


def _check_bone_budget(num_bones):
    if num_bones > MAX_ADDRESSABLE_BONES:
        raise AlbamCheckFailure(
            message=f"The armature has {num_bones} bones, more than the format can address",
            details=(f"a bone refers to its parent and its mirror with one byte each, and "
                     f"255 of the 256 values means \"none\", so no bone past index "
                     f"{MAX_ADDRESSABLE_BONES - 1} can be named by another"),
            solution="Remove bones until the skeleton is within the limit",
        )


def _check_bone_map(bone_map, anim_ids):
    """Every id a bone claims has to lead back to a bone.

    Two bones sharing an id is normal and the map keeps the last of them, so the
    check is that each id resolves at all, not that it resolves to a particular
    bone. What it catches is an id whose slot was never written, which would
    leave an animation targeting that id driving nothing.
    """
    for bone_index, anim_id in enumerate(anim_ids):
        if bone_map[anim_id] == UNMAPPED_ANIM_ID:
            raise AlbamCheckFailure(
                message=f"Bone {bone_index} claims animation id {anim_id}, which maps to nothing",
                details="the table that resolves an animation id to a bone has no entry for it, "
                        "so every animation addressing that id would drive no bone at all",
                solution="Report this: the exported skeleton is inconsistent with itself",
            )


def _build_bone_map(anim_ids):
    """The 256-byte reverse table an .lmt is resolved through: id -> bone index.

    Rebuilt from the ids rather than copied, which is exact: assigning in bone
    order reproduces all 404 re5 models byte for byte. Two bones sharing an id
    is normal rather than a mistake - 280 of those models give a second bone
    the id 0 - and the shipped tables always resolve such an id to the *last*
    bone holding it, which is what overwriting in bone order does.
    """
    bone_map = bytearray([UNMAPPED_ANIM_ID] * 256)
    for bone_index, anim_id in enumerate(anim_ids):
        bone_map[anim_id] = bone_index
    return bytes(bone_map)


class Skeleton:
    """The scene's joints in the model's bone order, with what the .mod needs
    of each: parent, rest transforms in file units, and the ids the scene's
    extras carry.

    The order is `bone_order` when the root's extras name one (the Blender
    armature's own bone order, which is what every bone index in the file and
    in the vertex groups means), otherwise the skin's joint order.
    """

    def __init__(self, scene, root, skin):
        self.scene = scene
        joints = skin.joints
        names = [scene.nodes[j].name for j in joints]
        root_extras = scene.nodes[root].extras.get(EXTRAS_KEY, {})
        bone_order = root_extras.get("bone_order") or names
        node_of = {scene.nodes[j].name: j for j in joints}
        self.names = list(bone_order)
        self.nodes = [node_of[name] for name in self.names if name in node_of]
        if len(self.nodes) != len(self.names):
            missing = [name for name in self.names if name not in node_of]
            raise AlbamCheckFailure(
                message="The exported armature and the exported skin disagree",
                details=f"bones {missing} are in the armature but not among the skin's joints",
                solution="Report this: the scene is inconsistent with itself",
            )
        self.index_of = {name: i for i, name in enumerate(self.names)}
        # joint slot (what JOINTS_n holds) -> bone index, or None for a joint
        # outside the skeleton (Blender's neutral bone for unweighted vertices)
        self.bone_of_joint = [self.index_of.get(scene.nodes[j].name) for j in joints]

        parents = scene.parents()
        self.parent_ids = []
        self.local_matrices = []
        self.world_matrices = []
        for node_index in self.nodes:
            parent = parents[node_index]
            parent_bone = self.index_of.get(scene.nodes[parent].name) if parent is not None else None
            if parent_bone is not None and parent not in self.nodes:
                parent_bone = None
            self.parent_ids.append(NO_PARENT if parent_bone is None else parent_bone)
            local = scene.nodes[node_index].local_matrix
            self.local_matrices.append(local)
            self.world_matrices.append(scene.world_matrix(node_index, up_to=root))

    def __len__(self):
        return len(self.nodes)

    def extras(self, bone_index):
        return self.scene.nodes[self.nodes[bone_index]].extras.get(EXTRAS_KEY, {})

    def heads_cm(self):
        """bone index -> rest position in file units."""
        return {i: m[:3, 3] * SCALE for i, m in enumerate(self.world_matrices)}

    def exportable_count(self):
        """How many of the rig's bones belong in the model.

        Animation import gives a bone of its own to the second track in a
        block that keys an id already taken, and names its id "<id>_<n>".
        Those exist to carry animation and are not part of the skeleton the
        model describes, so they are left out. Import appends them, so they
        sit at the end; if one does not, the rest of the export would
        silently shift every bone index after it, and that is an error
        rather than something to work around.
        """
        kept = 0
        for i, name in enumerate(self.names):
            raw = str(self.extras(i).get("anim_retarget", ""))
            if "_" not in raw:
                if kept != i:
                    raise AlbamCheckFailure(
                        message=f"Bone {name!r} sits after a bone that only carries animation",
                        details=("bones added by animation import are skipped on export, and they are "
                                 "expected at the end of the armature; one earlier in the order would "
                                 "shift the index of every bone after it"),
                        solution="Move the bone before any animation-only bone, or delete those bones",
                    )
                kept += 1
        return kept

    def anim_map_ids(self, num_bones):
        """Each bone's idx_anim_map, read off the rig instead of the source file."""
        if len(self.names) < num_bones:
            raise AlbamCheckFailure(
                message="The armature has fewer bones than the model expects",
                details=f"the model declares {num_bones} bones, the armature has {len(self.names)}",
                solution="Export the armature the model was imported with, without deleting bones",
            )
        ids = []
        for i in range(num_bones):
            # Animation import gives a bone of its own to the second track in a
            # block that keys an id already taken, naming it "<id>_<n>"; the id is
            # the part before the "_".
            value = str(self.extras(i).get("anim_retarget", "")).split("_")[0]
            if not value.isdigit() or int(value) > 255:
                raise AlbamCheckFailure(
                    message=f"Bone {self.names[i]!r} has no usable animation id",
                    details=(f"its Anim Retarget is {value!r}, which is not a number in 0-255. "
                             f"Animations address bones by this id, so a bone without one would "
                             f"be invisible to every animation"),
                    solution=("Set Anim Retarget on the bone in the Bone tab, or re-import the "
                              "model to have it filled in"),
                )
            ids.append(int(value))
        return ids

    def parent_ids_for(self, num_bones):
        ids = []
        for i in range(num_bones):
            parent = self.parent_ids[i]
            if parent != NO_PARENT and parent >= num_bones:
                raise AlbamCheckFailure(
                    message=f"Bone {self.names[i]!r} is parented outside the exported skeleton",
                    details=(f"its parent {self.names[parent]!r} is not among the first {num_bones} bones, "
                             f"so there is no index to write for it"),
                    solution="Re-parent the bone within the model's own skeleton before exporting",
                )
            ids.append(parent)
        return ids

    def mirror_ids(self, num_bones, src_mod):
        """Each bone's idx_mirror, resolved from the name the rig carries.

        A rig imported before Mirror Bone existed (0.5.0 and earlier) carries no
        mirror on any bone, which would write every bone as unmirrored. Such a rig
        keeps the source file's mirrors instead; a source with no mirrors at all
        comes out the same either way.
        """
        mirrors = [str(self.extras(i).get("mirror", "")) for i in range(num_bones)]
        if not any(mirrors):
            src_bones = src_mod.bones_data.bones_hierarchy if src_mod.bones_data else []
            return [src_bones[i].idx_mirror if i < len(src_bones) else NO_MIRROR
                    for i in range(num_bones)]
        ids = []
        for i, name in enumerate(mirrors):
            if not name:
                ids.append(NO_MIRROR)
                continue
            if name not in self.index_of:
                raise AlbamCheckFailure(
                    message=f"Bone {self.names[i]!r} names a mirror that is not in the skeleton",
                    details=f"its Mirror Bone is {name!r}, which is not one of the exported bones",
                    solution="Point Mirror Bone at a bone of this skeleton, or clear it if the "
                             "bone sits on the midline",
                )
            ids.append(self.index_of[name])
        return ids

    def furthest_vertex_distances(self, num_bones, mesh_inputs):
        """Each bone's `furthest_vertex_distance`: how far the furthest vertex it
        influences sits, in file units, zero for a bone nothing skins to."""
        heads = self.heads_cm()
        furthest = [0.0] * num_bones
        for mesh_input in mesh_inputs:
            if not mesh_input.skinned:
                continue
            positions_cm = mesh_input.primitive.attributes["POSITION"].astype(np.float64) * SCALE
            for vertex_index, influence_list in enumerate(mesh_input.influences):
                for bone_index, weight in influence_list:
                    if not weight or bone_index >= num_bones:
                        continue
                    distance = float(np.linalg.norm(positions_cm[vertex_index] - heads[bone_index]))
                    if distance > furthest[bone_index]:
                        furthest[bone_index] = distance
        return furthest

    def transforms(self, dst_mod):
        """(parent_distance, location, parent-space matrix, inverse bind matrix)
        per bone, the matrices as row lists in the file's row-vector layout."""
        magnitudes = []
        locations = []
        parent_space = []
        inverse_bind = []
        bbox_affected = dst_mod.header.version in VERSIONS_BONES_BBOX_AFFECTED
        if bbox_affected:
            min_length = abs(min(dst_mod.bbox_min.x, dst_mod.bbox_min.y, dst_mod.bbox_min.z))
            max_length = max(abs(dst_mod.bbox_max.x), abs(dst_mod.bbox_max.y), abs(dst_mod.bbox_max.z))
            dimension = min_length + max_length
            translation_matrix = np.zeros((4, 4))
            translation_matrix[:3, 3] = (dst_mod.bbox_min.x, dst_mod.bbox_min.y, dst_mod.bbox_min.z)
            scale_matrix = np.diag([dimension] * 3 + [1.0])
        for local, world in zip(self.local_matrices, self.world_matrices):
            parent_space_matrix = local.copy()
            parent_space_matrix[:3, 3] *= SCALE
            inverse_space = world.copy()
            inverse_space[:3, 3] *= SCALE
            if bbox_affected:
                # shift the matrix to the bbox space and scale it
                ibbox_matrix = np.linalg.inv(inverse_space)
                ibbox_matrix = ibbox_matrix @ scale_matrix + translation_matrix
                inverse_bind.append(ibbox_matrix.T)
            else:
                inverse_bind.append(np.linalg.inv(inverse_space).T)
            translation = parent_space_matrix[:3, 3]
            locations.append(translation)
            parent_space.append(parent_space_matrix.T)
            magnitudes.append(math.sqrt(float((translation ** 2).sum())))
        return magnitudes, locations, parent_space, inverse_bind


def merge_split_vertices(primitive):
    """One vertex per (source vertex, UVs, color): what the .mod needs and
    what albam's own export vertex table produced.

    Blender's glTF exporter splits a vertex wherever any corner attribute
    differs, normals included, and its custom normals come back from storage
    a little different per corner, so a vertex that was one in the file
    comes out as several. The source vertex rides along in VERTEX_ATTRIBUTE;
    without it the primitive is left as it is. The first split's normal and
    tangent are kept, the way the vertex table kept the first corner's.
    """
    attributes = primitive.attributes
    if VERTEX_ATTRIBUTE not in attributes:
        return primitive
    count = primitive.vertex_count
    columns = [np.rint(attributes[VERTEX_ATTRIBUTE].reshape(count, -1)).astype(np.int64)]
    for name in sorted(attributes):
        if name.startswith("TEXCOORD_") or name.startswith("COLOR_") or name == COLOR_ATTRIBUTE:
            values = attributes[name].reshape(count, -1).astype(np.float64)
            columns.append(np.rint(values * 1e6).astype(np.int64))
    key = np.concatenate(columns, axis=1)
    _, first, inverse = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inverse = inverse.reshape(-1)
    if len(first) == count:
        merged_attributes = {k: v for k, v in attributes.items() if k != VERTEX_ATTRIBUTE}
        return Primitive(attributes=merged_attributes, indices=primitive.indices,
                         material=primitive.material, mode=primitive.mode)
    merged_attributes = {
        name: array[first] for name, array in attributes.items() if name != VERTEX_ATTRIBUTE}
    indices = None if primitive.indices is None else inverse[primitive.indices].astype(np.uint32)
    return Primitive(attributes=merged_attributes, indices=indices,
                     material=primitive.material, mode=primitive.mode)


def _mesh_inputs(scene, root, skeleton):
    """Every mesh node under the root, in export order, as MeshInput."""
    root_extras = scene.nodes[root].extras.get(EXTRAS_KEY, {})
    node_indices = scene.mesh_nodes()
    mesh_order = root_extras.get("mesh_order")
    if mesh_order:
        by_name = {scene.nodes[i].name: i for i in node_indices}
        node_indices = [by_name[name] for name in mesh_order if name in by_name]

    inputs = []
    for node_index in node_indices:
        node = scene.nodes[node_index]
        mesh = scene.meshes[node.mesh]
        node_extras = node.extras.get(EXTRAS_KEY, {})
        mesh_extras = mesh.extras.get(EXTRAS_KEY, {})
        for primitive in mesh.primitives:
            if primitive.indices is None or primitive.mode != 4:
                continue
            primitive = merge_split_vertices(primitive)
            material_name = node_extras.get("material_name") or mesh_extras.get("material_name")
            if material_name is None and primitive.material is not None:
                material_name = scene.materials[primitive.material].name
            influences = _influences(primitive, skeleton)
            inputs.append(MeshInput(
                name=node.name,
                primitive=primitive,
                material_name=material_name,
                mesh_props=node_extras.get("mesh_props") or mesh_extras.get("mesh_props") or {},
                material_props=node_extras.get("material_props") or mesh_extras.get("material_props") or {},
                skinned=node.skin is not None,
                influences=influences,
            ))
    return inputs


def _influences(primitive, skeleton):
    """Per vertex [(bone_index, weight), ...] for the weights the primitive
    carries, with joints outside the skeleton dropped."""
    attributes = primitive.attributes
    count = len(attributes["POSITION"])
    if "JOINTS_0" not in attributes or skeleton is None:
        return [[] for _ in range(count)]
    joints = np.concatenate(
        [attributes[f"JOINTS_{k}"] for k in range(4) if f"JOINTS_{k}" in attributes], axis=1)
    weights = np.concatenate(
        [attributes[f"WEIGHTS_{k}"] for k in range(4) if f"WEIGHTS_{k}" in attributes], axis=1)
    bone_of_joint = skeleton.bone_of_joint
    influences = []
    for vertex_joints, vertex_weights in zip(joints.tolist(), weights.tolist()):
        pairs = []
        for joint, weight in zip(vertex_joints, vertex_weights):
            if weight <= 0:
                continue
            bone_index = bone_of_joint[joint] if joint < len(bone_of_joint) else None
            if bone_index is None:
                continue
            pairs.append((bone_index, weight))
        influences.append(pairs)
    return influences


def _init_mod_header(src_mod, dst_mod):
    dst_mod_header = dst_mod.ModHeader(_parent=dst_mod, _root=dst_mod._root)
    dst_mod_header.__dict__.update(dict(
        ident=b"MOD\x00",
        version=src_mod.header.version,
        revision=1 if src_mod.header.version != 153 else 0,
        num_bones=0,
        num_meshes=0,
        num_materials=0,
        num_vertices=0,
        num_indices=0,
        num_triangles=0,
        size_vertex_buffer=0,
        num_groups=src_mod.header.num_groups,
        offset_bones_data=0,
        offset_groups=0,
        offset_materials_data=0,
        offset_meshes_data=0,
        offset_vertex_buffer=0,
        offset_index_buffer=0,
    ))

    if dst_mod_header.version in VERSIONS_USE_BONE_PALETTES:
        dst_mod_header.num_bone_palettes = 0
        dst_mod_header.size_vertex_buffer_2 = 0
        dst_mod_header.num_textures = 0
        dst_mod_header.offset_vertex_buffer_2 = 0
    if dst_mod_header.version in (210, 211, 212):
        dst_mod_header.revision = 0
        dst_mod_header.reserved_01 = 0

    dst_mod_header._check()
    dst_mod.header = dst_mod_header
    return dst_mod_header


def _serialize_top_level_mod(app_id, mesh_inputs, src_mod, dst_mod):
    positions = np.concatenate([m.primitive.attributes["POSITION"] for m in mesh_inputs]).astype(np.float64)
    bbox_min = positions.min(axis=0)
    bbox_max = positions.max(axis=0)
    center = (bbox_min + bbox_max) / 2
    radius = float(np.sqrt(((positions - center) ** 2).sum(axis=1)).max())

    center_cm = center * SCALE
    bbox_min_cm = bbox_min * SCALE
    bbox_max_cm = bbox_max * SCALE
    dst_mod.bsphere = _vec4(dst_mod, dst_mod, center_cm[0], center_cm[1], center_cm[2], radius * SCALE)
    # .w is padding, not a coordinate (TODO: research)
    dst_mod.bbox_min = _vec4(dst_mod, dst_mod, bbox_min_cm[0], bbox_min_cm[1], bbox_min_cm[2], 0)
    dst_mod.bbox_max = _vec4(dst_mod, dst_mod, bbox_max_cm[0], bbox_max_cm[1], bbox_max_cm[2], 0)

    dst_mod.model_info = dst_mod.ModelInfo(_parent=dst_mod, _root=dst_mod._root)
    dst_mod.model_info.middist = src_mod.model_info.middist
    dst_mod.model_info.lowdist = src_mod.model_info.lowdist
    dst_mod.model_info.light_group = src_mod.model_info.light_group
    dst_mod.model_info.strip_type = src_mod.model_info.strip_type
    dst_mod.model_info.memory = src_mod.model_info.memory
    dst_mod.model_info.reserved = src_mod.model_info.reserved

    if src_mod.header.version == 153:
        dst_mod.reserved_01 = src_mod.reserved_01
        dst_mod.reserved_02 = src_mod.reserved_02

    if src_mod.header.version == 156:
        dst_mod.rcn_header = dst_mod.RcnHeader(_parent=dst_mod, _root=dst_mod._root)
        dst_mod.reserved_01 = src_mod.reserved_01
        dst_mod.reserved_02 = src_mod.reserved_02
        dst_mod.rcn_header.ptri = src_mod.rcn_header.ptri
        dst_mod.rcn_header.pvtx = src_mod.rcn_header.pvtx
        dst_mod.rcn_header.ptb = src_mod.rcn_header.ptb
        dst_mod.rcn_header.num_tri = 0
        dst_mod.rcn_header.num_vtx = 0
        dst_mod.rcn_header.num_tbl = 0
        dst_mod.rcn_header.parts = 0
        dst_mod.rcn_header.reserved = 0
        dst_mod.rcn_tables = []
        dst_mod.rcn_vertices = []
        dst_mod.rcn_trianlges = []

    if src_mod.header.version in (210, 212) or app_id == "umvc3":
        dst_mod.num_weight_bounds = 0


def _serialize_bones_data(skeleton, mesh_inputs, src_mod, dst_mod, app_id, settings, bone_palettes):
    if skeleton is None:
        return None
    export_bones = settings.export_bones
    bone_magnitudes, bone_transforms, parent_space_matrix, invert_bind_matrix = skeleton.transforms(dst_mod)
    if export_bones:
        # The rig decides how many bones there are, which is what lets one gain
        # bones the file it came from never had.
        dst_mod.header.num_bones = skeleton.exportable_count()
    else:
        dst_mod.header.num_bones = src_mod.header.num_bones
    num_bones = dst_mod.header.num_bones
    bones_data = dst_mod.BonesData(_parent=dst_mod, _root=dst_mod._root)
    if export_bones:
        _check_bone_budget(num_bones)
        anim_map_ids = skeleton.anim_map_ids(num_bones)
        parent_ids = skeleton.parent_ids_for(num_bones)
        mirror_ids = skeleton.mirror_ids(num_bones, src_mod)
        furthest_vertex = skeleton.furthest_vertex_distances(num_bones, mesh_inputs)
        bones_data.bone_map = _build_bone_map(anim_map_ids)
        _check_bone_map(bones_data.bone_map, anim_map_ids)
    else:
        anim_map_ids = parent_ids = mirror_ids = furthest_vertex = None
        bones_data.bone_map = src_mod.bones_data.bone_map
    bones_data.bones_hierarchy = []
    bones_data.parent_space_matrices = []
    bones_data.inverse_bind_matrices = []

    if bone_palettes:
        bones_data.bone_palettes = []
        dst_mod.header.num_bone_palettes = len(bone_palettes)
        for bp in bone_palettes.values():
            bone_palette = dst_mod.BonePalette(_parent=bones_data, _root=bones_data._root)
            bone_palette.unk_01 = len(bp)
            if len(bp) != MAX_BONE_PALETTE_SIZE:
                bp = bp + [0] * (MAX_BONE_PALETTE_SIZE - len(bp))
            bone_palette.indices = bp
            bones_data.bone_palettes.append(bone_palette)
            bone_palette._check()

    for i in range(num_bones):
        # Only the branch that copies needs the original, and it is not there to
        # read once the rig has more bones than the file did.
        src_bone = None if export_bones else src_mod.bones_data.bones_hierarchy[i]
        bone = dst_mod.Bone(_parent=bones_data, _root=bones_data._root)
        bone.idx_anim_map = anim_map_ids[i] if export_bones else src_bone.idx_anim_map
        bone.idx_parent = parent_ids[i] if export_bones else src_bone.idx_parent
        bone.idx_mirror = mirror_ids[i] if export_bones else src_bone.idx_mirror
        bone.padding = BONE_RECORD_PADDING if export_bones else src_bone.padding
        bone.furthest_vertex_distance = (
            furthest_vertex[i] if export_bones else src_bone.furthest_vertex_distance)
        bone.parent_distance = bone_magnitudes[i] if export_bones else src_bone.parent_distance
        loc = dst_mod.Vec3(_parent=bone, _root=bone._root)
        if export_bones:
            loc.x, loc.y, loc.z = (float(c) for c in bone_transforms[i])
        else:
            loc.x = src_bone.location.x
            loc.y = src_bone.location.y
            loc.z = src_bone.location.z
        bone.location = loc

        if export_bones:
            m = _matrix4x4(dst_mod, bones_data, parent_space_matrix[i].tolist())
        else:
            src_m = src_mod.bones_data.parent_space_matrices[i]
            m = _matrix4x4(dst_mod, bones_data, (
                (src_m.row_1.x, src_m.row_1.y, src_m.row_1.z, src_m.row_1.w),
                (src_m.row_2.x, src_m.row_2.y, src_m.row_2.z, src_m.row_2.w),
                (src_m.row_3.x, src_m.row_3.y, src_m.row_3.z, src_m.row_3.w),
                (src_m.row_4.x, src_m.row_4.y, src_m.row_4.z, src_m.row_4.w),
            ))

        if export_bones:
            m2 = _matrix4x4(dst_mod, bones_data, invert_bind_matrix[i].tolist())
        else:
            src_m2 = src_mod.bones_data.inverse_bind_matrices[i]
            rows = [
                [src_m2.row_1.x, src_m2.row_1.y, src_m2.row_1.z, src_m2.row_1.w],
                [src_m2.row_2.x, src_m2.row_2.y, src_m2.row_2.z, src_m2.row_2.w],
                [src_m2.row_3.x, src_m2.row_3.y, src_m2.row_3.z, src_m2.row_3.w],
                [src_m2.row_4.x, src_m2.row_4.y, src_m2.row_4.z, src_m2.row_4.w],
            ]
            if dst_mod.header.version in VERSIONS_BONES_BBOX_AFFECTED:
                # unapply transforms and apply the ones from the bbox to export
                # TODO: avoid doing this if bbox didn´t change
                src_bbox_data = _create_bbox_data(src_mod)
                dst_bbox_data = _create_bbox_data(dst_mod)
                r1x = round(src_m2.row_1.x - src_bbox_data.dimension + 1, 1)
                r2y = round(src_m2.row_2.y - src_bbox_data.dimension + 1, 1)
                r3z = round(src_m2.row_3.z - src_bbox_data.dimension + 1, 1)
                rows[0][0] = round(r1x + dst_bbox_data.dimension - 1, 1)
                rows[1][1] = round(r2y + dst_bbox_data.dimension - 1, 1)
                rows[2][2] = round(r3z + dst_bbox_data.dimension - 1, 1)
                rows[3][0] = src_m2.row_4.x - src_bbox_data.min_x + dst_bbox_data.min_x
                rows[3][1] = src_m2.row_4.y - src_bbox_data.min_y + dst_bbox_data.min_y
                rows[3][2] = src_m2.row_4.z - src_bbox_data.min_z + dst_bbox_data.min_z
            m2 = _matrix4x4(dst_mod, bones_data, rows)

        bones_data.bones_hierarchy.append(bone)
        bones_data.parent_space_matrices.append(m)
        bones_data.inverse_bind_matrices.append(m2)

    bones_data._check()
    return bones_data


def _serialize_groups(src_mod, dst_mod):
    groups = []
    for i in range(dst_mod.header.num_groups):
        src_group = src_mod.groups[i]
        g = dst_mod.Group(_parent=dst_mod, _root=dst_mod._root)
        g.group_index = src_group.group_index
        g.reserved = [src_group.reserved[0],
                      src_group.reserved[1],
                      src_group.reserved[2],
                      ]
        g.pos = dst_mod.Vec3(_parent=g, _root=g._root)
        g.pos.x = src_group.pos.x
        g.pos.y = src_group.pos.y
        g.pos.z = src_group.pos.z
        g.radius = src_group.radius

        groups.append(g)
    return groups


def _color_to_rgba_bytes(color):
    # source is (unusually) stored/expected as b, g, r, a - preserved from
    # the pre-existing behavior of the function this replaced
    b, g, r, a = color
    return (round(r * 255), round(g * 255), round(b * 255), round(a * 255))


def _byte_vector(values):
    """A direction in [-1, 1] as the file's bytes, NaNs as zeros."""
    out = []
    for v in values:
        try:
            out.append(max(0, min(255, round(((v * 0.5) + 0.5) * 255))))
        except ValueError:
            out.append(0)
    return out


def _vertex_format_for(mesh_input, dst_mod, has_bones):
    if dst_mod.header.version in (153, 156):
        vertex_format = int(mesh_input.material_props["vtype"], 16)
        skin_function = int(mesh_input.material_props["func_skin"], 16)
        return vertex_format, skin_function
    stored = mesh_input.mesh_props.get("vertex_format")
    try:
        stored_vertex_format = int(stored, 16) if isinstance(stored, str) else stored
    except (TypeError, ValueError):
        stored_vertex_format = None
    default_vertex_format = DEFAULT_VERTEX_FORMAT_SKIN if has_bones else DEFAULT_VERTEX_FORMAT_NONSKIN
    vertex_format = stored_vertex_format
    if vertex_format not in VERTEX_FORMATS_MAPPER:
        vertex_format = default_vertex_format
    return vertex_format, None


def _export_vertices(app_id, mesh_input, mesh, mesh_bone_palette, dst_mod, bbox_data):
    primitive = mesh_input.primitive
    attributes = primitive.attributes
    vertex_count = primitive.vertex_count
    max_bones_per_vertex = max((len(pairs) for pairs in mesh_input.influences), default=0)
    vtx_stream_2 = None
    vtx_stride_2 = 0
    has_vertex_buffer_2 = False
    has_bones = bool(dst_mod.header.num_bones)

    vertex_format, skin_function = _vertex_format_for(mesh_input, dst_mod, has_bones)
    if dst_mod.header.version in (153, 156):
        if vertex_format == 0x1 and skin_function == 0x4:
            has_vertex_buffer_2 = True
            vtx_stride_2 = 8
            VertexBuff2Cls = Mod156.Vertex28
        VertexCls = VERTEX_FORMATS_MAPPER[vertex_format]
        vtx_stride = 32
    else:
        VertexCls = VERTEX_FORMATS_MAPPER.get(vertex_format)
        vtx_stride = VertexCls().size_

    MAX_BONES, weight_half_float = _weight_export_params(dst_mod, vertex_format)
    # It breaks index serealization without clamping
    if max_bones_per_vertex > MAX_BONES:
        max_bones_per_vertex = MAX_BONES
    weights_per_vertex = _process_weights_for_export(
        dict(enumerate(mesh_input.influences)), max_bones_per_vertex=MAX_BONES, half_float=weight_half_float)
    uv_slots_used = (
        vertex_format not in VERTEX_FORMATS_BRIDGE,
        vertex_format in VERTEX_FORMATS_UV2,
        vertex_format in VERTEX_FORMATS_UV3,
        vertex_format in VERTEX_FORMATS_UV4,
    )
    uvs = [attributes.get(f"TEXCOORD_{i}") for i in range(4)]
    for layer_index, used in enumerate(uv_slots_used):
        if used:
            _check_uv_range(mesh_input.name, uvs[layer_index], layer_index)

    positions = attributes["POSITION"].astype(np.float64) * SCALE
    normals = attributes.get("NORMAL")
    tangents = attributes.get("TANGENT")
    colors = attributes.get(COLOR_ATTRIBUTE)
    if colors is None:
        colors = attributes.get("COLOR_0")

    vtx_stream = KaitaiStream(BytesIO(bytearray(vtx_stride * vertex_count)))
    if has_vertex_buffer_2:
        vtx_stream_2 = KaitaiStream(BytesIO(bytearray(8 * vertex_count)))
    bytes_empty = b'\x00\x00'
    for vertex_index in range(vertex_count):
        vertex_struct = VertexCls(_parent=mesh, _root=mesh._root)
        tangent = _byte_vector(tangents[vertex_index][:3]) if tangents is not None else [0, 0, 0]
        if has_vertex_buffer_2:
            vertex_struct_2 = VertexBuff2Cls(_parent=mesh, _root=mesh._root)
            vertex_struct_2.occlusion = _vec4u1(dst_mod, vertex_struct_2, 255, 255, 255, 255)
            vertex_struct_2.tangent = _vec4u1(
                dst_mod, vertex_struct_2, tangent[0], tangent[1], tangent[2], 254)
        # Position types
        if has_bones:
            if MAX_BONES == 1:
                vertex_struct.position = dst_mod.Vec3S2(
                    _parent=vertex_struct, _root=vertex_struct._root)
            else:
                vertex_struct.position = dst_mod.Vec4S2(
                    _parent=vertex_struct, _root=vertex_struct._root)
        else:
            vertex_struct.position = dst_mod.Vec3(
                _parent=vertex_struct, _root=vertex_struct._root)
        # Normals types
        if dst_mod.header.version in (153, 156) or vertex_format in VERTEX_FORMATS_NORMAL4:
            vertex_struct.normal = dst_mod.Vec4U1(
                _parent=vertex_struct, _root=vertex_struct._root)
        else:
            vertex_struct.normal = dst_mod.Vec3U1(
                _parent=vertex_struct, _root=vertex_struct._root)
            vertex_struct.occlusion = 254
        # Tangents
        if vertex_format in VERTEX_FORMATS_TANGENT:
            vertex_struct.tangent = _vec4u1(dst_mod, vertex_struct, tangent[0], tangent[1], tangent[2], 254)
        # UVs
        for slot, (attr, used) in enumerate(zip(("uv", "uv2", "uv3", "uv4"), uv_slots_used)):
            if not used:
                continue
            uv_struct = dst_mod.Vec2HalfFloat(_parent=vertex_struct, _root=vertex_struct._root)
            if uvs[slot] is not None:
                # the scene's v is already the file's (top-left origin)
                uv_x, uv_y = _clean_uv(*(float(c) for c in uvs[slot][vertex_index]))
                uv_struct.u = pack('e', uv_x)
                uv_struct.v = pack('e', uv_y)
            else:
                uv_struct.u = bytes_empty
                uv_struct.v = bytes_empty
            setattr(vertex_struct, attr, uv_struct)
        # Vertex colors
        if vertex_format in VERTEX_FORMATS_RGBA:
            color = tuple(float(c) for c in colors[vertex_index]) if colors is not None else (0, 0, 0, 0)
            c = _color_to_rgba_bytes(color)
            vertex_struct.rgba = _vec4u1(dst_mod, vertex_struct, *c)
        # Vertex Alpha
        if vertex_format in VERTEX_FORMATS_VERTEX_ALPHA:
            vertex_struct.vertex_alpha = 255
        # Set Position
        xyz = tuple(float(c) for c in positions[vertex_index])
        xyz = _apply_bbox_transforms(xyz, dst_mod, bbox_data) if has_bones else xyz
        vertex_struct.position.x = xyz[0]
        vertex_struct.position.y = xyz[1]
        vertex_struct.position.z = xyz[2]
        vertex_struct.position.w = 32767  # might be changed later
        # Set Normals
        normal = _byte_vector(normals[vertex_index]) if normals is not None else [0, 0, 0]
        vertex_struct.normal.x = normal[0]
        vertex_struct.normal.y = normal[1]
        vertex_struct.normal.z = normal[2]
        if dst_mod.header.version in (153, 156) or vertex_format in VERTEX_FORMATS_NORMAL4:
            vertex_struct.normal.w = 255  # is this occlusion as well?
        # Set Weights
        if has_bones:
            weights_data = weights_per_vertex.get(vertex_index, [])  # bone index, weight value hfloat
            weight_values = [w for _, w in weights_data]
            if not weight_values:
                raise AlbamCheckFailure(
                    "The mesh object has one or more vertices with zero skin weights",
                    details=f"Object: {mesh_input.name}",
                    solution="Please move a root bone in Pose mode to detect vertices that stand still"
                    " and use weight paint brush to fix them"
                )

            weight_values.extend([0] * (MAX_BONES - len(weight_values)))  # add nulls if less than bone limit
            if mesh_bone_palette:
                bone_indices = [mesh_bone_palette.index(
                    bone_index) for bone_index, _ in weights_data]
            else:
                bone_indices = [bi for bi, _ in weights_data]
            # minmics ingame files pattern if vertex has less than max_bones_per_vertex influences
            bone_indices.extend([bone_indices[0]] * (max_bones_per_vertex - len(bone_indices)))
            # fill other empty bone indices in vertex format range with 0
            bone_indices.extend([0] * (MAX_BONES - len(bone_indices)))
            if vertex_format == 0xdb7da014:  # very strange bridge format
                bone_indices.insert(1, 128)
                bone_indices.insert(3, 128)
                # The only bridge format with no weight bytes: its first
                # weight lives in position.w and the second is the
                # remainder, the way _get_weights reads it back.
                vertex_struct.position.w = round(weight_values[0] / 255 * 32767)
            vertex_struct.bone_indices = bone_indices
            if dst_mod.header.version not in (153, 156) and vertex_format not in VERTEX_FORMATS_BRIDGE:
                if MAX_BONES == 2:
                    vertex_struct.bone_indices = [
                        pack('e', bone_indices[0]), pack('e', bone_indices[1])]
                position_w, packed_weights, packed_weights_2 = _encode_half_float_weight_slots(
                    weight_values, MAX_BONES)
                if position_w is not None:
                    vertex_struct.position.w = position_w
                if packed_weights is not None:
                    vertex_struct.weight_values = packed_weights
                if packed_weights_2 is not None:
                    vertex_struct.weight_values2 = packed_weights_2
            else:
                vertex_struct.weight_values = weight_values
        if has_vertex_buffer_2:
            check_recursive(vertex_struct_2)
            vertex_struct_2._write(vtx_stream_2)
        check_recursive(vertex_struct)
        vertex_struct._write(vtx_stream)

    return vtx_stream, vtx_stream_2, vertex_format, vtx_stride, vtx_stride_2, max_bones_per_vertex


def _vec4u1(mod_cls, parent, x, y, z, w):
    v = mod_cls.Vec4U1(_parent=parent, _root=parent._root)
    v.x, v.y, v.z, v.w = x, y, z, w
    return v


def _serialize_meshes_data(app_id, mesh_inputs, skeleton, src_mod, dst_mod, materials_map,
                           settings, bone_palettes):
    dst_mod.header.num_meshes = len(mesh_inputs)
    meshes_data = dst_mod.MeshesData(_parent=dst_mod, _root=dst_mod._root)
    meshes_data.meshes = []
    meshes_data.weight_bounds = []

    vertex_buffer = bytearray()
    vertex_buffer_2 = bytearray()
    index_buffer = bytearray()
    bbox_data = _create_bbox_data(dst_mod)
    use_strips = dst_mod.header.version in VERSIONS_USE_TRISTRIPS
    bone_heads_cm = skeleton.heads_cm() if skeleton is not None else None

    current_vertex_position = 0
    current_vertex_offset = 0
    vertex_offset_accumulated = 0
    current_vertex_offset_2 = 0
    vertex_offset_2_accumulated = 0
    current_vertex_format = None
    total_num_vertices = 0

    index_start = 0
    vertex_base = 0  # unused for now

    for mesh_index, mesh_input in enumerate(mesh_inputs):
        face_padding = 0 if app_id not in ["re5", "dd"] else 2
        mesh = dst_mod.Mesh(_parent=meshes_data, _root=meshes_data._root)
        mesh.indices__enabled = False
        mesh.vertices__enabled = False
        mesh.vertices2__enabled = False
        mesh_bone_palette = None
        mesh_bone_palette_index = None
        if bone_palettes:
            for bpi, (meshes_indices, bp) in enumerate(bone_palettes.items()):
                if mesh_index in meshes_indices:
                    mesh_bone_palette_index = bpi
                    mesh_bone_palette = bp
                    break
            else:
                raise ValueError(
                    f"Mesh {mesh_index} doesn't have a bone_palette")

        vertices, vertices2, vertex_format, vertex_stride, vertex_stride_2, max_bones_per_vertex = (
            _export_vertices(app_id, mesh_input, mesh, mesh_bone_palette, dst_mod, bbox_data)
        )
        vertex_buffer.extend(vertices.to_byte_array())
        if vertices2:
            vertex_buffer_2.extend(vertices2.to_byte_array())
        if vertex_format != current_vertex_format or settings.no_vf_grouping:
            current_vertex_offset = vertex_offset_accumulated
            current_vertex_offset_2 = vertex_offset_2_accumulated
            current_vertex_position = 0
            current_vertex_format = vertex_format

        num_vertices = mesh_input.primitive.vertex_count
        last_index = current_vertex_position + num_vertices - 1
        if num_vertices > MAX_MESH_U2 or last_index > MAX_MESH_U2:
            _raise_vertex_count_failure(mesh_input.name, num_vertices, current_vertex_position)

        triangle_list = mesh_input.primitive.indices.astype(np.int64).tolist()
        triangle_tuples = list(zip(triangle_list[0::3], triangle_list[1::3], triangle_list[2::3]))
        if use_strips:
            triangles = triangles_list_to_triangles_strip(triangle_tuples) if triangle_tuples else []
        else:
            triangles = list(chain.from_iterable(triangle_tuples))

        triangles = [e + current_vertex_position for e in triangles]
        num_indices = len(triangles)
        if app_id in ["re5", "dd"]:
            # calculate padding for indices
            if ((num_indices * 2) % 4):
                triangles.append(triangles[-1])
                face_padding += 1
            triangles.append(triangles[-1])
            triangles.append(0)

        triangles_ctypes = (ctypes.c_ushort * len(triangles))(*triangles)
        index_buffer.extend(triangles_ctypes)

        mesh_props = dict(mesh_input.mesh_props)
        if settings.force_lod255:
            mesh_props["level_of_detail"] = 255
        for attr_name, value in mesh_props.items():
            if attr_name == "vertex_format":
                continue
            setattr(mesh, attr_name, int(value, 16) if isinstance(value, str) else value)
        if "disp" not in mesh_props:
            # Checked against every mesh (132161) in every .mod-156 in the local re5 install:
            # disp is always True, no shipped file ever disables it, so it's no longer a
            # stored/editable custom property there (or on mod-153/dmc4, which shares this
            # property group). Mod21MeshCustomProperties (re0/re1/re6/rev1/rev2/dd/umvc3)
            # still has a real, user-editable disp.
            mesh.disp = 1

        if mesh_input.material_name not in materials_map:
            raise AlbamCheckFailure(
                "A mesh has a material the export did not serialize",
                details=f"Object: {mesh_input.name}, material: {mesh_input.material_name!r}",
                solution="Make sure every mesh has a material in its first slot and export again",
            )
        mesh.idx_material = materials_map[mesh_input.material_name]
        mesh.vertex_format = vertex_format
        mesh.vertex_stride = vertex_stride
        mesh.vertex_stride_2 = vertex_stride_2
        mesh.num_vertices = num_vertices
        mesh.vertex_position_2 = current_vertex_position
        mesh.vertex_byte_offset = current_vertex_offset
        mesh.index_start = index_start
        mesh.num_indices = num_indices
        mesh.vertex_base = vertex_base
        mesh.vertex_index = current_vertex_position
        mesh.first_index = current_vertex_position
        mesh.last_index = last_index
        mesh.vertex_offset_2 = current_vertex_offset_2
        mesh.idx_bone_palette = mesh_bone_palette_index
        mesh.num_weight_bounds = 1
        if app_id == "umvc3":
            mesh.padding = 0

        # DD original hack, weapon meshes invisible without it
        if settings.force_max_num_weights:
            bone_limit = VERTEX_FORMATS_BONE_LIMIT.get(vertex_format)
            if bone_limit == 4 and max_bones_per_vertex < 4:
                max_bones_per_vertex = 4
            elif bone_limit == 8 and max_bones_per_vertex < 5:
                max_bones_per_vertex = 5
        mesh.max_bones_per_vertex = max_bones_per_vertex

        if dst_mod.header.version in (153, 156):
            mesh.reserved2 = 0
            mesh.connective = 0

        mesh._check()
        meshes_data.meshes.append(mesh)
        # The same bone limit and weight encoding `_export_vertices` used, so
        # the weight bound filter agrees with what actually got exported.
        wb_max_bones, wb_half_float = _weight_export_params(dst_mod, vertex_format)
        mesh_weight_bounds = _calculate_weight_bounds(
            dst_mod, meshes_data, mesh_input.primitive.attributes["POSITION"], mesh_input.influences,
            bone_heads_cm, wb_max_bones, wb_half_float)
        meshes_data.weight_bounds.extend(mesh_weight_bounds)
        mesh.num_weight_bounds = len(mesh_weight_bounds)

        current_vertex_position += num_vertices
        vertex_offset_accumulated += (num_vertices * vertex_stride)
        vertex_offset_2_accumulated += (num_vertices * vertex_stride_2)
        index_start += (num_indices + face_padding)
        total_num_vertices += mesh.num_vertices

    if dst_mod.header.version in (153, 156, 211) and app_id != "umvc3":
        meshes_data.num_weight_bounds = len(meshes_data.weight_bounds)
    else:
        dst_mod.num_weight_bounds = len(meshes_data.weight_bounds)

    meshes_data._check()
    return meshes_data, vertex_buffer, vertex_buffer_2, index_buffer


def copy_materials_data(src_mod, app_id, root_name):
    """A material serializer that carries the source file's materials over
    unchanged: what a round trip with no Blender in it uses in place of the
    node-tree reader. Keys the map by the names `mod_to_scene` gives the
    scene's materials."""
    def serialize(dst_mod):
        dst_mod.header.num_materials = src_mod.header.num_materials
        if src_mod.header.version in VERSIONS_USE_BONE_PALETTES:
            dst_mod.header.num_textures = src_mod.header.num_textures
        dst_mod.materials_data = adopt(src_mod.materials_data, dst_mod, dst_mod)
        materials_map = {}
        for mesh in src_mod.meshes_data.meshes:
            material_hash = _get_material_hash(src_mod, mesh, app_id)
            materials_map[f"{root_name}_material_{material_hash}"] = mesh.idx_material
        return materials_map
    return serialize


def scene_to_mod(scene, src_mod, app_id, settings, serialize_materials):
    """The scene as .mod bytes of `src_mod`'s version.

    `serialize_materials(dst_mod) -> {material name: material index}` fills
    `dst_mod.materials_data` (and `num_materials`) from wherever the
    materials live - Blender node trees, or the source file - and says which
    index each scene material name got.
    """
    if len(scene.roots) != 1:
        raise AlbamCheckFailure(
            "The scene to export has to have one root object",
            details=f"it has {len(scene.roots)}",
            solution="Export one model at a time",
        )
    root = scene.roots[0]
    root_node = scene.nodes[root]
    ModCls = APPID_CLASS_MAPPER[app_id]
    dst_mod = ModCls(app_id)

    skin = None
    skinned_nodes = [i for i in scene.mesh_nodes() if scene.nodes[i].skin is not None]
    if scene.skins and skinned_nodes:
        skin = scene.skins[scene.nodes[skinned_nodes[0]].skin]
    elif scene.skins and (scene.nodes[root].extras.get(EXTRAS_KEY, {}).get("bone_order")):
        skin = scene.skins[0]
    skeleton = Skeleton(scene, root, skin) if skin is not None else None

    mesh_inputs = _mesh_inputs(scene, root, skeleton)
    if not mesh_inputs:
        raise AlbamCheckFailure(
            "There is no mesh to export",
            details=f"Object '{root_node.name}' has no mesh children",
            solution=f"Parent the meshes to the exported object '{root_node.name}'",
        )
    if skeleton is not None:
        for mesh_input in mesh_inputs:
            if not mesh_input.skinned:
                raise AlbamCheckFailure(
                    "The mesh object has no Armature modifier",
                    details=f"Object: {mesh_input.name}",
                    solution="Please add Armature modifier and set imported skeleton as Object"
                )

    _serialize_top_level_mod(app_id, mesh_inputs, src_mod, dst_mod)
    _init_mod_header(src_mod, dst_mod)

    bone_palettes = create_bone_palettes(
        src_mod.header.version,
        [(m.name, {bone_index for pairs in m.influences for bone_index, _ in pairs}) for m in mesh_inputs],
    )
    bones_data = _serialize_bones_data(
        skeleton, mesh_inputs, src_mod, dst_mod, app_id, settings, bone_palettes)
    if bones_data is not None:
        # Only assign when there is one. Assigning None still *creates* the
        # attribute, and the generated _fetch_instances() guards optional
        # instances with hasattr(), which is true for an attribute holding
        # None - so a model with no armature would crash on write instead of
        # skipping the section it doesn't have.
        dst_mod.bones_data = bones_data
    dst_mod.groups = _serialize_groups(src_mod, dst_mod)
    materials_map = serialize_materials(dst_mod)

    meshes_data, vertex_buffer, vertex_buffer_2, index_buffer = _serialize_meshes_data(
        app_id, mesh_inputs, skeleton, src_mod, dst_mod, materials_map, settings, bone_palettes)

    dst_mod.header.num_vertices = sum(m.num_vertices for m in meshes_data.meshes)
    dst_mod.meshes_data = meshes_data
    dst_mod.vertex_buffer = vertex_buffer
    dst_mod.vertex_buffer_2 = vertex_buffer_2
    dst_mod.index_buffer = index_buffer

    offset = dst_mod.size_top_level_
    # A model with no armature has no bones_data section at all (num_bones is
    # what gates it, see the .ksy): real files signal that with a 0 offset
    # rather than an offset pointing at an empty section
    dst_mod.header.offset_bones_data = offset if dst_mod.header.num_bones else 0
    dst_mod.header.offset_groups = offset + dst_mod.bones_data_size_
    dst_mod.header.offset_materials_data = dst_mod.header.offset_groups + dst_mod.groups_size_
    dst_mod.header.offset_meshes_data = dst_mod.header.offset_materials_data + dst_mod.materials_data.size_
    dst_mod.header.offset_vertex_buffer = dst_mod.header.offset_meshes_data + dst_mod.meshes_data.size_
    dst_mod.header.offset_vertex_buffer_2 = dst_mod.header.offset_vertex_buffer + len(vertex_buffer)
    dst_mod.header.offset_index_buffer = dst_mod.header.offset_vertex_buffer_2 + len(vertex_buffer_2)

    dst_mod.header.size_vertex_buffer = len(vertex_buffer)
    dst_mod.header.size_vertex_buffer_2 = len(vertex_buffer_2)
    # num_indices (named num_faces until #252) is the index count, not a face
    # count (see num_triangles below, which is the actual triangle count on a
    # triangle-list version).
    #
    # The 21 formats size their index buffer as num_indices * 2, so num_indices
    # is exactly the number of indices. mod-153 and mod-156 size theirs as
    # (num_indices * 2) - 2, so there it is the index count plus one, and the
    # trailing entry the +1 accounts for is the padding appended below.
    # Applying the +1 everywhere wrote one index too many on 21: measured
    # against real umvc3 files, num_indices equals the summed mesh index count
    # exactly, and export was producing 205 against 204, 42847 against 42846.
    if dst_mod.header.version in VERSIONS_MOD_21:
        dst_mod.header.num_indices = len(index_buffer) // 2
    else:
        dst_mod.header.num_indices = (len(index_buffer) // 2) + 1
    if dst_mod.header.version not in VERSIONS_USE_TRISTRIPS:
        # On a version that indexes triangles as a plain list, the two fields
        # are one relation apart - measured across every model in the
        # serialization dataset, num_indices equals the summed mesh index
        # count and num_triangles is exactly a third of it. Deriving it keeps
        # the header self-consistent whatever num_indices ends up being.
        #
        # Left alone on the tristrip versions: there the index count is not
        # three per triangle, num_triangles has no such relation to num_indices
        # in a real file, and recovering the triangle count needs the strip
        # decomposition rather than arithmetic.
        dst_mod.header.num_triangles = dst_mod.header.num_indices // 3
    if app_id not in ["re5"] and dst_mod.header.version not in VERSIONS_MOD_21:
        # The trailing index the (num_indices * 2) - 2 sizing leaves room for.
        # A 21 file has no such entry: its meshes tile the index buffer
        # exactly, the last one ending on num_indices.
        index_buffer.extend((0, 0))
    # Real 21 files pad the index buffer with zeros to a 4 byte boundary, and
    # size_file counts that padding: an odd index count on re6 ends the
    # buffer at 16690 and the file carries size_file 16692. Only the size
    # needs it, the stream below starts zeroed.
    index_buffer_padding = (
        -len(index_buffer) % 4 if dst_mod.header.version in VERSIONS_MOD_21 else 0)

    final_size = sum((
        offset,
        dst_mod.bones_data_size_,
        dst_mod.groups_size_,
        dst_mod.materials_data.size_,
        dst_mod.meshes_data.size_,
        dst_mod.header.size_vertex_buffer,
        dst_mod.header.size_vertex_buffer_2,
        # No + 4: a real file's size_file stops at the end of the index
        # buffer and does not count the four trailing bytes after it.
        # Measured on umvc3 - a 2056 byte file carries size_file 2052, and a
        # 542808 byte one carries 542804 - while export was writing the full
        # length. size_file only exists on the 21 formats.
        len(index_buffer),
        index_buffer_padding,
    ))

    dst_mod.header.size_file = final_size
    # The file itself is four bytes longer than size_file: real ones carry a
    # zero trailer past it (2056/2052, 542808/542804, 1027148/1027144 on the
    # umvc3 models in the dataset).
    stream = KaitaiStream(BytesIO(bytearray(final_size + 4)))
    check_recursive(dst_mod)
    dst_mod._write(stream)
    return stream.to_byte_array()
