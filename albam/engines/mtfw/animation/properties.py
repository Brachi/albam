"""The shape .lmt data takes while it sits in a .blend.

Blender keeps these on the objects an import creates, and an export reads them
back off. They belong to neither half, which is why they live on their own -
and they are the only part of an .lmt that survives saving the file.
"""
import bpy

from ....registry import blender_registry
from .keyframes import to_signed_32, to_unsigned_32


@blender_registry.register_blender_type
class CustomPropsBase(bpy.types.PropertyGroup):
    """
    Base class for custom properties that provides methods
    for copying attributes
    """
    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            setattr(dst_obj, attr_name, getattr(self, attr_name))

    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                setattr(self, attr_name, getattr(src_obj, attr_name))
            except AttributeError:
                pass


@blender_registry.register_custom_properties_object("lmt_51_anim", ("re5",), asset_type="ANIMATION")
@blender_registry.register_blender_prop
class LMT51AnimationCustomProperties(CustomPropsBase):
    generate_new: bpy.props.BoolProperty(
        name="Generate new animation",
        default=False,
        options=set(),
    )
    ofs_frame: bpy.props.IntProperty(name="Offset", default=0, options=set())  # noqa: F821
    num_tracks: bpy.props.IntProperty(name="Number of Tracks", default=0, options=set())  # noqa: F821
    num_frames: bpy.props.IntProperty(name="Number of Frames", default=0, options=set())  # noqa: F821
    loop_frame: bpy.props.IntProperty(name="Loop Frame", default=0, options=set())  # noqa: F821
    init_position: bpy.props.FloatVectorProperty(
        name="Initial Position", size=3, default=(0.0, 0.0, 0.0), options=set())  # noqa: F821
    init_quaterion: bpy.props.FloatVectorProperty(
        name="Initial Quaternion", size=4, default=(1.0, 0.0, 0.0, 0.0), options=set())  # noqa: F821
    action: bpy.props.PointerProperty(
        name="Stored Action",  # noqa: F821
        type=bpy.types.Action
    )


# Everything below that carries version 67 - this group, SeqInfo, KeyInfo,
# KeyBlock, FrameBounds, LMT67Track - is filled in by an import that no longer
# runs, since .lmt import is registered for re5 alone. Registered anyway: they
# are what a .blend saved by an older albam still holds, and dropping them
# would make those files unreadable.
@blender_registry.register_custom_properties_object("lmt_67_anim",
                                                    ("re0", "re1", "re6",
                                                     "rev1", "rev2", "dd",),
                                                    asset_type="ANIMATION")
@blender_registry.register_blender_prop
class LMT67AnimationCustomProperties(CustomPropsBase):
    generate_new: bpy.props.BoolProperty(
        name="Generate new animation",  # noqa: F821
        default=False,
        options=set(),
    )
    ofs_frame: bpy.props.IntProperty(name="Offset", default=0, options=set())  # noqa: F821
    num_tracks: bpy.props.IntProperty(name="Number of Tracks", default=0, options=set())  # noqa: F821
    num_frames: bpy.props.IntProperty(name="Number of Frames", default=0, options=set())  # noqa: F821
    loop_frame: bpy.props.IntProperty(name="Loop Frame", default=0, options=set())  # noqa: F821
    init_position: bpy.props.FloatVectorProperty(
        name="Initial Position", size=3, default=(0.0, 0.0, 0.0), options=set())  # noqa: F821
    init_quaterion: bpy.props.FloatVectorProperty(
        name="Initial Quaternion", size=4, default=(1.0, 0.0, 0.0, 0.0), options=set())  # noqa: F821
    attr: bpy.props.IntProperty(name="Attr", default=0, options=set())  # noqa: F821
    kf_num: bpy.props.IntProperty(name="Keyframe Number", default=0, options=set())  # noqa: F821
    seq_num: bpy.props.IntProperty(name="Sequence Number", default=0, options=set())  # noqa: F821
    duplicate: bpy.props.IntProperty(name="Duplicate", default=0, options=set())  # noqa: F821
    reserved: bpy.props.IntProperty(name="Reserved", default=0, options=set())  # noqa: F821
    action: bpy.props.PointerProperty(
        name="Stored Action",  # noqa: F821
        type=bpy.types.Action
    )


@blender_registry.register_blender_prop
class LMT51Attribute(CustomPropsBase):
    """One event attribute: the group it belongs to, and the frame it fires on.

    Both are `u4` in the file, and the game's own files do set bit 31 of
    `group` - 0x80000000, 0x80000001, 0x88010000 - clearly a flag rather than a
    large number. Blender's IntProperty is signed, so storing that raises and
    aborts the whole import rather than degrading. Keep the same 32 bits folded
    into the signed range and fold them back on the way out, so the value
    round-trips bit for bit.
    """

    UNSIGNED_FIELDS = ("group", "frame")

    group: bpy.props.IntProperty(name="Group", default=0, options=set())  # noqa: F821
    frame: bpy.props.IntProperty(name="Frame", default=0, options=set())  # noqa: F821

    def copy_custom_properties_from(self, src_obj):
        for attr_name in self.__annotations__:
            try:
                value = getattr(src_obj, attr_name)
            except AttributeError:
                continue
            if attr_name in self.UNSIGNED_FIELDS:
                value = to_signed_32(value)
            setattr(self, attr_name, value)

    def copy_custom_properties_to(self, dst_obj):
        for attr_name in self.__annotations__:
            value = getattr(self, attr_name)
            if attr_name in self.UNSIGNED_FIELDS:
                value = to_unsigned_32(value)
            setattr(dst_obj, attr_name, value)


@blender_registry.register_custom_properties_object(
    "col_events",
    ("re5",), is_secondary=True,
    display_name="Collision Events", asset_type="ANIMATION")
@blender_registry.register_blender_prop
class ColEventsCustomProperties(CustomPropsBase):
    event_id: bpy.props.IntVectorProperty(
        name="Event ID",  # noqa: F821
        size=32,
        default=[0] * 32,
        description="Collision group ID")
    attributes: bpy.props.CollectionProperty(
        type=LMT51Attribute,
        name="Attributes",  # noqa: F821
        description="Collision attributes for each group"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",  # noqa: F821
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_custom_properties_object(
    "motion_se",
    ("re5",), is_secondary=True,
    display_name="Motion Sound Events", asset_type="ANIMATION")
@blender_registry.register_blender_prop
class MotionSECustomProperties(CustomPropsBase):
    event_id: bpy.props.IntVectorProperty(
        name="Event ID",  # noqa: F821
        size=32,
        default=[0] * 32,
        description="Collision group ID")
    attributes: bpy.props.CollectionProperty(
        type=LMT51Attribute,
        name="Attributes",  # noqa: F821
        description="Collision attributes for each group"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",  # noqa: F821
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_blender_prop
class SeqInfoAttribute(CustomPropsBase):
    unk_00: bpy.props.IntProperty(name="Unk 00", default=0, options=set())  # noqa: F821
    unk_01: bpy.props.IntProperty(name="Unk 01", default=0, options=set())  # noqa: F821
    unk_02: bpy.props.IntProperty(name="Unk 02", default=0, options=set())  # noqa: F821


@blender_registry.register_blender_prop
class SeqInfo(CustomPropsBase):
    work: bpy.props.IntVectorProperty(
        name="Work",  # noqa: F821
        size=32,
        default=[0] * 32,
    )
    attributes: bpy.props.CollectionProperty(
        type=SeqInfoAttribute,
        name="Attributes"  # noqa: F821
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",  # noqa: F821
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_custom_properties_object(
    "sequence_infos",
    ("re0", "re1", "rev1", "rev2", "re6",), is_secondary=True,
    display_name="Sequence Infos", asset_type="ANIMATION")
@blender_registry.register_blender_prop
class SequenceInfoProperties(CustomPropsBase):
    sequence_info: bpy.props.CollectionProperty(
        type=SeqInfo,
        name="Sequence Info"  # noqa: F821
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",  # noqa: F821
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_blender_prop
class KeyBlock(CustomPropsBase):
    unk_00: bpy.props.IntProperty(
        name="Unk 00",  # noqa: F821
        default=0
    )
    unk_01: bpy.props.IntProperty(
        name="Unk 01",  # noqa: F821
        default=0
    )
    unk_02: bpy.props.FloatProperty(
        name="Unk 02",  # noqa: F821
        default=0
    )
    unk_03: bpy.props.FloatProperty(
        name="Unk 03",  # noqa: F821
        default=0
    )
    unk_04: bpy.props.FloatProperty(
        name="Unk 04",  # noqa: F821
        default=0
    )


@blender_registry.register_blender_prop
class KeyInfo(CustomPropsBase):
    type: bpy.props.IntProperty(
        name="Type", default=0, options=set())  # noqa: F821
    work: bpy.props.IntProperty(
        name="Work", default=0, options=set())  # noqa: F821
    attr: bpy.props.IntProperty(
        name="Attr", default=0, options=set())  # noqa: F821
    keyframe_blocks: bpy.props.CollectionProperty(
        type=KeyBlock
    )


@blender_registry.register_custom_properties_object(
    "keyframe_infos",
    ("re0", "re1", "rev1", "rev2", "re6",), is_secondary=True,
    display_name="Keyframe Infos", asset_type="ANIMATION")
@blender_registry.register_blender_prop
class KeyframeInfoProperties(CustomPropsBase):
    keyframe_info: bpy.props.CollectionProperty(
        type=KeyInfo,
        name="Keyframe Info"  # noqa: F821
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",  # noqa: F821
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_blender_prop
class LMT51Track(CustomPropsBase):
    buffer_type: bpy.props.IntProperty(
        name="Buffer Type",  # noqa: F821
        default=0,
        options=set(),
        description="Type of buffer used for this track")
    usage: bpy.props.IntProperty(
        name="Usage",  # noqa: F821
        default=0,
        options=set(),
        description="Track type")
    joint_type: bpy.props.IntProperty(
        name="Joint Type",  # noqa: F821
        default=0,
        options=set())
    bone_index: bpy.props.IntProperty(
        name="Bone Index",  # noqa: F821
        default=0,
        options=set(),
        description="Animation index of the bone in the armature")
    weight: bpy.props.FloatProperty(
        name="Weight",  # noqa: F821
        default=1.0,
        options=set(),
        description="Weight of the track, used for blending")
    reference_data: bpy.props.FloatVectorProperty(
        name="Reference Data",  # noqa: F821
        size=4,
        default=(0.0, 0.0, 0.0, 1.0),
        options=set(),
        description="Reference data for the track, used for blending"
    )
    raw_data: bpy.props.StringProperty(
        name="Raw Data",  # noqa: F821
        description="Raw binary data for this track",
        subtype='BYTE_STRING'  # noqa: F821
    )


@blender_registry.register_blender_prop
class FrameBounds(CustomPropsBase):
    addin: bpy.props.FloatVectorProperty(
        name="AddIn",  # noqa: F821
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        options=set(),
    )
    offset: bpy.props.FloatVectorProperty(
        name="Offset",  # noqa: F821
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        options=set(),
    )


@blender_registry.register_blender_prop
class LMT67Track(CustomPropsBase):
    buffer_type: bpy.props.IntProperty(
        name="Buffer Type",  # noqa: F821
        default=0,
        options=set(),
        description="Type of buffer used for this track")
    usage: bpy.props.IntProperty(
        name="Usage",  # noqa: F821
        default=0,
        options=set(),
        description="Track type")
    joint_type: bpy.props.IntProperty(
        name="Joint Type",  # noqa: F821
        default=0,
        options=set())
    bone_index: bpy.props.IntProperty(
        name="Bone Index",  # noqa: F821
        default=0,
        options=set(),
        description="Animation index of the bone in the armature")
    weight: bpy.props.FloatProperty(
        name="Weight",  # noqa: F821
        default=1.0,
        options=set(),
        description="Weight of the track, used for blending")
    reference_data: bpy.props.FloatVectorProperty(
        name="Reference Data",  # noqa: F821
        size=4,
        default=(0.0, 0.0, 0.0, 1.0),
        options=set(),
        description="Reference data for the track, used for blending"
    )
    raw_data: bpy.props.StringProperty(
        name="Raw Data",  # noqa: F821
        description="Raw binary data for this track",
        subtype='BYTE_STRING'  # noqa: F821
    )
    track_bounds: bpy.props.CollectionProperty(
        type=FrameBounds,
        name="Frame Bounds",  # noqa: F821
    )


@blender_registry.register_custom_properties_object(
    "tracks",
    ("re5",), is_secondary=True,
    display_name="Animation Tracks", asset_type="ANIMATION")
@blender_registry.register_blender_prop
class AnimTrackCustomProperties(CustomPropsBase):
    tracks: bpy.props.CollectionProperty(
        type=LMT51Track,
        name="Tracks",  # noqa: F821
        description="Animation tracks for the LMT file"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",  # noqa: F821
        description="Allows to select an item from the collection",
        default=0
    )


@blender_registry.register_custom_properties_object(
    "tracks",
    ("re0", "re1", "rev1", "rev2", "re6",), is_secondary=True,
    display_name="Animation Tracks", asset_type="ANIMATION")
@blender_registry.register_blender_prop
class AnimTrack67CustomProperties(CustomPropsBase):
    tracks: bpy.props.CollectionProperty(
        type=LMT67Track,
        name="Tracks",  # noqa: F821
        description="Animation tracks for the LMT file"
    )
    item_index: bpy.props.IntProperty(
        name="Item Index",  # noqa: F821
        description="Allows to select an item from the collection",
        default=0
    )
