"""Blender properties for editable RE5 chain-collision records."""

import bpy

from ...registry import blender_registry


def _update_ccl_record(self, context):
    # Keep property registration independent from preview construction.
    from .chain_preview import rebuild_armature_previews

    armature = self.id_data
    if not isinstance(armature, bpy.types.Object) and context is not None:
        armature = getattr(context, "active_object", None)
    if isinstance(armature, bpy.types.Object) and armature.type == "ARMATURE":
        rebuild_armature_previews(armature)


@blender_registry.register_blender_prop
class CCLRecordProperties(bpy.types.PropertyGroup):
    # -1 identifies a record created in Blender rather than loaded from the file.
    record_index: bpy.props.IntProperty(default=-1, options={"HIDDEN"})
    ref_joint_no: bpy.props.IntProperty(default=0, options={"HIDDEN"})
    preview_object: bpy.props.PointerProperty(
        name="Preview Object", type=bpy.types.Object, options={"HIDDEN"})

    attr: bpy.props.StringProperty(name="Attribute", default="1", update=_update_ccl_record)
    pair_joint_no: bpy.props.IntProperty(
        name="Tail Joint ID", default=65535, min=0, max=65535, update=_update_ccl_record)
    shape: bpy.props.EnumProperty(
        name="Shape",
        items=(
            ("SPHERE", "Sphere", "Sphere centered at Position"),
            ("CAPSULE", "Capsule", "Capsule between the reference and tail joints"),
            ("AABB", "AABB", "Axis-aligned box"),
            ("OBB", "OBB", "Oriented box"),
        ),
        default="SPHERE",
        update=_update_ccl_record,
    )
    position: bpy.props.FloatVectorProperty(
        name="Position (cm)", size=3, default=(0.0, 0.0, 0.0), update=_update_ccl_record)
    id: bpy.props.StringProperty(name="ID", default="0", update=_update_ccl_record)
    extent: bpy.props.FloatVectorProperty(
        name="Extent (cm)", size=3, default=(0.0, 0.0, 0.0), update=_update_ccl_record)
    radius: bpy.props.FloatProperty(
        name="Radius (cm)", default=1.0, min=0.0, update=_update_ccl_record)
    angle: bpy.props.FloatVectorProperty(
        name="Angle (radians)", size=3, default=(0.0, 0.0, 0.0), update=_update_ccl_record)


@blender_registry.register_custom_properties_object(
    "physics_ccl_primitive", ("re5",), asset_type="PHYSICS")
@blender_registry.register_blender_prop
class CCLPrimitiveProperties(bpy.types.PropertyGroup):
    """Visible identity link from a generated child mesh to its owning bone record."""

    armature: bpy.props.PointerProperty(
        name="Armature", type=bpy.types.Object, options=set())
    reference_bone_name: bpy.props.StringProperty(name="Reference Bone", options=set())
    anim_id: bpy.props.IntProperty(name="Anim ID", default=-1, options=set())
    pair_joint_id: bpy.props.IntProperty(name="Pair Joint ID", default=-1, options={"HIDDEN"})
    pair_bone_name: bpy.props.StringProperty(name="Tail Bone", options=set())
    record_index: bpy.props.IntProperty(name="Record Index", default=-1, options=set())
    record_slot: bpy.props.IntProperty(name="Record Slot", default=-1, options={"HIDDEN"})
    shape: bpy.props.StringProperty(name="Shape", options=set())


@blender_registry.register_custom_properties_bone(
    "physics_ccl_bone", ("re5",), asset_type="PHYSICS")
@blender_registry.register_blender_prop
class CCLBoneProperties(bpy.types.PropertyGroup):
    records: bpy.props.CollectionProperty(type=CCLRecordProperties)
    active_record_index: bpy.props.IntProperty(default=0, min=0)


@blender_registry.register_blender_prop
class CCLFileProperties(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(
        name="Armature", type=bpy.types.Object,
        description="Skeleton this CCL file is attached to")
    record_count: bpy.props.IntProperty(name="Records", default=0, min=0)
    unresolved_records: bpy.props.IntProperty(
        name="Records without a matching bone", default=0, min=0, options={"HIDDEN"})
    duplicate_joint_ids: bpy.props.StringProperty(default="", options={"HIDDEN"})


def get_ccl_bone_properties(pose_bone):
    return pose_bone.albam_custom_properties.get_custom_properties_for_appid(
        "re5", asset_type="PHYSICS")


def get_ccl_file_properties(bl_object):
    return bl_object.albam_ccl_file


def get_ccl_primitive_properties(bl_object):
    return bl_object.albam_custom_properties.get_custom_properties_for_appid(
        "re5", asset_type="PHYSICS")


def find_ccl_file_for_armature(armature):
    if armature is None:
        return None
    for bl_object in tuple(bpy.data.objects):
        if bl_object.type != "EMPTY" or bl_object.albam_asset.extension != "ccl":
            continue
        file_props = get_ccl_file_properties(bl_object)
        if file_props and file_props.armature == armature:
            return bl_object
    return None
