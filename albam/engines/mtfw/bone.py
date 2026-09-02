"""Per-bone data albam keeps for an MT Framework skeleton.

Only the animation id so far: .mod's `idx_anim_map`, the engine-wide bone id
space .lmt tracks are keyed on. It is what lets an .lmt authored for one
character play on another, since import and export address bones through it
rather than through the .mod's own bone order.
"""

import bpy

from ...registry import blender_registry


# idx_anim_map is a u1 in mod 153, 156 and 21x alike, so one group covers all
MTFW_APP_IDS = ("re0", "re1", "re5", "re6", "rev1", "rev2", "dd", "dmc4", "umvc3")

# Where the id lived while re-targeting was experimental. Files saved before
# the move still carry it, so a read falls back to it and moves it over.
LEGACY_ANIM_RETARGET_PROP = "mtfw.anim_retarget"


@blender_registry.register_custom_properties_bone("mod_bone", MTFW_APP_IDS)
@blender_registry.register_blender_prop
class ModBoneCustomProperties(bpy.types.PropertyGroup):
    # A string, not the u1 it is in the file: a second track on the same id
    # gets a bone of its own, retargeted "<id>_<n>". Empty means unmapped.
    anim_retarget: bpy.props.StringProperty(
        name="Anim Retarget",
        description="Animation bone id this bone answers to, from the .mod's idx_anim_map",
        default="",
        options=set(),
    )


def get_bone_custom_properties(pose_bone, app_id):
    """Takes a pose bone (`armature_obj.pose.bones[...]`), where the group lives."""
    return pose_bone.albam_custom_properties.get_custom_properties_for_appid(app_id)


def get_anim_retarget(pose_bone, app_id):
    props = get_bone_custom_properties(pose_bone, app_id)
    if not props.anim_retarget:
        legacy = pose_bone.bone.get(LEGACY_ANIM_RETARGET_PROP)
        if legacy is not None:
            props.anim_retarget = str(legacy)
    return props.anim_retarget


def set_anim_retarget(pose_bone, app_id, value):
    get_bone_custom_properties(pose_bone, app_id).anim_retarget = value
