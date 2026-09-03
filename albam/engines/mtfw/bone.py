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

# Where these lived before they became albam custom properties. Files saved
# before the move still carry them, so a read falls back and moves them over.
LEGACY_ANIM_RETARGET_PROP = "mtfw.anim_retarget"
LEGACY_CHAIN_TARGET_PROP = "mtfw.chain_target"
LEGACY_CHAIN_LENGTH_PROP = "mtfw.chain_length"


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
    # A limb is not keyed as a finished pose: the goal it is solved towards
    # rides its own control bone, which is what these mark. Import leaves that
    # bone's position channel unconverted, and export has to do the same.
    chain_target: bpy.props.BoolProperty(
        name="Chain Target",
        description="This bone carries a limb chain's goal rather than a joint's own transform",
        default=False,
        options=set(),
    )
    chain_length: bpy.props.IntProperty(
        name="Chain Length",
        description="Joints the solver owns, plus the target",
        default=0,
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


def get_chain_target(pose_bone, app_id):
    props = get_bone_custom_properties(pose_bone, app_id)
    if not props.chain_target and pose_bone.bone.get(LEGACY_CHAIN_TARGET_PROP):
        props.chain_target = True
    return props.chain_target


def get_chain_length(pose_bone, app_id):
    props = get_bone_custom_properties(pose_bone, app_id)
    if not props.chain_length:
        legacy = pose_bone.bone.get(LEGACY_CHAIN_LENGTH_PROP)
        if legacy is not None:
            props.chain_length = int(legacy)
    return props.chain_length


def set_chain_target(pose_bone, app_id, chain_length):
    props = get_bone_custom_properties(pose_bone, app_id)
    props.chain_target = True
    props.chain_length = chain_length
