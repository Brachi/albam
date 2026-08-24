"""
RE:ORC (.anims.ssg) animation decoding + Blender Action building.

Deliberately self-contained: build_blender_action() takes an *already
built* armature object (see its own docstring for the exact bone-lookup
shape it expects) rather than building one itself - the skeleton
(dlc/pack1/Characters/skel/*.ssg) importer is separate work that wires
into albam.engines.hexn.mesh.build_blender_model.

The per-clip payload past AnimClip.size_header (see structs/anims.ksy) is
Sony PS3 "Edge" middleware's bit-packed, adaptively-interpolated keyframe
stream: constant channels store one value used for every frame; animated
channels are split into "framesets" (each covering a contiguous frame
range) that bracket any given frame between two explicit keys located via
a per-frame bitmask search over a packed bit array, then slerp/lerp
between them. decode_clip() below ports that algorithm - modeled against
a community Blender import script that documents it (see anims.ksy's own
module doc for how that reference was obtained and cross-checked against
real bytes, not trusted blindly) - using plain Python ints for the
bit-packed 128-bit window math instead of the reference's manual 4x32-bit
word shuffling (masking to the same fixed widths at each step reproduces
the same truncation behavior; see _first_set_bit/_last_set_bit).

Only num_frame_sets > 1 is implemented: every real clip entry in the
verified dataset has num_frame_sets >= 2, so the num_frame_sets == 1
layout (which the community reference itself never
fully resolves either - every offset that would be needed for it stays at
its zero default in that script) is left unsupported, raising rather than
silently producing wrong keyframes.

Root motion (a per-frame world translation + rotation for bone index 0,
stored separately from the regular channel system when
AnimClip.offset_custom_data > 0) is decoded too.
"""
import struct
from dataclasses import dataclass, field
from math import sqrt

import bpy
from mathutils import Quaternion, Vector

from .structs.hexane_anims import HexaneAnims

_QUAT_SCALE = ((1 << 15) - 1) / sqrt(2)
_QUAT_OFFSET = _QUAT_SCALE / sqrt(2)
_MASK32 = 0xFFFFFFFF
_MASK128 = (1 << 128) - 1


def _align(value, to):
    return value + (-value) % to


def _decompress_rotation(raw6):
    """"Smallest three" quaternion compression: the largest of the 4
    components is dropped (its sign/index recorded in the low 2 bits) and
    reconstructed from the other 3 via the unit-length constraint. Ported
    from decompress_animation_rotation (see module docstring)."""
    q64 = int.from_bytes(raw6, "big")
    a = (q64 >> 32) & 0x7FFF
    b = (q64 >> 17) & 0x7FFF
    c = (q64 >> 2) & 0x7FFF
    idx = q64 & 3

    fa = (a - _QUAT_OFFSET) / _QUAT_SCALE
    fb = (b - _QUAT_OFFSET) / _QUAT_SCALE
    fc = (c - _QUAT_OFFSET) / _QUAT_SCALE
    d_sq = 1 - fa * fa - fb * fb - fc * fc
    fd = sqrt(d_sq) if d_sq > 0 else 0.0

    if idx == 0:
        return Quaternion((fc, fd, fa, fb))
    elif idx == 1:
        return Quaternion((fc, fa, fd, fb))
    elif idx == 2:
        return Quaternion((fc, fa, fb, fd))
    else:
        return Quaternion((fd, fa, fb, fc))


def _decompress_vector(raw12):
    x, y, z = struct.unpack_from("<3f", raw12)
    return Vector((x, y, z))


def _bit_mask_128(bit_pos):
    """128-bit value (as a plain Python int, MSB = bit 0) with the top
    `bit_pos` bits set. Ported from anim_generate_bit_mask."""
    all64 = (1 << 64) - 1
    if bit_pos >= 64:
        t0 = all64
        shift = 128 - bit_pos
        t1 = (all64 << shift) & all64 if 0 < shift < 64 else (all64 if shift == 0 else 0)
    else:
        shift = 64 - bit_pos
        t0 = (all64 << shift) & all64 if shift < 64 else 0
        t1 = 0
    return (t0 << 64) | t1


def _first_set_bit(v, width):
    """Position (0 = MSB) of the highest set bit in a `width`-bit value,
    or `width` if v == 0. Ported from anim_get_first_set_bit_32/128 -
    equivalent in plain Python to width - v.bit_length()."""
    return width - v.bit_length()


def _last_set_bit(v, width):
    """Position (0 = MSB) of the lowest set bit in a `width`-bit value, or
    `width - 1` (matching the reference's uint32(-1) sentinel wrapping
    back to -1 under the width-bit arithmetic it's always combined with -
    see _bracketing_keyframes) if v == 0. Ported from
    anim_get_last_set_bit_32/128 (v & -v isolates the lowest set bit)."""
    if v == 0:
        return -1
    return _first_set_bit(v & -v, width)


@dataclass
class _FrameSet:
    base_frame: int
    num_intra_frames: int
    start: int = 0
    bits_intra_adr: int = 0
    offset_initial_r: int = 0
    offset_initial_t: int = 0
    offset_intra_r: int = 0
    offset_intra_t: int = 0
    offset_final_r: int = 0
    offset_final_t: int = 0
    offset_intra_r_bits: int = 0
    offset_intra_t_bits: int = 0
    bit_mask: int = 0
    next_frame_set: int = 0


@dataclass
class DecodedClip:
    name: str
    skeleton_name: str
    duration_seconds: float
    framerate: float
    num_frames: int
    num_bones: int
    # bone_index -> (list[Vector] positions, list[Quaternion] rotations), one
    # entry per frame. Only bones actually referenced by a const/animated
    # channel (or bone 0, for root motion) get an entry - every other bone
    # simply has no keyframes produced for it (stays at whatever pose the
    # armature already has, i.e. its bind pose for an otherwise-untouched
    # armature).
    bones: dict = field(default_factory=dict)


def parse_clip_name(file_info_name):
    """Splits a file_info.name ("<clip_path>--<skeleton_name>") into
    (clip_path, skeleton_name). See structs/anims.ksy's module doc for how
    this convention was confirmed."""
    clip_path, _, skeleton_name = file_info_name.rpartition("--")
    return clip_path, skeleton_name


def decode_clip(clip_bytes, name="", skeleton_name=""):
    """Decodes one animation clip's raw bytes (starting with the "40AE"
    magic - see structs/anims.ksy's AnimClip) into a DecodedClip: real
    position/rotation keyframes per bone per frame, in the same
    parent-bone-local space the referenced skeleton's own per-bone bind
    transform is stored in (see build_blender_action's docstring for how
    that's turned into pose_bone.location/rotation_quaternion).
    """
    clip = HexaneAnims.AnimClip.from_bytes(clip_bytes)
    clip._read()

    if clip.num_frame_sets <= 1:
        raise NotImplementedError(
            f"num_frame_sets={clip.num_frame_sets} (clip {name!r}) - only the num_frame_sets > 1 "
            f"layout is implemented (every real clip in the verified dataset has >= 2); "
            f"see module docstring."
        )

    result = DecodedClip(
        name=name, skeleton_name=skeleton_name, duration_seconds=clip.duration_seconds,
        framerate=clip.framerate, num_frames=clip.num_frames, num_bones=clip.num_bones,
    )
    bones = {
        i: ([Vector((0, 0, 0))] * clip.num_frames, [Quaternion((1, 0, 0, 0))] * clip.num_frames)
        for i in range(clip.num_bones)
    }

    pos = 96  # AnimClip's own confirmed header ends here - see structs/anims.ksy
    (num_const_r, num_const_t, num_const_s, num_const_user,
     num_anim_r, num_anim_t, num_anim_s, num_anim_user) = (
        clip.num_const_r_channels, clip.num_const_t_channels, clip.num_const_s_channels,
        clip.num_const_user_channels, clip.num_anim_r_channels, clip.num_anim_t_channels,
        clip.num_anim_s_channels, clip.num_anim_user_channels,
    )

    def read_u2_array(pos, count, align_to):
        n = _align(count, align_to)
        values = struct.unpack_from(f"<{n}H", clip_bytes, pos) if n else ()
        return values[:count], pos + n * 2

    const_r_idx, pos = read_u2_array(pos, num_const_r, 8)
    const_t_idx, pos = read_u2_array(pos, num_const_t, 4)
    const_s_idx, pos = read_u2_array(pos, num_const_s, 4)
    const_user_idx, pos = read_u2_array(pos, num_const_user, 4)
    anim_r_idx, pos = read_u2_array(pos, num_anim_r, 4)
    anim_t_idx, pos = read_u2_array(pos, num_anim_t, 4)
    anim_s_idx, pos = read_u2_array(pos, num_anim_s, 4)
    anim_user_idx, pos = read_u2_array(pos, num_anim_user, 4)
    pos = _align(pos, 16)

    for i, bone_idx in enumerate(const_r_idx):
        rot = _decompress_rotation(clip_bytes[pos + i * 6:pos + i * 6 + 6])
        positions, rotations = bones[bone_idx]
        bones[bone_idx] = (positions, [rot] * clip.num_frames)
    pos += num_const_r * 6
    pos = _align(pos, 16)

    for i, bone_idx in enumerate(const_t_idx):
        translation = _decompress_vector(clip_bytes[pos + i * 12:pos + i * 12 + 12])
        positions, rotations = bones[bone_idx]
        bones[bone_idx] = ([translation] * clip.num_frames, rotations)
    pos += num_const_t * 12
    pos = _align(pos, 16)

    pos += num_const_s * 12  # const scale: not applied (not used in RE:ORC - see reference)
    pos = _align(pos, 4)
    pos += num_const_user * 4  # const user channels: not animation data, not applied
    if clip.offset_packing_specs != 0:
        pos = _align(pos, 4)  # packing specs: not used in RE:ORC - only alignment matters here
    pos = _align(pos, 16)

    pos += clip.num_frame_sets * 8  # frame set dma array: not needed, only its size
    pos = _align(pos, 4)
    frame_sets = []
    for _ in range(clip.num_frame_sets):
        base_frame, num_intra_frames = struct.unpack_from("<2H", clip_bytes, pos)
        frame_sets.append(_FrameSet(base_frame=base_frame, num_intra_frames=num_intra_frames))
        pos += 4
    pos = _align(pos, 16)

    if clip.size_joints_weight_array:
        pos = _align(pos, 16)
        pos += clip.size_joints_weight_array
    pos = _align(pos, 16)
    assert pos == clip.size_header, (name, pos, clip.size_header)

    num_anim_channels_per_frame = num_anim_r + num_anim_t + num_anim_s + num_anim_user
    for i, fs in enumerate(frame_sets):
        pos = _align(pos, 16)
        fs.start = pos
        size_initial_r, size_initial_t, size_initial_s, size_initial_user = struct.unpack_from(
            "<4H", clip_bytes, pos)
        size_intra_r, size_intra_t, size_intra_s, size_intra_user = struct.unpack_from(
            "<4H", clip_bytes, pos + 8)

        fs.offset_initial_r = 0x10
        offset_initial_t = fs.offset_initial_r + size_initial_r
        offset_initial_s = offset_initial_t + size_initial_t
        offset_initial_user = offset_initial_s + size_initial_s
        fs.offset_initial_t = offset_initial_t
        fs.bits_intra_adr = offset_initial_user + size_initial_user
        fs.offset_intra_r = fs.bits_intra_adr + (
            num_anim_channels_per_frame * fs.num_intra_frames + 7) // 8
        offset_intra_t = fs.offset_intra_r + size_intra_r
        offset_intra_s = offset_intra_t + size_intra_t
        fs.offset_intra_t = offset_intra_t
        offset_intra_user = _align(offset_intra_s + size_intra_s, 4)
        fs.next_frame_set = _align(offset_intra_user + size_intra_user, 16)

        final_pos = fs.start + fs.next_frame_set
        size_final_r, size_final_t, size_final_s = struct.unpack_from("<3H", clip_bytes, final_pos)
        fs.offset_final_r = (final_pos + 16) - fs.start  # 3 u2 (6 bytes) + 10 bytes skipped = 16
        offset_final_t = fs.offset_final_r + size_final_r
        fs.offset_final_t = offset_final_t
        # offset_final_s (= offset_final_t + size_final_t) isn't needed - no
        # scale channel decoding (see the num_const_s/num_anim_s handling
        # above - matches the community reference, which doesn't apply
        # scale channels either).

        fs.offset_intra_r_bits = 0
        fs.offset_intra_t_bits = fs.offset_intra_r_bits + num_anim_r * fs.num_intra_frames
        fs.bit_mask = _bit_mask_128(fs.num_intra_frames)

        pos = final_pos

    # -- per-frame decode: for each frame, both cursors below (rotation and
    # translation) reset to the frameset's own base offsets and then walk
    # forward one channel-sized region at a time - each animated channel
    # owns a fixed-width slice of the shared per-frameset bit/data arrays
    # (its own num_intra_frames-wide presence-bitmask window, its own
    # num_keys-sized run of explicit keys), so re-deriving channel j's
    # slice from the frameset base + the preceding j channels' own sizes is
    # the correct way to locate it for *every* frame, not something to
    # carry over frame-to-frame (channel sizes don't depend on which frame
    # is being queried) - ported from parse_anim's own per-frame reset of
    # offset_intra_r_bits/offset_intra_r_data/etc from frame_set's fields.
    for frame in range(clip.num_frames):
        fs_id = _frame_set_index(frame_sets, frame)
        fs = frame_sets[fs_id]
        frame_number = frame - fs.base_frame
        frame_fraction = 0
        if frame_number > fs.num_intra_frames:
            frame_number = fs.num_intra_frames
            frame_fraction = 1
        prev_bit_mask = _bit_mask_128(frame_number)

        ob, od, oi, of = fs.offset_intra_r_bits, fs.offset_intra_r, fs.offset_initial_r, fs.offset_final_r
        for j in range(num_anim_r):
            key_a, key_b, num_keys, alpha = _bracketing_keyframes(
                clip_bytes, frame_number, frame_fraction, prev_bit_mask, 6,
                ob, od, oi, of, fs.start, fs.bits_intra_adr, fs.bit_mask,
            )
            rot_a = _decompress_rotation(clip_bytes[fs.start + key_a:fs.start + key_a + 6])
            rot_b = _decompress_rotation(clip_bytes[fs.start + key_b:fs.start + key_b + 6])
            result_rot = rot_a.slerp(rot_b, alpha) if rot_a != rot_b else rot_a
            bone_idx = anim_r_idx[j]
            positions, rotations = bones[bone_idx]
            rotations[frame] = result_rot
            ob += fs.num_intra_frames
            od += num_keys * 6
            oi += 6
            of += 6

        ob, od, oi, of = fs.offset_intra_t_bits, fs.offset_intra_t, fs.offset_initial_t, fs.offset_final_t
        for j in range(num_anim_t):
            key_a, key_b, num_keys, alpha = _bracketing_keyframes(
                clip_bytes, frame_number, frame_fraction, prev_bit_mask, 12,
                ob, od, oi, of, fs.start, fs.bits_intra_adr, fs.bit_mask,
            )
            trans_a = _decompress_vector(clip_bytes[fs.start + key_a:fs.start + key_a + 12])
            trans_b = _decompress_vector(clip_bytes[fs.start + key_b:fs.start + key_b + 12])
            result_pos = trans_a.lerp(trans_b, alpha)
            bone_idx = anim_t_idx[j]
            positions, rotations = bones[bone_idx]
            positions[frame] = result_pos
            ob += fs.num_intra_frames
            od += num_keys * 12
            oi += 12
            of += 12

    if clip.offset_custom_data > 0:
        _decode_root_motion(clip, clip_bytes, bones)

    result.bones = bones
    return result


def _decode_root_motion(clip, clip_bytes, bones):
    """Per-frame world translation + full (unpacked, uncompressed)
    quaternion for bone 0, stored separately from the regular channel
    system. Ported from parse_anim's own "custom data (skel_root motion)"
    block."""
    pos = clip.offset_custom_data + 0x50 + 32
    positions = []
    for _ in range(clip.num_frames):
        x, y, z = struct.unpack_from("<3f", clip_bytes, pos)
        positions.append(Vector((x, y, z)))
        pos += 16  # xyz + 4 bytes unused
    rotations = []
    for _ in range(clip.num_frames):
        x, y, z, w = struct.unpack_from("<4f", clip_bytes, pos)
        quat = Quaternion((w, x, y, z))
        # A handful of real clips store an all-zero quaternion on their
        # last frame or two (trailing garbage past the last real sample,
        # not a valid rotation) - same category of occasional bad data
        # the community reference itself hits and falls back on for its
        # own compressed-channel decode (its "a NaN by Sony" case). Fall
        # back to the previous frame rather than produce a zero-magnitude
        # rotation.
        if quat.magnitude < 0.5 and rotations:
            quat = rotations[-1]
        rotations.append(quat)
        pos += 16
    bones[0] = (positions, rotations)


def _frame_set_index(frame_sets, frame):
    left, right = 0, len(frame_sets) - 1
    while left + 1 < right:
        mid = (left + right) >> 1
        if frame < frame_sets[mid].base_frame:
            right = mid
        else:
            left = mid
    return left


def _bracketing_keyframes(
    clip_bytes, frame_number, frame_fraction, prev_bit_mask, stride,
    offset_intra_bits, offset_intra_data, offset_initial_data,
    offset_final_data, frameset_start, bits_intra_adr, bit_mask,
):
    """Locates the two explicit keys bracketing `frame_number` within one
    animated channel's own bit-packed intra-frame presence stream, plus
    the interpolation factor between them. Ported from
    anim_get_bracketing_keyframes (see module docstring): the original's
    4x32-bit-word bit-window extraction is replaced with one big-int
    window covering the same 128 bits (see module docstring)."""
    byte_offset = bits_intra_adr + (offset_intra_bits >> 3)
    bit_shift = offset_intra_bits & 7
    window_bytes = clip_bytes[frameset_start + byte_offset:frameset_start + byte_offset + 17]
    window = int.from_bytes(window_bytes, "big")
    window128 = (window >> (8 - bit_shift)) & _MASK128

    intra_bits = window128 & bit_mask
    prev_bits = window128 & prev_bit_mask
    num_bits = bin(intra_bits).count("1")
    num_prev_bits = bin(prev_bits).count("1")
    not_prev_mask = (~prev_bit_mask) & _MASK128
    not_bit_mask = (~bit_mask) & _MASK128
    intra_bits_m = (intra_bits & not_prev_mask) | not_bit_mask

    last_prev = _last_set_bit(prev_bits, 128)
    b_bits = (frame_number - last_prev - 1) & _MASK32
    first_intra_m = _first_set_bit(intra_bits_m, 128)
    a_bits = (first_intra_m - frame_number + 1) & _MASK32

    if num_prev_bits == 0:
        key_a = offset_initial_data
    else:
        key_a = offset_intra_data + (num_prev_bits - 1) * stride

    if num_prev_bits == num_bits:
        key_b = offset_final_data
    else:
        key_b = offset_intra_data + num_prev_bits * stride

    denom = a_bits + b_bits + frame_fraction
    alpha = (b_bits + frame_fraction) / denom if denom else 0.0
    return key_a, key_b, num_bits, alpha


def build_blender_action(armature_object, decoded_clip, action_name, bone_names):
    """Builds a bpy.types.Action from a DecodedClip (see decode_clip()) and
    assigns it to `armature_object.animation_data.action`.

    `armature_object`: a bpy.types.Object of type 'ARMATURE', already
    built by a real skeleton importer - each pose bone's own
    `.bone.matrix_local` (Blender's local-to-armature bind transform) must
    already reflect the skeleton this clip was authored against, since the
    decoded position/rotation values are parent-bone-local deltas measured
    against that same bind pose (see the community reference's own
    `pose_bone.location = bone.position[i] - bind_matrix.to_translation()`
    - ported the same way here).

    `bone_names`: a sequence indexable 0..decoded_clip.num_bones-1 (a
    plain list, or anything supporting `bone_names[i]`) giving the pose
    bone name for each clip-internal bone index, or None to skip that
    index. THIS INDEX ORDER IS AN ASSUMPTION, NOT CONFIRMED: it assumes
    the skeleton importer preserves the skeleton file's own bone order
    1:1 into armature_object.pose.bones (e.g. `bone_names =
    [b.name for b in armature_object.pose.bones]` if so) - the skeleton
    side of this work was not available to verify this against when this
    was written. If the real importer instead needs a name-hash or
    explicit remapping, build `bone_names` from that instead; nothing
    else here depends on how it was produced.
    """
    armature_object.animation_data_create()
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    armature_object.animation_data.action = action

    pose_bones = armature_object.pose.bones
    for bone_idx, (positions, rotations) in decoded_clip.bones.items():
        if bone_idx >= len(bone_names):
            continue
        bone_name = bone_names[bone_idx]
        if bone_name is None or bone_name not in pose_bones:
            continue
        pose_bone = pose_bones[bone_name]
        bind_matrix = pose_bone.bone.matrix_local
        if pose_bone.parent is not None:
            bind_matrix = pose_bone.parent.bone.matrix_local.inverted() @ bind_matrix
        bind_translation = bind_matrix.to_translation()
        bind_rotation = bind_matrix.to_quaternion()

        # Blender 5.x's layered Action data model has no direct
        # action.fcurves/action.groups anymore (see mtfw.animation's own
        # load_lmt for the pre-5.x direct-fcurves idiom this replaces) -
        # fcurve_ensure_for_datablock() creates the layer/strip/slot the
        # new model needs, assigns the slot to armature_object, and groups
        # by group_name in one call.
        loc_curves = [
            action.fcurve_ensure_for_datablock(
                armature_object, f'pose.bones["{bone_name}"].location', index=i, group_name=bone_name)
            for i in range(3)
        ]
        rot_curves = [
            action.fcurve_ensure_for_datablock(
                armature_object, f'pose.bones["{bone_name}"].rotation_quaternion', index=i,
                group_name=bone_name)
            for i in range(4)
        ]

        prev_rotation = None
        for frame in range(decoded_clip.num_frames):
            local_pos = positions[frame] - bind_translation
            local_rot = bind_rotation.rotation_difference(rotations[frame])
            # Baked quaternions have no inherent sign - flip to the same
            # hemisphere as the previous frame so interpolation takes the
            # shortest path instead of an arbitrary per-frame sign flip.
            if prev_rotation is not None and local_rot.dot(prev_rotation) < 0:
                local_rot = -local_rot
            prev_rotation = local_rot

            for i, curve in enumerate(loc_curves):
                curve.keyframe_points.add(1)
                curve.keyframe_points[-1].co = (frame, local_pos[i])
                curve.keyframe_points[-1].interpolation = 'LINEAR'
            for i, curve in enumerate(rot_curves):
                curve.keyframe_points.add(1)
                curve.keyframe_points[-1].co = (frame, local_rot[i])
                curve.keyframe_points[-1].interpolation = 'LINEAR'

    return action
