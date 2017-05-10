from ctypes import Structure, c_uint, c_float, c_char, c_short, c_ushort, c_byte, c_ubyte

from albam.engines.mtframework.mod_156 import Bone, GroupData, get_meshes_sizes
from albam.lib.structure import DynamicStructure


class Mod210(DynamicStructure):
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


VERTEX_FORMATS_TO_CLASSES = {
                             0xA8FAB018: VertexFormat_Test1,
                             0xB0983013: VertexFormat_Test2,
                             0xB0983014: VertexFormat_Test2,
                             0x2F55C03D: VertexFormat_Test3,
                             0xC31F201C: VertexFormat_Test4,
                             0xDB7DA014: VertexFormat_Test5,
                             }

CLASSES_TO_VERTEX_FORMATS = {v: k for k, v in VERTEX_FORMATS_TO_CLASSES.items()}
