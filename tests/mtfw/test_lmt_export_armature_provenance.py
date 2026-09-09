"""#254: .lmt export must retarget bone ids through the armature the
animation was actually imported onto, not whichever one the import panel
happens to point at by the time export runs.

Built synthetically - two rigs authored in memory, sharing a bone name but
keyed to different animation ids - so this runs without --game-dir and
proves the mechanism directly, the same way #281's investigation drove
albam's real import/export functions against a synthetic MT Framework model.
"""
import bpy
import pytest

from albam.engines.mtfw.animation.animation_export import export_lmt
from albam.engines.mtfw.animation.animation_import import set_block_index
from albam.engines.mtfw.bone import set_anim_retarget
from albam.engines.mtfw.structs.lmt import Lmt
from albam.lib.blender import get_action_channels
from albam.lib.kaitai_utils import parse

APP_ID = "re5"


def _make_armature(name, bone_name, anim_id):
    arm_data = bpy.data.armatures.new(f"{name}_data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bone = arm_data.edit_bones.new(bone_name)
    edit_bone.head = (0.0, 0.0, 0.0)
    edit_bone.tail = (0.0, 0.0, 0.1)
    bpy.ops.object.mode_set(mode='OBJECT')
    set_anim_retarget(arm_obj.pose.bones[bone_name], APP_ID, anim_id)
    return arm_obj


def _make_action(name, armature_obj, bone_name):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    channels = get_action_channels(action, armature_obj.name)
    data_path = f'pose.bones["{bone_name}"].location'
    curves = [channels.fcurves.new(data_path=data_path, index=i) for i in range(3)]
    for frame, values in enumerate([(0.0, 0.0, 0.0), (0.1, 0.2, 0.3)], start=1):
        for curve, value in zip(curves, values):
            curve.keyframe_points.add(1)
            curve.keyframe_points[-1].co = (frame, value)
            curve.keyframe_points[-1].interpolation = 'LINEAR'
    return action


def _make_lmt_block(armature_obj, action):
    """A minimal in-memory stand-in for what load_lmt() leaves behind: a top
    .lmt object recording the armature it was imported onto, with one
    populated block underneath, set to regenerate its tracks from `action`.
    """
    bl_object = bpy.data.objects.new("synthetic_lmt", None)
    bpy.context.collection.objects.link(bl_object)
    bl_object.albam_asset.app_id = APP_ID
    bl_object.albam_asset.asset_type = "ANIMATION"
    bl_object.albam_asset.relative_path = "synthetic/anim.lmt"
    bl_object.albam_lmt_armature = armature_obj

    anim_object = bpy.data.objects.new("synthetic_lmt.0000", None)
    bpy.context.collection.objects.link(anim_object)
    anim_object.parent = bl_object
    set_block_index(anim_object, APP_ID, 0)

    custom_props = anim_object.albam_custom_properties.get_custom_properties_for_appid(APP_ID)
    custom_props.ofs_frame = 1  # non-zero: marks the block as populated
    custom_props.action = action
    custom_props.generate_new = True
    return bl_object


@pytest.fixture
def two_armatures():
    """Two rigs sharing a bone name but keyed to different animation ids -
    the situation that makes export retarget bones wrong if it reads the
    wrong rig's mapping (#254): same bone, silently renumbered.
    """
    armature_a = _make_armature("SyntheticArmatureA", "hip", "10")
    armature_b = _make_armature("SyntheticArmatureB", "hip", "20")
    yield armature_a, armature_b
    for obj in (armature_a, armature_b):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


def test_export_uses_the_stored_armature_not_the_panels(two_armatures):
    """The captain's #254 repro: import an animation onto armature A
    (recording it via albam_lmt_armature, as load_lmt now does), then point
    the import panel at armature B - the state it's left in after importing
    a second character - and export. The tracks must still carry A's ids.
    """
    armature_a, armature_b = two_armatures
    action = _make_action("SyntheticAction", armature_a, "hip")
    bl_object = _make_lmt_block(armature_a, action)

    # The panel now points at B - exactly the state the issue describes.
    bpy.context.scene.albam.import_options_lmt.armature = armature_b

    vfiles = export_lmt(bl_object)
    assert len(vfiles) == 1
    dst_lmt = parse(Lmt, vfiles[0].data_bytes, APP_ID)

    dst_block = dst_lmt.block_offsets[0]
    assert dst_block.offset != 0
    exported_ids = {t.bone_index for t in dst_block.block_header.tracks}

    assert 10 in exported_ids, (
        f"exported track ids {exported_ids} don't include A's id (10) for 'hip' - "
        "export didn't use the armature this animation was imported onto"
    )
    assert 20 not in exported_ids, (
        f"exported track ids {exported_ids} include B's id (20) for 'hip' - export "
        "used the import panel's armature instead of the one this .lmt was actually "
        "imported onto"
    )


def test_export_falls_back_to_the_panel_when_the_property_is_unset(two_armatures):
    """A .blend saved before this property existed has no albam_lmt_armature
    on its .lmt objects - export must still work, reading the panel's
    armature exactly as it always did.
    """
    armature_a, armature_b = two_armatures
    action = _make_action("SyntheticActionFallback", armature_a, "hip")
    bl_object = _make_lmt_block(armature_a, action)
    bl_object.albam_lmt_armature = None  # simulate a pre-existing scene

    bpy.context.scene.albam.import_options_lmt.armature = armature_a

    vfiles = export_lmt(bl_object)
    dst_lmt = parse(Lmt, vfiles[0].data_bytes, APP_ID)
    exported_ids = {t.bone_index for t in dst_lmt.block_offsets[0].block_header.tracks}
    assert 10 in exported_ids


def test_export_refuses_a_block_that_resolves_zero_tracks(two_armatures):
    """If none of an action's fcurve bone names resolve through the
    armature's mapping, the block would otherwise be written with
    num_tracks = 0 and a non-zero ofs_frame - a well-formed file quietly
    missing its animation (#254). Export must refuse instead.
    """
    armature_a, _armature_b = two_armatures
    action = _make_action("SyntheticActionUnmapped", armature_a, "not_a_real_bone_254")
    bl_object = _make_lmt_block(armature_a, action)

    with pytest.raises(ValueError, match="resolved zero tracks"):
        export_lmt(bl_object)


def test_export_accepts_a_block_whose_action_has_no_channels_at_all(two_armatures):
    """A genuinely empty action has no bone channels to resolve, so nothing has
    gone wrong and export must keep writing the block - the zero-track refusal
    is only for an action that had bone channels and resolved none of them.
    """
    armature_a, _armature_b = two_armatures
    empty_action = bpy.data.actions.new("SyntheticActionEmpty")
    empty_action.use_fake_user = True
    bl_object = _make_lmt_block(armature_a, empty_action)
    anim_object = bl_object.children[0]
    custom_props = anim_object.albam_custom_properties.get_custom_properties_for_appid(APP_ID)
    custom_props.num_frames = 10

    vfiles = export_lmt(bl_object)
    dst_lmt = parse(Lmt, vfiles[0].data_bytes, APP_ID)
    assert dst_lmt.block_offsets[0].block_header.num_tracks == 0
