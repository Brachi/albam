"""A 0x40 (short) .bin header: albam.engines.cie.structs.re4_uhd_bin.py.

The format allows a header of 0x40, 0x50 or 0x60 bytes - offset_bones (the
header's first field) doubles as its own size, and the shorter variants stop
before the four trailing offset fields exist in the file at all (see
re4-uhd-bin.ksy). Reading them unconditionally, as this hand-maintained
generated file used to, consumed the next 16 bytes of whatever actually
follows a short header - here, bone data - as if they were those fields.

No file in a several-hundred-file sample of the shipped game (see
tests/cie/test_lfs_fs.py's dataset scale, and GitHub issue #271) uses a
header this short, so this is a synthetic file rather than a real one - a
reader still has no business assuming a format it did not design always
ships the longest variant.
"""
import struct

from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

SHORT_HEADER_SIZE = 0x40


def _short_header_bin(bone_id=42, bone_parent=0xFF, bone_xyz=(1.0, 2.0, 3.0)):
    """A minimal, otherwise-empty mesh .bin whose header stops at 0x40,
    followed immediately by one bone - exactly where offset_bones says it
    should be.
    """
    end = SHORT_HEADER_SIZE + 16  # header + one bone, nothing else in this file
    header = struct.pack(
        "<IIIIIIBBHIIIBBHIIIHHI",
        SHORT_HEADER_SIZE,  # offset_bones (doubles as header size)
        0,                  # unk_00
        0,                  # unk_01
        0,                  # offset_vertex_colors
        0,                  # offset_vertex_texcoord
        0,                  # offset_weights
        0,                  # num_weights
        1,                  # num_bones
        0,                  # num_materials
        end,                # offset_materials (unread: num_materials == 0)
        0x80000000,         # flags (mesh)
        0,                  # num_tpl
        0,                  # vertex_scale
        0,                  # unk_02
        0,                  # num_weights2
        0,                  # offset_morphs
        end,                # offset_vertex_position (unread: num_vertices == 0)
        end,                # offset_vertex_normals
        0,                  # num_vertices
        0,                  # num_vertex_normals
        0,                  # version_flags
    )
    assert len(header) == SHORT_HEADER_SIZE
    bone = struct.pack("<BBHfff", bone_id, bone_parent, 0, *bone_xyz)
    return header + bone


def test_a_short_header_s_trailing_offsets_default_to_absent():
    parsed = Re4UhdBin.from_bytes(_short_header_bin())
    parsed._read()

    assert parsed.header.offset_bones == SHORT_HEADER_SIZE
    assert parsed.header.offset_bonepairs == 0
    assert parsed.header.offset_adjacents == 0
    assert parsed.header.offset_index_buffer == 0
    assert parsed.header.offset_index_buffer2 == 0
    # None of these optional blocks should even be attempted: each is only
    # read `if offset_X > 0` (see re4-uhd-bin.ksy).
    assert parsed.header.offset_bonepairs == 0 and not hasattr(parsed, "_m_bone_pairs")
    assert parsed.header.offset_adjacents == 0 and not hasattr(parsed, "_m_adjacent")


def test_a_short_header_s_bone_data_is_read_correctly_not_as_trailing_offsets():
    bin_bytes = _short_header_bin(bone_id=42, bone_parent=0xFF, bone_xyz=(1.0, 2.0, 3.0))
    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()

    assert len(parsed.bones) == 1
    bone = parsed.bones[0]
    assert bone.bone_id == 42
    assert bone.parent == 0xFF
    assert (bone.x, bone.y, bone.z) == (1.0, 2.0, 3.0)
