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
