"""The "Custom Properties (Albam)" panel on the Bone properties tab.

Synthetic: builds its own armature, no game data needed. See #286.
"""

from types import SimpleNamespace

import bpy


def test_bone_panel_polls_true_off_active_pose_bone_not_pose_bone():
    """The Properties Editor's Bone tab never populates context.pose_bone.

    Confirmed live in Blender 5.2: with a bone made active in Pose Mode,
    Blender's own built-in Bone panels render fine off context.bone and
    context.active_pose_bone, but context.pose_bone is never set - so a panel
    reading it, like this one used to, silently never shows. This context
    stands in for that real one: bone and active_pose_bone set, pose_bone
    absent entirely, the way Blender's own Properties Editor presents it.
    """
    from albam.blender_ui.custom_properties import ALBAM_PT_CustomPropertiesBone
    from albam.engines.mtfw.bone import set_anim_retarget

    armature_data = bpy.data.armatures.new("bone_panel_rig")
    armature = bpy.data.objects.new("bone_panel_rig", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous = bpy.context.view_layer.objects.active
    try:
        armature.albam_asset.app_id = "re5"
        armature.albam_asset.relative_path = "pawn/pl/pl00/model/pl0000.mod"
        armature.albam_asset.asset_type = "MODEL"

        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        edit_bone = armature_data.edit_bones.new("0")
        edit_bone.tail = (0.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")

        pose_bone = armature.pose.bones["0"]
        set_anim_retarget(pose_bone, "re5", "0")

        context = SimpleNamespace(bone=armature_data.bones["0"], active_pose_bone=pose_bone)

        assert not hasattr(context, "pose_bone")
        assert ALBAM_PT_CustomPropertiesBone.poll(context) is True
    finally:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(armature_data)
        bpy.context.view_layer.objects.active = previous
