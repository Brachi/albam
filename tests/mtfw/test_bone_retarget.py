"""The animation id albam keeps on each pose bone (albam/engines/mtfw/bone.py).

All synthetic: these build their rigs directly, no game data needed.
"""

import bpy


def test_anim_ids_are_the_rigs_own_and_survive_renaming_its_bones():
    """The mapping is independent of bone names, which any rename may change.

    A bone the .mod mapped to nothing stays out of it, rather than claiming
    the empty id.
    """
    from albam.engines.mtfw.animation.animation_import import _create_bone_mapping
    from albam.engines.mtfw.bone import get_anim_retarget, set_anim_retarget

    armature_data = bpy.data.armatures.new("retarget_rig")
    armature = bpy.data.objects.new("retarget_rig", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous = bpy.context.view_layer.objects.active
    try:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        for name in ("0", "1", "2", "3"):
            edit_bone = armature_data.edit_bones.new(name)
            edit_bone.tail = (0.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")

        for name, anim_id in (("0", "0"), ("1", "7"), ("2", "255")):
            set_anim_retarget(armature.pose.bones[name], "re5", anim_id)
        # "3" is left alone: a bone the .mod mapped to no animation id

        assert _create_bone_mapping(armature, "re5") == {"0": "0", "7": "1", "255": "2"}

        for name, renamed in (("0", "root"), ("1", "hips"), ("2", "root_motion")):
            armature.pose.bones[name].name = renamed

        assert _create_bone_mapping(armature, "re5") == {
            "0": "root", "7": "hips", "255": "root_motion"
        }
        assert get_anim_retarget(armature.pose.bones["hips"], "re5") == "7"
    finally:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(armature_data)
        bpy.context.view_layer.objects.active = previous


def test_autorenaming_bones_keeps_them_addressable_by_animation_id():
    """Autorename Bones renames by animation id, and must not consume it.

    It also runs over rigs an animation import has added control bones to,
    which answer to "<id>_<n>" and belong to no body part; reading one as a
    number used to be a ValueError that took the whole tool down.
    """
    from albam.blender_ui.tools import rename_bones
    from albam.engines.mtfw.animation.animation_import import _create_bone_mapping
    from albam.engines.mtfw.bone import set_anim_retarget

    armature_data = bpy.data.armatures.new("autorename_rig")
    armature = bpy.data.objects.new("autorename_rig", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous = bpy.context.view_layer.objects.active
    try:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        for name in ("0", "1", "IK_Foot.R"):
            edit_bone = armature_data.edit_bones.new(name)
            edit_bone.tail = (0.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")
        for name, anim_id in (("0", "0"), ("1", "1"), ("IK_Foot.R", "19_1")):
            set_anim_retarget(armature.pose.bones[name], "re5", anim_id)

        rename_bones(armature, "re5", "Body")

        # BONES_BODY names ids 0 and 1; the control bone is not a body part
        assert set(armature.pose.bones.keys()) == {"root", "spine_lower", "IK_Foot.R"}
        assert _create_bone_mapping(armature, "re5") == {
            "0": "root", "1": "spine_lower", "19_1": "IK_Foot.R"
        }
    finally:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(armature_data)
        bpy.context.view_layer.objects.active = previous


def test_a_rig_saved_before_the_move_still_maps_its_bones():
    """.blend files predating the move carry the id as a raw bone property.

    Reading nothing there would leave every bone unmapped, so an animation
    imported onto such a rig would build a second skeleton out of missing
    bones. The read finds the old property and moves it across.
    """
    from albam.engines.mtfw.animation.animation_import import _create_bone_mapping
    from albam.engines.mtfw.bone import (
        LEGACY_ANIM_RETARGET_PROP,
        get_bone_custom_properties,
    )

    armature_data = bpy.data.armatures.new("legacy_rig")
    armature = bpy.data.objects.new("legacy_rig", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous = bpy.context.view_layer.objects.active
    try:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        for name in ("0", "1"):
            edit_bone = armature_data.edit_bones.new(name)
            edit_bone.tail = (0.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")
        for name, anim_id in (("0", "0"), ("1", "7")):
            armature_data.bones[name][LEGACY_ANIM_RETARGET_PROP] = anim_id

        assert _create_bone_mapping(armature, "re5") == {"0": "0", "7": "1"}
        assert get_bone_custom_properties(armature.pose.bones["1"], "re5").anim_retarget == "7", (
            "reading it should have moved it onto the pose bone"
        )
    finally:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(armature_data)
        bpy.context.view_layer.objects.active = previous


def test_a_created_root_motion_bone_carries_the_id_it_was_created_for():
    """Bones an import adds get their id after edit mode, not during it.

    A pose bone exists only once its edit bone has been committed, so a write
    inside the edit-mode block would land on nothing.
    """
    from albam.engines.mtfw.animation.animation_import import (
        ROOT_MOTION_BONE_NAME,
        _create_bone_mapping,
        _get_or_create_root_motion_bone,
    )
    from albam.engines.mtfw.bone import get_anim_retarget, set_anim_retarget

    armature_data = bpy.data.armatures.new("root_motion_rig")
    armature = bpy.data.objects.new("root_motion_rig", armature_data)
    bpy.context.scene.collection.objects.link(armature)
    previous = bpy.context.view_layer.objects.active
    try:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        edit_bone = armature_data.edit_bones.new("0")
        edit_bone.tail = (0.0, 0.0, 0.1)
        bpy.ops.object.mode_set(mode="OBJECT")
        set_anim_retarget(armature.pose.bones["0"], "re5", "0")

        mapping = _create_bone_mapping(armature, "re5")
        created = _get_or_create_root_motion_bone(armature, mapping, "re5")

        assert created == ROOT_MOTION_BONE_NAME
        assert get_anim_retarget(armature.pose.bones[created], "re5") == "255"
        # and the skeleton's root now rides it
        assert any(c.subtarget == created for c in armature.pose.bones["0"].constraints)
    finally:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(armature_data)
        bpy.context.view_layer.objects.active = previous
