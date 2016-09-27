from ctypes import Structure, c_uint, c_uint16, c_float, c_char, c_short, c_ushort, c_byte, c_ubyte

from albam.utils import BaseStructure
from albam.registry import blender_registry


class Bone(Structure):
    _fields_ = (('anim_map_index', c_ubyte),
                ('parent_index', c_ubyte),  # 255: root
                ('mirror_index', c_ubyte),
                ('palette_index', c_ubyte),
                ('unk_01', c_float),
                ('parent_distance', c_float),
                # Relative to the parent bone
                ('location_x', c_float),
                ('location_y', c_float),
                ('location_z', c_float),
                )


class BonePalette(Structure):
    _fields_ = (('unk_01', c_uint),
                ('values', c_ubyte * 32),
                )

    _comments_ = {'unk_01': 'Seems to be the count of meaninful values out of the 32 bytes, needs verification'}


class GroupData(Structure):
    _fields_ = (('group_index', c_uint),
                ('unk_02', c_float),
                ('unk_03', c_float),
                ('unk_04', c_float),
                ('unk_05', c_float),
                ('unk_06', c_float),
                ('unk_07', c_float),
                ('unk_08', c_float),
                )
    _comments_ = {'group_index': "In ~25% of all RE5 mods, this value doesn't match the index"}


class MaterialFlag(Structure):
    _fields_ = (('unk_01', c_uint16, 1),
                ('unk_02', c_uint16, 1),
                ('unk_03', c_uint16, 1),
                ('unk_04', c_uint16, 1),
                ('unk_05', c_uint16, 1),
                ('unk_06', c_uint16, 1),
                ('unk_07', c_uint16, 1),
                ('unk_08', c_uint16, 1),
                ('unk_09', c_uint16, 1),
                ('unk_10', c_uint16, 1),
                ('unk_11', c_uint16, 1),
                ('unk_12', c_uint16, 1),
                ('unk_13', c_uint16, 1),
                ('unk_14', c_uint16, 1),
                ('unk_15', c_uint16, 1),
                ('unk_16', c_uint16, 1),
                )


@blender_registry.register_bpy_prop('material', 'unk_')
class MaterialData(Structure):
    _fields_ = (('unk_01', c_ushort),
                ('flags_01', MaterialFlag),
                ('unk_02', c_ushort),
                ('unk_03', c_short),
                ('unk_04', c_ushort),
                ('unk_05', c_ushort),
                ('unk_06', c_ushort),
                ('unk_07', c_ushort),
                ('unk_08', c_ushort),
                ('unk_09', c_ushort),
                ('unk_10', c_ushort),
                ('unk_11', c_ushort),
                ('texture_indices', c_uint * 8),
                ('unk_12', c_float),
                ('unk_13', c_float),
                ('unk_14', c_float),
                ('unk_15', c_float),
                ('unk_16', c_float),
                ('unk_17', c_float),
                ('unk_18', c_float),
                ('unk_19', c_float),
                ('unk_20', c_float),
                ('unk_21', c_float),
                ('unk_22', c_float),
                ('unk_23', c_float),
                ('unk_24', c_float),
                ('unk_25', c_float),
                ('unk_26', c_float),
                ('unk_27', c_float),
                ('unk_28', c_float),
                ('unk_29', c_float),
                ('unk_30', c_float),
                ('unk_31', c_float),
                ('unk_32', c_float),
                ('unk_33', c_float),
                ('unk_34', c_float),
                ('unk_35', c_float),
                ('unk_36', c_float),
                ('unk_37', c_float),)


class Mesh156(Structure):
    _fields_ = (('group_index', c_ushort),
                ('material_index', c_ushort),
                ('constant', c_ubyte),  # always 1
                ('level_of_detail', c_ubyte),
                ('unk_01', c_ubyte),
                ('vertex_format', c_ubyte),
                ('vertex_stride', c_ubyte),
                ('unk_02', c_ubyte),
                ('unk_03', c_ubyte),
                ('unk_04', c_ubyte),
                ('vertex_count', c_ushort),
                ('vertex_index_end', c_ushort),
                ('vertex_index_start_1', c_uint),
                ('vertex_offset', c_uint),
                ('unk_05', c_uint),
                ('face_position', c_uint),
                ('face_count', c_uint),
                ('face_offset', c_uint),
                ('unk_06', c_ubyte),
                ('unk_07', c_ubyte),
                ('vertex_index_start_2', c_ushort),
                ('vertex_group_count', c_ubyte),
                ('bone_palette_index', c_ubyte),
                ('unk_08', c_ubyte),
                ('unk_09', c_ubyte),
                ('unk_10', c_ushort),
                ('unk_11', c_ushort),
                )


class Mesh210_211(Structure):
    _fields_ = (('mesh_type', c_ushort),
                ('vertex_count', c_ushort),
                ('unk_01', c_ubyte),
                ('material_index', c_ubyte),
                ('level_of_detail', c_ubyte),
                ('class', c_ubyte),
                ('mesh_class', c_ubyte),
                ('vertex_stride', c_ubyte),
                ('render_mode', c_ubyte),
                ('vertex_index', c_uint),
                ('vertex_offset', c_uint),
                ('vertex_format', c_uint),
                ('face_position', c_uint),
                ('face_count', c_uint),
                ('face_offset', c_uint),
                ('bone_id_start', c_ubyte),
                ('vertex_group_count', c_ubyte),
                ('unk_02', c_ubyte),
                ('unk_03', c_ubyte),
                ('min_index', c_ushort),
                ('max_index', c_ushort),
                ('hash', c_uint),
                )


class VertexFormat0(Structure):
    _fields_ = (('position_x', c_float),
                ('position_y', c_float),
                ('position_z', c_float),
                ('normal_x', c_byte),
                ('normal_y', c_byte),
                ('normal_z', c_byte),
                ('normal_w', c_byte),
                ('tangent_x', c_byte),
                ('tangent_y', c_byte),
                ('tangent_z', c_byte),
                ('tangent_w', c_byte),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                ('uv2_x', c_ushort),  # half float
                ('uv2_y', c_ushort),  # half float
                ('uv3_x', c_ushort),  # half float
                ('uv3_y', c_ushort),  # half float
                )


class VertexFormat(Structure):
    # http://forum.xentax.com/viewtopic.php?f=10&t=3057&start=165
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('position_w', c_short),
                ('bone_indices', c_ubyte * 4),
                ('weight_values', c_ubyte * 4),
                ('normal_x', c_byte),
                ('normal_y', c_byte),
                ('normal_z', c_byte),
                ('normal_w', c_byte),
                ('tangent_x', c_byte),
                ('tangent_y', c_byte),
                ('tangent_z', c_byte),
                ('tangent_w', c_byte),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                ('uv2_x', c_ushort),  # half float
                ('uv2_y', c_ushort),  # half float
                )


class VertexFormat2(VertexFormat):
    pass


class VertexFormat3(VertexFormat):
    pass


class VertexFormat4(VertexFormat):
    pass


class VertexFormat5(Structure):
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('position_w', c_short),
                ('bone_indices', c_ubyte * 8),
                ('weight_values', c_ubyte * 8),
                ('normal_x', c_byte),
                ('normal_y', c_byte),
                ('normal_z', c_byte),
                ('normal_w', c_byte),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                )


class VertexFormat6(VertexFormat5):
    pass


class VertexFormat7(VertexFormat5):
    pass


class VertexFormat8(VertexFormat5):
    pass


class VertexFormat_Test1(Structure):
    # 0xA8FAB018
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('bone_indices', c_ubyte * 1),
                ('weight_values', c_ubyte * 1),
                ('normal_x', c_byte),
                ('normal_y', c_byte),
                ('normal_z', c_byte),
                ('normal_w', c_byte),
                ('tangent_x', c_byte),
                ('tangent_y', c_byte),
                ('tangent_z', c_byte),
                ('tangent_w', c_byte),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                )


class VertexFormat_Test2(Structure):
    # 0xB0983013
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('bone_indices', c_ubyte * 1),
                ('weight_values', c_ubyte * 1),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                )


class VertexFormat_Test3(Structure):
    # 0x2F55C03D
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('weight_value_1', c_ushort),
                ('normal_x', c_byte),
                ('normal_y', c_byte),
                ('normal_z', c_byte),
                ('normal_w', c_byte),
                ('tangent_x', c_byte),
                ('tangent_y', c_byte),
                ('tangent_z', c_byte),
                ('tangent_w', c_byte),
                ('bone_indices', c_ubyte * 4),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                ('weight_value_2', c_ushort),  # half float
                ('weight_value_3', c_ushort),  # half float
                ('unk_01', c_uint),
                ('unk_02', c_uint),
                ('unk_03', c_uint),
                ('unk_04', c_uint),
                ('unk_05', c_uint),
                ('unk_06', c_uint),
                ('unk_07', c_uint),
                ('unk_08', c_uint),
                ('unk_09', c_uint),
                )


class VertexFormat_Test4(Structure):
    # 0xC31F201C
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('weight_value_1', c_ushort),
                ('normal_x', c_byte),
                ('normal_y', c_byte),
                ('normal_z', c_byte),
                ('normal_w', c_byte),
                ('tangent_x', c_byte),
                ('tangent_y', c_byte),
                ('tangent_z', c_byte),
                ('tangent_w', c_byte),
                ('bone_indices', c_ushort * 2),  # half float??
                ('uv_x', c_ushort),  # halhf float
                ('uv_y', c_ushort),  # half float
                )


class VertexFormat_Test5(Structure):
    # 0xDB7DA014
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('unk_01', c_byte),
                ('unk_02', c_byte),
                ('unk_03', c_byte),
                ('unk_04', c_byte),
                ('bone_indices', c_ubyte * 1),
                ('weight_values', c_ubyte * 1),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                )

VERTEX_FORMATS_TO_CLASSES = {0: VertexFormat0,
                             1: VertexFormat,
                             2: VertexFormat2,
                             3: VertexFormat3,
                             4: VertexFormat4,
                             5: VertexFormat5,
                             6: VertexFormat6,
                             7: VertexFormat7,
                             8: VertexFormat8,
                             0xA8FAB018: VertexFormat_Test1,
                             0xB0983013: VertexFormat_Test2,
                             0xB0983014: VertexFormat_Test2,
                             0x2F55C03D: VertexFormat_Test3,
                             0xC31F201C: VertexFormat_Test4,
                             0xDB7DA014: VertexFormat_Test5,
                             }


CLASSES_TO_VERTEX_FORMATS = {v: k for k, v in VERTEX_FORMATS_TO_CLASSES.items()}


def get_meshes_sizes(mod):
    if mod.version == 156:
        extra = 1  # TODO: investigate
    else:
        extra = 0
    total_count = sum(mesh.vertex_group_count for mesh in mod.meshes_array)
    return c_float * ((total_count * 36) + extra)


def unk_data_depends_on_other_unk(tmp_struct):
    if tmp_struct.unk_08:
        return c_ubyte * (tmp_struct.bones_array_offset - 176)
    else:
        return c_ubyte * 0


class Mod156(BaseStructure):
    _fields_ = (('id_magic', c_char * 4),
                ('version', c_ubyte),
                ('version_rev', c_byte),
                ('bone_count', c_ushort),
                ('mesh_count', c_short),
                ('material_count', c_ushort),
                ('vertex_count', c_uint),
                ('face_count', c_uint),
                ('edge_count', c_uint),
                ('vertex_buffer_size', c_uint),
                ('vertex_buffer_2_size', c_uint),
                ('texture_count', c_uint),
                ('group_count', c_uint),
                ('bone_palette_count', c_uint),
                ('bones_array_offset', c_uint),
                ('group_offset', c_uint),
                ('textures_array_offset', c_uint),
                ('meshes_array_offset', c_uint),
                ('vertex_buffer_offset', c_uint),
                ('vertex_buffer_2_offset', c_uint),
                ('index_buffer_offset', c_uint),
                ('reserved_01', c_uint),
                ('reserved_02', c_uint),
                ('sphere_x', c_float),
                ('sphere_y', c_float),
                ('sphere_z', c_float),
                ('sphere_w', c_float),
                ('box_min_x', c_float),
                ('box_min_y', c_float),
                ('box_min_z', c_float),
                ('box_min_w', c_float),
                ('box_max_x', c_float),
                ('box_max_y', c_float),
                ('box_max_z', c_float),
                ('box_max_w', c_float),
                ('unk_01', c_uint),
                ('unk_02', c_uint),
                ('unk_03', c_uint),
                ('unk_04', c_uint),
                ('unk_05', c_uint),
                ('unk_06', c_uint),
                ('unk_07', c_uint),
                ('unk_08', c_uint),
                ('unk_09', c_uint),
                ('unk_10', c_uint),
                ('unk_11', c_uint),
                ('reserved_03', c_uint),
                ('unk_12', unk_data_depends_on_other_unk),
                ('bones_array', lambda s: Bone * s.bone_count),
                ('bones_unk_matrix_array', lambda s: (c_float * 16) * s.bone_count),
                ('bones_world_transform_matrix_array', lambda s: (c_float * 16) * s.bone_count),
                ('unk_13', lambda s: (c_ubyte * 256) if s.bone_palette_count else c_ubyte * 0),
                ('bone_palette_array', lambda s: BonePalette * s.bone_palette_count),
                ('group_data_array', lambda s: GroupData * s.group_count),
                ('textures_array', lambda s: (c_char * 64) * s.texture_count),
                ('materials_data_array', lambda s: MaterialData * s.material_count),
                ('meshes_array', lambda s: Mesh156 * s.mesh_count),
                ('meshes_array_2', get_meshes_sizes),
                ('vertex_buffer', lambda s: c_ubyte * s.vertex_buffer_size),
                ('vertex_buffer_2', lambda s: c_ubyte * s.vertex_buffer_2_size),
                # TODO: investigate the padding
                ('index_buffer', lambda s: c_ushort * (s.face_count - 1)),
                )


class Mod210(BaseStructure):
    _fields_ = (('id_magic', c_char * 4),
                ('version', c_ubyte),
                ('version_rev', c_byte),
                ('bone_count', c_ushort),
                ('mesh_count', c_short),
                ('material_count', c_ushort),
                ('vertex_count', c_uint),
                ('face_count', c_uint),
                ('edge_count', c_uint),
                ('vertex_buffer_size', c_uint),
                ('vertex_buffer_2_size', c_uint),
                ('group_count', c_uint),
                ('bones_array_offset', c_uint),
                ('group_offset', c_uint),
                ('materials_data_offset', c_uint),
                ('meshes_array_offset', c_uint),
                ('vertex_buffer_offset', c_uint),
                ('index_buffer_offset', c_uint),
                ('file_size', c_uint),
                ('sphere_w', c_float),
                ('sphere_x', c_float),
                ('sphere_y', c_float),
                ('sphere_z', c_float),
                ('box_min_x', c_float),
                ('box_min_y', c_float),
                ('box_min_z', c_float),
                ('box_min_w', c_float),
                ('box_max_x', c_float),
                ('box_max_y', c_float),
                ('box_max_z', c_float),
                ('box_max_w', c_float),
                ('unk_02', c_uint),
                ('unk_03', c_uint),
                ('unk_04', c_uint),
                ('unk_05', c_uint),
                ('unk_06', c_uint),
                ('bones_array', lambda s: Bone * s.bone_count),
                ('bones_unk_matrix_array', lambda s: (c_float * 16) * s.bone_count),
                ('bones_world_transform_matrix_array', lambda s: (c_float * 16) * s.bone_count),
                ('unk_07', lambda s: (c_ubyte * 256) if s.bone_count else c_ubyte * 0),
                ('group_data_array', lambda s: GroupData * s.group_count),
                ('materials_data_array', lambda s: ((32 * c_uint) * s.material_count)),
                ('meshes_array', lambda s: Mesh210_211 * s.mesh_count),
                ('meshes_array_2', get_meshes_sizes),
                ('vertex_buffer', lambda s: c_ubyte * s.vertex_buffer_size),
                ('vertex_buffer_2', lambda s: c_ubyte * s.vertex_buffer_2_size),
                ('index_buffer', lambda s: c_ushort * s.face_count),
                ('file_padding', c_ubyte * 2)
                )
