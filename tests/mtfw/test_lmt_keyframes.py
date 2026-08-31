"""Encode/decode round trips for LMTKeyFrames, the .lmt keyframe codec.

CI-safe: drives the codec directly on synthetic values, no game data.
"""
import math

import pytest
from mathutils import Quaternion

VERSION_51 = 51
# Single-frame rotation buffer type: stores x, y and z only, and decoding
# rebuilds w from them (LMTKeyFrames.restore_w).
QUAT3_KF_TYPE = 4


def _round_trip_rotation(quaternion, version=VERSION_51, kf_type=QUAT3_KF_TYPE):
    from albam.engines.mtfw.animation import LMTKeyFrames

    encoder = LMTKeyFrames()
    encoder.version = version
    encoder.track_type = "rotation_quaternion"
    encoder.encode_framedata(kf_type, 0, {0.0: quaternion}, usage=0)
    (track,) = encoder.encoded_frames

    decoder = LMTKeyFrames()
    decoder.version = version
    decoder.track_type = "rotation_quaternion"
    decoder.decode_framedata(version, kf_type, track.data)
    (decoded,) = decoder.decoded_frames
    return decoded, track


def _same_rotation(a, b, tolerance=1e-3):
    """q and -q name the same rotation, so compare on the dot product."""
    dot = a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z
    return abs(abs(dot) - 1.0) < tolerance


@pytest.mark.parametrize("angle_deg", [30, 90, 150, 210, 300])
@pytest.mark.parametrize("negated", [False, True], ids=["w_positive", "w_negative"])
def test_single_frame_rotation_round_trips(angle_deg, negated):
    """Both signs of the same rotation have to survive.

    Quaternion(axis, angle) always hands back the w >= 0 form, so the
    negated case is built explicitly - it is the same rotation written the
    other way round, and the only one that exercises a w the buffer type
    cannot store.
    """
    source = Quaternion((0.0, 0.0, 1.0), math.radians(angle_deg))
    if negated:
        source = Quaternion((-source.w, -source.x, -source.y, -source.z))
    decoded, _track = _round_trip_rotation(source)
    assert _same_rotation(source, decoded), (
        f"{angle_deg} degrees (negated={negated}): {list(source)} came back as {list(decoded)}"
    )


def test_negative_w_rotation_round_trips():
    """A quaternion with w < 0 is the same rotation as its negation, but the
    buffer type stores no w and restore_w() rebuilds it as a positive square
    root - so it has to be written in canonical (w >= 0) form or it decodes
    to a different rotation.
    """
    source = Quaternion((-0.9055, 0.0, 0.0, -0.4246)).normalized()
    decoded, _track = _round_trip_rotation(source)
    assert decoded.w >= 0, "restore_w() can only ever produce w >= 0"
    assert _same_rotation(source, decoded), (
        f"{list(source)} came back as {list(decoded)} - a different rotation"
    )


# Buffer type 6 packs four 14-bit components and an 8-bit duration into eight
# bytes, so a record's duration is its last byte.
QUAT14_KF_TYPE = 6
QUAT14_RECORD_SIZE = 8


def _encode_rotation_track(frames, kf_type=QUAT14_KF_TYPE, version=VERSION_51):
    from albam.engines.mtfw.animation import LMTKeyFrames

    encoder = LMTKeyFrames()
    encoder.version = version
    encoder.track_type = "rotation_quaternion"
    encoder.encode_framedata(kf_type, 0, frames, usage=0)
    (track,) = encoder.encoded_frames
    return track


def _durations(track):
    data = track.data
    return [data[i + QUAT14_RECORD_SIZE - 1]
            for i in range(0, len(data), QUAT14_RECORD_SIZE)]


def _spin(angle_deg):
    return Quaternion((0.0, 0.0, 1.0), math.radians(angle_deg))


def test_the_last_record_terminates_the_track():
    """A zero duration is the only thing that stops the engine walking.

    Records are walked by accumulating durations with no bound from len_data,
    so a final record carrying a real duration lets the read continue past the
    track - and past the buffer, for the last track in a file.
    """
    track = _encode_rotation_track({0.0: _spin(10), 4.0: _spin(20), 9.0: _spin(30)})

    assert _durations(track)[-1] == 0


def test_frames_sharing_a_number_do_not_truncate_the_track():
    """A zero duration before the end would silently cut the track short."""
    track = _encode_rotation_track({0.0: _spin(10), 4.0: _spin(20),
                                    4.0000001: _spin(25), 9.0: _spin(30)})
    durations = _durations(track)

    assert all(d > 0 for d in durations[:-1]), durations


def test_a_gap_wider_than_the_field_is_clamped_not_wrapped():
    """Eight bits cannot express a 300-frame gap.

    Letting it wrap would put a small duration - or a zero, ending the track -
    where a long hold was meant.
    """
    track = _encode_rotation_track({0.0: _spin(10), 300.0: _spin(20)})
    durations = _durations(track)

    assert durations[0] == 0xFF
    assert durations[-1] == 0


def test_a_buffer_type_the_evaluator_ignores_is_refused():
    """Type 9 is decoded for translation and scale, never for rotation.

    The engine would fall through to a default and freeze the bone at zero
    rather than fail, so this has to be caught on the way out.
    """
    with pytest.raises(ValueError, match="not decoded for rotation_quaternion"):
        _encode_rotation_track({0.0: _spin(10), 4.0: _spin(20)}, kf_type=9)


# The event attribute's `group` is a u4 in the file and the game's own files
# set bit 31 of it, but Blender's IntProperty is signed. These two guard the
# fold that lets the value survive the trip through Blender unchanged.
@pytest.mark.parametrize("unsigned", [
    0,
    1,
    0x7FFFFFFF,
    0x80000000,      # the smallest value that overflows a signed IntProperty
    0x80000001,
    0x88010000,      # the largest seen in a real re5 file
    0xFFFFFFFF,
])
def test_unsigned_32_survives_the_fold_into_a_signed_property(unsigned):
    from albam.engines.mtfw.animation import to_signed_32, to_unsigned_32

    signed = to_signed_32(unsigned)
    assert -0x80000000 <= signed <= 0x7FFFFFFF, "must fit a Blender IntProperty"
    assert to_unsigned_32(signed) == unsigned


def test_fold_leaves_values_a_signed_property_already_holds_alone():
    from albam.engines.mtfw.animation import to_signed_32

    for already_fine in (0, 1, 900, 0x7FFFFFFF):
        assert to_signed_32(already_fine) == already_fine


class _FakeKeyframe:
    def __init__(self, frame):
        self.co = (frame, 0.0)


class _FakeFcurve:
    def __init__(self, frames):
        self.keyframe_points = [_FakeKeyframe(f) for f in frames]


class _FakeAction:
    def __init__(self, last_frame):
        self.frame_range = (1.0, float(last_frame))


class _FakeProps:
    def __init__(self, num_frames):
        self.num_frames = num_frames


def test_a_block_that_never_moves_keeps_its_length():
    """A constant track needs one keyframe, however long the block runs.

    Reading the length off the action there turns a static hold into a single
    frame: the pose stays right and the timing is destroyed, which is worse
    than a wrong pose because nothing about the exported file looks wrong.
    """
    from albam.engines.mtfw.animation.animation_export import _block_length

    action = _FakeAction(1)
    fcurves = [_FakeFcurve([1.0]) for _ in range(57)]
    assert _block_length(action, fcurves, _FakeProps(60)) == 60


def test_an_action_with_keyframes_decides_its_own_length():
    """Including when the intent is to shorten the block - an edited action is
    the authority on how long it runs, so the stored length must not win.
    """
    from albam.engines.mtfw.animation.animation_export import _block_length

    action = _FakeAction(30)
    fcurves = [_FakeFcurve([1.0, 15.0, 30.0])]
    assert _block_length(action, fcurves, _FakeProps(150)) == 30


def test_a_block_with_no_stored_length_falls_back_to_the_action():
    """A block built from scratch has nothing stored to fall back to."""
    from albam.engines.mtfw.animation.animation_export import _block_length

    action = _FakeAction(1)
    fcurves = [_FakeFcurve([1.0])]
    assert _block_length(action, fcurves, _FakeProps(0)) == 1


def test_restoring_w_survives_a_quantized_over_unit_quaternion():
    """A stored x/y/z can already sum past unit norm.

    Quantization does it on its own, and it shows up where w is near zero -
    rare, but present in real files. Rebuilding w with an unclamped square root
    raises there, which would let albam write a track it cannot read back.
    """
    from albam.engines.mtfw.animation import LMTKeyFrames

    class _Kf:
        # x^2 + y^2 + z^2 == 1.000289, straight from a real single-frame track
        x, y, z = -0.98218, 0.0, -0.18872

    restored = LMTKeyFrames().restore_w(_Kf())
    assert restored.w == 0.0
    assert restored.x == pytest.approx(-0.98218)


def test_a_rotation_that_misses_unit_norm_still_round_trips():
    """Real files carry quaternions a fraction off unit length.

    Scaling a quaternion does not change the rotation it names, so nothing is
    wrong with those values - but a buffer type that stores only x, y and z
    rebuilds w as sqrt(1 - x^2 - y^2 - z^2), which is the right answer only for
    a unit quaternion. Feed it a slightly long one and the rebuilt w is wrong,
    worst of all where w is small: a norm off by 4e-4 came back as a rotation
    off by 1.7 degrees.
    """
    unit = Quaternion((0.02, 0.7, 0.1, 0.707)).normalized()
    stretched = Quaternion([c * 1.0004 for c in unit])
    assert stretched.magnitude != pytest.approx(1.0, abs=1e-6), "test value must not be unit"

    decoded, _track = _round_trip_rotation(stretched)
    drift = math.degrees(decoded.normalized().rotation_difference(unit).angle)
    drift = min(drift, abs(360.0 - drift))
    assert drift < 0.05, f"rotation drifted {drift:.4f} deg"
