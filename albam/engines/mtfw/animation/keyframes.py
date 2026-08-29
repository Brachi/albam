"""The .lmt keyframe codec: a track's bytes to poses and back again.

Every buffer type the format uses is decoded and encoded here, along with the
quantization each one applies. Nothing in this module touches Blender beyond
mathutils, which is what lets the codec tests drive it directly.
"""
import math
from io import BytesIO

from kaitaistruct import KaitaiStream
from mathutils import Quaternion, Vector

from ..structs.lmt import Lmt


# usages that carry a position rather than a rotation or a scale
TRANSLATION_USAGES = {1, 4}
BOUNDS_BUFF_TYPES = [4, 5, 7, 11, 12, 13, 14, 15]
# Usage
# U_QUATERNION = 0x0, Local Rotation
# U_TRANSLATE = 0x1,  Local Position
# U_SCALE = 0x2, Local Scale
# U_NULL_QUATERNION = 0x3, Absolute Rotation
# U_NULL_TRANSLATE = 0x4, Absolute Position
# U_NULL_SCALE = 0x5, Unknown
USAGE = {
    0: "rotation_quaternion",  # Local rotation
    1: "location",  # Local Position
    2: "scale",  # Local Scale
    3: "rotation_quaternion",  # Absolute Rotation
    4: "location",  # Absolute Position
    5: "scale",  # Unknown
}
# the only channels of an action that are a bone's transform, and so the only
# ones an exported track can come from
BONE_TRACK_TYPES = set(USAGE.values())

APPID_VERSION_MAPPER = {
    "re0": 67,
    "re1": 67,
    "re5": 51,
    "re6": 67,
    "rev1": 67,
    "rev2": 67,
    "dd": 67,
}

KEYFRAME_TYPES_51 = {
    1: Lmt.Vec3Frame12,  # LMTVec3 but tests didn't find it in re games
    2: Lmt.Vec3Frame12,
    3: Lmt.Vec3Frame16,
    4: Lmt.Quat3Frame,  # Lmt.Quatized16Vec3 for ver55+
    5: Lmt.QuadraticVector3,  # Lmt.Quatized8Vec3 for ver55+
    6: Lmt.QuatFramev14,  # Lmt.PolarFrame for ver50-
    7: Lmt.Quatized32Quat,
    9: Lmt.Vec3Frame16,
    11: Lmt.XwQuat,
    12: Lmt.YwQuat,
    13: Lmt.ZwQuat,
    14: Lmt.Quatized11Quat,
    15: Lmt.Quatized9Quat,
}

KEYFRAME_TYPES_67 = KEYFRAME_TYPES_51.copy()
KEYFRAME_TYPES_67.update({
    4: Lmt.Quatized16Vec3,
    5: Lmt.Quatized8Vec3,
})

KEYFRAME_TYPES = {
    51: KEYFRAME_TYPES_51,
    67: KEYFRAME_TYPES_67
}

# Rotation buffer types that store x, y and z but no w, leaving decoding to
# rebuild it with LMTKeyFrames.restore_w().
W_REBUILT_FROM_XYZ_TYPES = {4}


# The widest duration each buffer type can carry, for the types that carry one
# at all. A track is walked by accumulating these until they pass the requested
# time, so a gap wider than the field can hold cannot be expressed in a single
# record.
KEYFRAME_DURATION_MAX = {
    3: 0xFFFFFFFF,  # Vec3Frame16, u4
    6: 0xFF,        # QuatFramev14, 8 bits
    9: 0xFFFFFFFF,  # Vec3Frame16, u4
}

# Which buffer types the engine decodes for a track, keyed by the channel whose
# usage selects the evaluator. A buffer type its evaluator does not handle falls
# through to a default that yields zeros, so the pose comes out wrong silently
# rather than failing.
EVALUATOR_BUFFER_TYPES_51 = {
    "rotation_quaternion": {3, 4, 6, 7},
    "location": {1, 2, 9},
    "scale": {1, 2, 9},
}


# Unused for now but maybe LMTQuadraticVector3 will need it
class ActionKey:
    def __init__(self):
        self.location = None  # Vector((0.0, 0.0, 0.0))
        self.rotation_quaternion = None  # Quaternion((1.0, 0.0, 0.0, 0.0))
        self.scale = None  # Vector((0.0, 0.0, 0.0))


class QuantizedKey:
    def __init__(self):
        self.w = 0
        self.x = 0
        self.y = 0
        self.z = 0


class LMTKeyFrames:
    def __init__(self):
        self.version = 0
        self.bounds = None
        self.size = 0
        self.track_type = ""
        self.decoded_frames = []
        self.encoded_frames = []

    def decode_framedata(self, version, key_type, data):
        kfcls = KEYFRAME_TYPES[version].get(key_type, None)
        if kfcls is None:
            print("Unknown keyframe type:", key_type)
            return
        keyframe = kfcls()  # hack to get the size before reading
        for start in range(0, len(data), keyframe.size_):
            chunk = data[start: start + keyframe.size_]
            frame = kfcls(KaitaiStream(BytesIO(chunk)))
            frame._read()
            duration = getattr(frame, "duration", 1)
            dframe = None
            if self.track_type == "rotation_quaternion":
                if key_type == 4:  # Quat3Frame
                    dframe = self.restore_w(frame)
                elif key_type in (6, 7, 11, 12, 13, 14, 15):
                    dframe = self.dequantaize(frame, key_type)
                else:
                    dframe = self.to_quat(frame)
                if key_type in BOUNDS_BUFF_TYPES and self.bounds:
                    dframe = self.bounds.lerpq(dframe)
            else:
                if key_type in BOUNDS_BUFF_TYPES and self.bounds:
                    dframe = self.to_vec3(self.bounds.lerp3(frame), self.track_type, key_type)
                else:
                    dframe = self.to_vec3(frame, self.track_type, key_type)
            self.decoded_frames.append(dframe)
            if duration:
                self.decoded_frames.extend([None] * (duration - 1))

    def encode_framedata(self, kf_type, bone_index, track, usage, static=False):
        # Track51 and Track67 share every field encode_framedata touches (the
        # extra ofs_bounds/bounds Track67 carries are filled in later by
        # export_lmt, not here), so one code path serializes both.
        track_cls = Lmt.Track51 if self.version == 51 else Lmt.Track67
        dst_track = track_cls(_parent=None, _root=None)
        dst_track.buffer_type = kf_type
        dst_track.usage = usage
        dst_track.joint_type = 0
        dst_track.bone_index = bone_index
        dst_track.reference_data = []

        if static:
            # A single value for the whole block (a non-animating bone).
            # Real re1/re6/... (v67) files store this with no track data at
            # all - the value lives purely in reference_data. This matters
            # because v67 renumbers several buffer_type ids to unrelated
            # physical layouts (e.g. type 4 is Quat3Frame - a bare
            # quaternion - in v51 but Quatized16Vec3 - a quantized location
            # triplet - in v67, see KEYFRAME_TYPES_67), and some of those
            # ids additionally require bounds data this exporter never
            # populates for freshly generated tracks. len_data=0 sidesteps
            # both problems, matching the real on-disk convention (re5/v51
            # doesn't use this shortcut: every sampled real single-frame v51
            # rotation track does carry one genuine kf_type 4 record).
            ((frame, value),) = track.items()
            if self.track_type == "rotation_quaternion":
                dst_track.reference_data = [value.x, value.y, value.z, value.w]
            elif self.track_type == "location":
                value = value * 100
                dst_track.reference_data = [value.x, value.y, value.z, 1.0]
            else:
                dst_track.reference_data = [value.x, value.y, value.z, 1.0]
            dst_track.data = b""
            self.encoded_frames.append(dst_track)
            return

        dst_raw_data = bytearray()
        kfcls = KEYFRAME_TYPES[self.version].get(kf_type, None)
        if kfcls is None:
            print("Unknown keyframe type:", kf_type)
            return
        self._check_buffer_type(kf_type)
        duration_max = KEYFRAME_DURATION_MAX.get(kf_type)
        i = 0
        frames_time = [ft for ft in track.keys()]
        for frame, value in track.items():
            kf = kfcls()
            if self.track_type == "rotation_quaternion":
                value = self.canonicalize(value, kf_type)
                if not dst_track.reference_data:
                    dst_track.reference_data = [value.x, value.y, value.z, value.w]
                value = self.quantaize(value, kf_type)
                kf.w = value.w
            elif self.track_type == "location":
                value = value * 100
                if not dst_track.reference_data:
                    dst_track.reference_data = [value.x, value.y, value.z, 1.0]
            elif self.track_type == "scale":
                if not dst_track.reference_data:
                    dst_track.reference_data = [value.x, value.y, value.z, 1.0]
            kf.x = value.x
            kf.y = value.y
            kf.z = value.z
            is_last = i + 1 >= len(frames_time)
            if is_last:
                # A zero duration is what ends the track. The engine walks
                # records by accumulating durations and stops on the first
                # zero, with no bound from len_data, so a last record that
                # carried a real duration would let it read past the track
                # and, for the last track in a file, past the buffer.
                duration = 0
            else:
                # Clamped to at least one: a zero here would terminate the
                # walk early and silently truncate the track, which is what
                # two keyframes sharing a frame number would otherwise
                # produce.
                duration = max(1, int(frames_time[i + 1] - frame))
                if duration_max is not None and duration > duration_max:
                    print(f"albam: keyframe gap of {duration} frames on bone "
                          f"{bone_index} exceeds what buffer type {kf_type} can "
                          f"store; clamped to {duration_max}")
                    duration = duration_max
            i += 1
            kf.duration = int(duration)
            stream = KaitaiStream(BytesIO(bytearray(kf.size_)))
            kf._check()
            kf._write(stream)
            dst_raw_data.extend(stream.to_byte_array())
        dst_track.data = bytes(dst_raw_data)
        self.encoded_frames.append(dst_track)

    def _check_buffer_type(self, kf_type):
        """Refuse a buffer type the channel's evaluator does not decode.

        Getting this wrong produces a file that loads and plays, with the
        affected bones simply frozen at zero - the evaluator falls through to
        a default rather than complaining - so it is worth failing loudly here
        instead.
        """
        if self.version != 51:
            return
        allowed = EVALUATOR_BUFFER_TYPES_51.get(self.track_type)
        if allowed is not None and kf_type not in allowed:
            raise ValueError(
                f"buffer type {kf_type} is not decoded for {self.track_type} "
                f"tracks; version 51 accepts {sorted(allowed)}"
            )

    def dequantaize(self, kf, key_type):
        dkf = Quaternion((0.0, 0.0, 0.0, 0.0))
        if key_type in (11, 12, 13):
            if getattr(kf, "w", None):
                if self.bounds:
                    dkf.w = kf.w * 0.000061039
                else:
                    dkf.w = self.clip_and_divide(kf.w, qw=True)
            if getattr(kf, "x", None):
                if self.bounds:
                    dkf.x = kf.x * 0.000061039  # 1/16383
                else:
                    dkf.x = self.clip_and_divide(kf.x, qw=True)
            if getattr(kf, "y", None):
                if self.bounds:
                    dkf.y = kf.y * 0.000061039
                else:
                    dkf.y = self.clip_and_divide(kf.y, qw=True)
            if getattr(kf, "z", None):
                if self.bounds:
                    dkf.z = kf.z * 0.000061039
                else:
                    dkf.z = self.clip_and_divide(kf.z, qw=True)
        elif key_type == 7:
            dkf.w = (kf.w - 8) * 0.0089285718
            dkf.x = (kf.x - 8) * 0.0089285718
            dkf.y = (kf.y - 8) * 0.0089285718
            dkf.z = (kf.z - 8) * 0.0089285718
        elif key_type == 6:
            dkf.w = self.clip_and_divide(kf.w)
            dkf.x = self.clip_and_divide(kf.x)
            dkf.y = self.clip_and_divide(kf.y)
            dkf.z = self.clip_and_divide(kf.z)
        return dkf

    def canonicalize(self, kf, key_type):
        """The w >= 0 form of a rotation, for buffer types that drop w.

        restore_w() rebuilds w as a positive square root, so a quaternion
        stored with w < 0 decodes to a different rotation. Negating all four
        components names the same rotation with w >= 0, which does survive.
        Types that store w keep whichever sign they were given.
        """
        if key_type not in W_REBUILT_FROM_XYZ_TYPES or kf.w >= 0:
            return kf
        return Quaternion((-kf.w, -kf.x, -kf.y, -kf.z))

    def restore_w(self, kf):
        # Always the positive root: see canonicalize(), which is what keeps
        # that from silently changing the rotation.
        w = math.sqrt(1.0 - kf.x**2 - kf.y**2 - kf.z**2)
        frame = Quaternion((w, kf.x, kf.y, kf.z))
        return frame

    def to_quat(self, kf):
        return Quaternion((kf.w, kf.x, kf.y, kf.z))

    def to_vec3(self, kf, track_type, key_type):
        dkf = Vector((kf.x, kf.y, kf.z))
        if key_type == 4:
            dkf = dkf / 65535.0  # restore 16
        elif key_type == 5 and self.version == 67:
            dkf = dkf / 255.0  # restore 8
        if track_type == "location":
            dkf = dkf / 100
        return dkf

    def quantaize(self, kf, type):
        qkf = QuantizedKey()
        if type == 6:
            qkf.w = self.unclip_and_multiply(kf.w)
            qkf.x = self.unclip_and_multiply(kf.x)
            qkf.y = self.unclip_and_multiply(kf.y)
            qkf.z = self.unclip_and_multiply(kf.z)
        else:
            return kf
        return qkf

    def clip_and_divide(self, num, qw=False):
        """
        Restore a sign from an usigned int value and convert to float
        """
        RANGE_ALL = 2 ** 14  # 16384
        RANGE_SPLIT = 2 ** 13 - 1  # 8191
        DIVIDER = 4096 if not qw else 8192
        if num > RANGE_SPLIT:
            num -= RANGE_ALL
        return num / DIVIDER

    def unclip_and_multiply(self, val, qw=False):
        RANGE_ALL = 2 ** 14
        # RANGE_SPLIT = 2 ** 13 - 1
        DIVIDER = 8192 if qw else 4096

        signed = int(round(val * DIVIDER))
        # Map negative signed back to unsigned storage representation
        if signed < 0:
            orig = signed + RANGE_ALL
        else:
            orig = signed
        # Clamp
        if orig < 0:
            orig = 0
        if orig > RANGE_ALL:
            orig = RANGE_ALL

        return int(orig)


class LMTKeyframeBounds:
    def __init__(self, bound):
        self.addin = bound.addin
        self.offset = bound.offset
        self.map = ["x", "y", "z", "w"]

    def lerp3(self, fraction):
        """fraction: imported vector keyframe"""
        # Returns only x, y, z (as point3)
        return Vector((
            self.offset[0] + fraction.x * self.addin[0],
            self.offset[1] + fraction.y * self.addin[1],
            self.offset[2] + fraction.z * self.addin[2],
        ))

    def lerpq(self, fraction):
        """fraction: imported quaternion keyframe"""
        # Returns quaternion (x, y, z, w)
        return Quaternion((
            self.offset[3] + fraction.w * self.addin[3],
            self.offset[0] + fraction.x * self.addin[0],
            self.offset[1] + fraction.y * self.addin[1],
            self.offset[2] + fraction.z * self.addin[2],
        ))


def to_signed_32(value):
    """The same 32 bits, as a value Blender's signed IntProperty can hold."""
    return value - 0x100000000 if value > 0x7FFFFFFF else value


def to_unsigned_32(value):
    """Undo to_signed_32, for a field the format declares as u4."""
    return value + 0x100000000 if value < 0 else value
