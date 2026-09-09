"""Short .bin headers: albam.engines.cie.structs.re4_uhd_bin.py.

The format allows a header of 0x40, 0x50 or 0x60 bytes - offset_bones (the
header's first field) doubles as its own size. The fields down to
version_flags are exactly 0x40 bytes and the four trailing offsets bring the
header to exactly 0x50, so only a 0x40 header stops before those four exist
in the file at all; a 0x50 header states all four, and a 0x60 one is a 0x50
header plus 16 bytes of padding nothing reads (see re4-uhd-bin.ksy). Reading
the four unconditionally, as this hand-maintained generated file used to,
consumed the next 16 bytes of whatever actually follows a 0x40 header - here,
bone data - as if they were those fields.

No file in a several-hundred-file sample of the shipped game (see
tests/cie/test_lfs_fs.py's dataset scale, and GitHub issue #271) uses a
header this short, so these are synthetic files rather than real ones - a
reader still has no business assuming a format it did not design always
ships the longest variant.
"""
import struct

from albam.engines.cie.structs.re4_uhd_bin import Re4UhdBin

SHORT_HEADER_SIZE = 0x40
MEDIUM_HEADER_SIZE = 0x50


def _bin_with_one_bone(bone_id=42, bone_parent=0xFF, bone_xyz=(1.0, 2.0, 3.0),
                       trailing_offsets=None):
    """A minimal, otherwise-empty mesh .bin followed immediately by one bone -
    exactly where offset_bones says it should be.

    `trailing_offsets` are the four the header ends with: None builds the
    0x40 header that stops before them, a 4-tuple the 0x50 header that
    states them.
    """
    header_size = (SHORT_HEADER_SIZE if trailing_offsets is None
                   else MEDIUM_HEADER_SIZE)
    end = header_size + 16  # header + one bone, nothing else in this file
    header = struct.pack(
        "<IIIIIIBBHIIIBBHIIIHHI",
        header_size,        # offset_bones (doubles as header size)
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
    if trailing_offsets is not None:
        header += struct.pack("<IIII", *trailing_offsets)
    assert len(header) == header_size
    bone = struct.pack("<BBHfff", bone_id, bone_parent, 0, *bone_xyz)
    return header + bone


def test_a_short_header_s_trailing_offsets_default_to_absent():
    parsed = Re4UhdBin.from_bytes(_bin_with_one_bone())
    parsed._read()

    assert parsed.header.offset_bones == SHORT_HEADER_SIZE
    assert parsed.header.offset_bonepairs == 0
    assert parsed.header.offset_adjacents == 0
    assert parsed.header.offset_index_buffer == 0
    assert parsed.header.offset_index_buffer2 == 0
    # Each optional block is only read `if offset_X > 0` (see
    # re4-uhd-bin.ksy), so asking for one comes back with nothing rather than
    # parsing whatever those bytes happen to be.
    assert parsed.bone_pairs is None
    assert parsed.adjacent is None
    assert parsed.indexes is None
    assert parsed.indexes2 is None


def test_a_short_header_s_bone_data_is_read_correctly_not_as_trailing_offsets():
    bin_bytes = _bin_with_one_bone(bone_id=42, bone_parent=0xFF, bone_xyz=(1.0, 2.0, 3.0))
    parsed = Re4UhdBin.from_bytes(bin_bytes)
    parsed._read()

    assert len(parsed.bones) == 1
    bone = parsed.bones[0]
    assert bone.bone_id == 42
    assert bone.parent == 0xFF
    assert (bone.x, bone.y, bone.z) == (1.0, 2.0, 3.0)


def test_a_0x50_header_states_its_trailing_offsets_and_its_bone_follows_them():
    """A 0x50 header is exactly the four trailing offsets present, so it must
    keep being read like a 0x60 one: defaulting them to 0 here would drop the
    bone-pair, adjacency and weight-index blocks such a file does state.
    """
    trailing = (0x1000, 0x2000, 0x3000, 0x4000)
    parsed = Re4UhdBin.from_bytes(
        _bin_with_one_bone(bone_id=7, bone_parent=3, bone_xyz=(4.0, 5.0, 6.0),
                           trailing_offsets=trailing))
    parsed._read()

    assert parsed.header.offset_bones == MEDIUM_HEADER_SIZE
    assert (parsed.header.offset_bonepairs, parsed.header.offset_adjacents,
            parsed.header.offset_index_buffer,
            parsed.header.offset_index_buffer2) == trailing

    assert len(parsed.bones) == 1
    bone = parsed.bones[0]
    assert bone.bone_id == 7
    assert bone.parent == 3
    assert (bone.x, bone.y, bone.z) == (4.0, 5.0, 6.0)
