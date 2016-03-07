from ctypes import Structure, c_uint, c_float, c_char, c_short, c_ushort, c_byte, c_ubyte

from albam.utils import BaseStructure


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
    _fields_ = (('unk_01', c_uint),  # could be bone_count in values
                ('values', c_ubyte * 32),
                )


class GroupData(Structure):
    _fields_ = (('unk_01', c_uint),
                ('unk_02', c_uint),
                ('unk_03', c_uint),
                ('unk_04', c_uint),
                ('unk_05', c_uint),
                ('unk_06', c_uint),
                ('unk_07', c_uint),
                ('unk_08', c_uint),
                )


class MaterialData(Structure):
    _fields_ = (('unk_01', c_uint),
                ('unk_02', c_uint),
                ('unk_03', c_uint),
                ('unk_04', c_uint),
                ('unk_05', c_uint),
                ('unk_06', c_uint),
                ('texture_indices', c_uint * 8),
                ('unk_07', c_float * 26),
                )


class Mesh156(Structure):
    _fields_ = (('type', c_ushort),
                ('material_index', c_ushort),
                ('unk_01', c_ubyte),
                ('level_of_detail', c_ubyte),
                ('unk_02', c_ubyte),
                ('vertex_format', c_ubyte),
                ('vertex_stride', c_ubyte),
                ('unk_03', c_ubyte),
                ('unk_04', c_ubyte),
                ('unk_05', c_ubyte),
                ('vertex_count', c_ushort),
                ('vertex_index_end', c_ushort),
                ('vertex_index_start_1', c_uint),
                ('vertex_offset', c_uint),
                ('unk_06', c_uint),
                ('face_position', c_uint),
                ('face_count', c_uint),
                ('face_offset', c_uint),
                ('unk_07', c_ubyte),
                ('unk_08', c_ubyte),
                ('vertex_index_start_2', c_ushort),
                ('unk_09', c_ubyte),
                ('bone_palette_index', c_ubyte),
                ('unk_10', c_ubyte),
                ('unk_11', c_ubyte),
                ('unk_12', c_ushort),
                ('unk_13', c_ushort),
                )


class Mesh210_211(Structure):
    _fields_ = (('mesh_type', c_ushort),
                ('vertex_count', c_ushort),
                ('group_index', c_ubyte),
                ('unk_01', c_ubyte),
                ('material_index', c_ubyte),
                ('level_of_detail', c_ubyte),
                ('class', c_ubyte),
                ('mesh_class', c_ubyte),
                ('vertex_stride', c_ubyte),
                ('render_mode', c_ubyte),
                ('vertex_position', c_uint),
                ('vertex_offset', c_uint),
                ('vertex_format', c_uint),
                ('face_position', c_uint),
                ('face_count', c_uint),
                ('face_offset', c_uint),
                ('bone_id_start', c_ubyte),
                ('unique_boneids', c_ubyte),
                ('mesh_index', c_ushort),
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


def get_meshes_sizes(tmp_struct):
    sizes = 0
    for m in tmp_struct.meshes_array:
        try:
            sizes += m.unk_09
            extra = 1  # TODO: investigate
        except AttributeError:
            sizes += m.unique_boneids
            extra = 0
    total_size = 144 * sizes
    q = (total_size // 4) + extra
    return (c_uint * q)


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

