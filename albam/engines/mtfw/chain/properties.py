"""Blender properties for editable RE5 chain-collision and simulation data."""

import bpy

from ....registry import blender_registry


def _update_ccl_record(self, context):
    # Keep property registration independent from preview construction.
    from .ccl_preview import rebuild_armature_previews

    armature = self.id_data
    if not isinstance(armature, bpy.types.Object) and context is not None:
        armature = getattr(context, "active_object", None)
    if isinstance(armature, bpy.types.Object) and armature.type == "ARMATURE":
        rebuild_armature_previews(armature)


@blender_registry.register_blender_prop
class CCLRecordProperties(bpy.types.PropertyGroup):
    # -1 identifies a record created in Blender rather than loaded from the file.
    record_index: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    ref_joint_no: bpy.props.IntProperty(default=0, options={"HIDDEN"})  # noqa: F821
    preview_object: bpy.props.PointerProperty(
        name="Preview Object", type=bpy.types.Object, options={"HIDDEN"})  # noqa: F821

    attr: bpy.props.StringProperty(name="Attribute", default="1", update=_update_ccl_record)  # noqa: F821
    pair_joint_no: bpy.props.IntProperty(
        name="Tail Joint ID", default=65535, min=0, max=65535, update=_update_ccl_record)
    shape: bpy.props.EnumProperty(
        name="Shape",  # noqa: F821
        items=(
            ("SPHERE", "Sphere", "Sphere centered at Position"),  # noqa: F821
            ("CAPSULE", "Capsule", "Capsule between the reference and tail joints"),  # noqa: F821
            ("AABB", "AABB", "Axis-aligned box"),  # noqa: F821
            ("OBB", "OBB", "Oriented box"),  # noqa: F821
        ),
        default="SPHERE",  # noqa: F821
        update=_update_ccl_record,
    )
    position: bpy.props.FloatVectorProperty(
        name="Position (cm)", size=3, default=(0.0, 0.0, 0.0), update=_update_ccl_record)  # noqa: F821
    id: bpy.props.StringProperty(name="ID", default="0", update=_update_ccl_record)  # noqa: F821
    extent: bpy.props.FloatVectorProperty(
        name="Extent (cm)", size=3, default=(0.0, 0.0, 0.0), update=_update_ccl_record)  # noqa: F821
    radius: bpy.props.FloatProperty(
        name="Radius (cm)", default=1.0, min=0.0, update=_update_ccl_record)  # noqa: F821
    angle: bpy.props.FloatVectorProperty(
        name="Angle (radians)", size=3, default=(0.0, 0.0, 0.0), update=_update_ccl_record)  # noqa: F821


@blender_registry.register_custom_properties_object(
    "physics_ccl_primitive", ("re5",), asset_type="PHYSICS")
@blender_registry.register_blender_prop
class CCLPrimitiveProperties(bpy.types.PropertyGroup):
    """Visible identity link from a generated child mesh to its owning bone record."""

    armature: bpy.props.PointerProperty(
        name="Armature", type=bpy.types.Object, options=set())  # noqa: F821
    reference_bone_name: bpy.props.StringProperty(name="Reference Bone", options=set())
    anim_id: bpy.props.IntProperty(name="Anim ID", default=-1, options=set())
    pair_joint_id: bpy.props.IntProperty(name="Pair Joint ID", default=-1, options={"HIDDEN"})  # noqa: F821
    pair_bone_name: bpy.props.StringProperty(name="Tail Bone", options=set())
    record_index: bpy.props.IntProperty(name="Record Index", default=-1, options=set())
    record_slot: bpy.props.IntProperty(name="Record Slot", default=-1, options={"HIDDEN"})  # noqa: F821
    shape: bpy.props.StringProperty(name="Shape", options=set())  # noqa: F821


def _update_chn_preview(self, context):
    owner = self.id_data
    root_object = _chn_root_from_owner(owner, context)
    if root_object is None or root_object.get("_albam_chn_suppress_update", False):
        return
    from .chn_preview import rebuild_chn_previews

    rebuild_chn_previews(root_object)


def _chn_root_from_owner(owner, context):
    if isinstance(owner, bpy.types.Object):
        if owner.get("_albam_chn_root", False):
            return owner
        if owner.type == "ARMATURE":
            return find_chn_file_for_armature(owner)
    armature = getattr(context, "active_object", None) if context is not None else None
    return find_chn_file_for_armature(armature)


def _update_chn_header_preview(self, context):
    root_object = self.id_data
    if (not isinstance(root_object, bpy.types.Object) or
            root_object.get("_albam_chn_suppress_update", False)):
        return
    from .chn_preview import rebuild_chn_previews

    rebuild_chn_previews(root_object)


def _chn_attr_bit_getter(bit):
    def getter(self):
        try:
            return bool(int(self.attr) & bit)
        except (TypeError, ValueError):
            return False

    return getter


def _chn_attr_bit_setter(bit):
    def setter(self, value):
        try:
            attr = int(self.attr)
        except (TypeError, ValueError):
            attr = 0
        self.attr = str(attr | bit if value else attr & ~bit)

    return setter


@blender_registry.register_blender_prop
class CHNJointProperties(bpy.types.PropertyGroup):
    """One rChain JointInfo stored on its reference PoseBone or as a file orphan."""

    chain_index: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    joint_index: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    source_joint_index: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    source_ref_joint_no: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    raw_node_num: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    raw_node_slots: bpy.props.StringProperty(default="", options={"HIDDEN"})  # noqa: F821
    preview_object: bpy.props.PointerProperty(
        name="Preview Object", type=bpy.types.Object, options={"HIDDEN"})  # noqa: F821
    ref_joint_no: bpy.props.IntProperty(name="Reference Anim ID", default=0, min=0, max=65535,
                                        update=_update_chn_preview)
    # Keep the original mask hidden so unknown bits and older .blend files
    # remain intact; expose the three documented bits as individual toggles.
    attr: bpy.props.StringProperty(default="0", options={"HIDDEN"}, update=_update_chn_preview)  # noqa: F821
    attr_constraint: bpy.props.BoolProperty(
        name="Constraint", description="Pin this joint to its reference bone (bit 1)",  # noqa: F821
        get=_chn_attr_bit_getter(1), set=_chn_attr_bit_setter(1))
    attr_attached: bpy.props.BoolProperty(
        name="Attached", description="Attach this joint to another chain node (bit 2)",  # noqa: F821
        get=_chn_attr_bit_getter(2), set=_chn_attr_bit_setter(2))
    attr_no_rotate: bpy.props.BoolProperty(
        name="No Rotate", description="Disable rotation for this joint (bit 4)",
        get=_chn_attr_bit_getter(4), set=_chn_attr_bit_setter(4))
    min_angle: bpy.props.FloatVectorProperty(
        name="Minimum Angle", size=3, unit="ROTATION",
        description="Per-axis minimum rotation; stored in radians",  # noqa: F821
        default=(-0.055, -0.055, -0.055), update=_update_chn_preview)
    spring_coef: bpy.props.FloatProperty(
        name="Spring Coefficient", default=10.0, update=_update_chn_preview)
    max_angle: bpy.props.FloatVectorProperty(
        name="Maximum Angle", size=3, unit="ROTATION",
        description="Per-axis maximum rotation; stored in radians",  # noqa: F821
        default=(0.055, 0.055, 0.055), update=_update_chn_preview)
    dumping_coef: bpy.props.FloatProperty(
        name="Damping Coefficient", default=0.2, update=_update_chn_preview)
    mass: bpy.props.FloatProperty(name="Mass", default=1.0, update=_update_chn_preview)  # noqa: F821
    restrict_flag: bpy.props.IntProperty(
        name="Restrict Flag", default=0, min=0, max=255, update=_update_chn_preview)
    col_shape: bpy.props.EnumProperty(
        name="Collision Shape",
        items=(
            ("SPHERE", "Sphere", "Spherical collision shape", 1),  # noqa: F821
            ("CAPSULE", "Capsule", "Capsule extending to connected graph neighbors", 2),  # noqa: F821
        ),
        default="SPHERE",  # noqa: F821
        update=_update_chn_preview,
    )
    col_radius: bpy.props.FloatProperty(
        name="Collision Radius (cm)", default=5.0, min=0.0, update=_update_chn_preview)
    air_regist: bpy.props.FloatProperty(
        name="Air Resistance", default=0.1, update=_update_chn_preview)
    friction: bpy.props.FloatProperty(name="Friction", default=0.0, update=_update_chn_preview)  # noqa: F821
    soft_coef: bpy.props.FloatProperty(
        name="Soft Coefficient", default=0.8, update=_update_chn_preview)
    bend_regist: bpy.props.FloatProperty(
        name="Bend Resistance", default=0.0, update=_update_chn_preview)


@blender_registry.register_custom_properties_bone(
    "physics_ccl_bone", ("re5",), asset_type="PHYSICS")
@blender_registry.register_blender_prop
class CCLBoneProperties(bpy.types.PropertyGroup):
    records: bpy.props.CollectionProperty(type=CCLRecordProperties)
    active_record_index: bpy.props.IntProperty(default=0, min=0)
    chn_joints: bpy.props.CollectionProperty(type=CHNJointProperties)
    active_chn_joint_index: bpy.props.IntProperty(default=0, min=0)


@blender_registry.register_blender_prop
class CHNStrandJointProperties(bpy.types.PropertyGroup):
    """A reference to a joint Anim ID in the owning ChainInfo."""

    anim_id: bpy.props.IntProperty(default=0)


@blender_registry.register_blender_prop
class CHNStrandProperties(bpy.types.PropertyGroup):
    """An editable path through joints in one ChainInfo graph."""

    strand_index: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    name: bpy.props.StringProperty(default="")
    closed: bpy.props.BoolProperty(default=False)
    joints: bpy.props.CollectionProperty(type=CHNStrandJointProperties)


@blender_registry.register_blender_prop
class CHNChainProperties(bpy.types.PropertyGroup):
    """Header settings for one CHN chain on its file root."""

    chain_index: bpy.props.IntProperty(default=-1, options={"HIDDEN"})  # noqa: F821
    num_joints: bpy.props.IntProperty(name="Joints", default=0, min=0, max=255)  # noqa: F821
    topology_dirty: bpy.props.BoolProperty(default=False, options={"HIDDEN"})  # noqa: F821
    strands: bpy.props.CollectionProperty(type=CHNStrandProperties)
    active_strand_index: bpy.props.IntProperty(default=0, min=0)
    chain_type: bpy.props.IntProperty(
        name="Chain Info Type (1=chain, 2=shake)", default=1, min=1, max=2,
        update=_update_chn_header_preview)
    grav_scaler: bpy.props.FloatProperty(
        name="Gravity Scale", default=0.0, update=_update_chn_header_preview)
    time_scaler: bpy.props.FloatProperty(
        name="Time Scale", default=0.0, update=_update_chn_header_preview)
    dump_scaler: bpy.props.FloatProperty(
        name="Damping Scale", default=0.0, update=_update_chn_header_preview)


@blender_registry.register_blender_prop
class CHNFileProperties(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(
        name="Armature", type=bpy.types.Object,  # noqa: F821
        description="Skeleton this CHN file is attached to")  # noqa: F821
    total_joints: bpy.props.IntProperty(name="Joints", default=0, min=0)  # noqa: F821
    chain_count: bpy.props.IntProperty(name="Chain Info Entries", default=0, min=0, max=255)
    unresolved_joints: bpy.props.IntProperty(name="Unresolved Bone References", default=0, min=0)
    unresolved_links: bpy.props.IntProperty(name="Unresolved Graph Links", default=0, min=0)
    duplicate_joint_ids: bpy.props.StringProperty(default="", options={"HIDDEN"})  # noqa: F821
    chains: bpy.props.CollectionProperty(type=CHNChainProperties)
    active_chain_index: bpy.props.IntProperty(default=0, min=0)
    show_angle_limits: bpy.props.BoolProperty(
        name="Show Angle Limits",
        description=("Draw per-axis CHN angle limits as colored arcs around each "
                     "reference bone in the 3D View"),
        default=False, update=_update_chn_header_preview)  # noqa: F821
    show_strand_links: bpy.props.BoolProperty(
        name="Show Strand Links",
        description="Draw strand links and direction arrows between reference bones",
        default=False, update=_update_chn_header_preview)  # noqa: F821
    orphans: bpy.props.CollectionProperty(type=CHNJointProperties)
    active_orphan_index: bpy.props.IntProperty(default=0, min=0)


@blender_registry.register_blender_prop
class CCLFileProperties(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(
        name="Armature", type=bpy.types.Object,  # noqa: F821
        description="Skeleton this CCL file is attached to")  # noqa: F821
    record_count: bpy.props.IntProperty(name="Records", default=0, min=0)  # noqa: F821
    unresolved_records: bpy.props.IntProperty(
        name="Records without a matching bone", default=0, min=0, options={"HIDDEN"})  # noqa: F821
    duplicate_joint_ids: bpy.props.StringProperty(default="", options={"HIDDEN"})  # noqa: F821


def get_ccl_bone_properties(pose_bone):
    return pose_bone.albam_custom_properties.get_custom_properties_for_appid(
        "re5", asset_type="PHYSICS")


def get_ccl_file_properties(bl_object):
    return bl_object.albam_ccl_file


def get_chn_file_properties(bl_object):
    return bl_object.albam_chn_file


@blender_registry.register_blender_prop
class CHNJointPreviewProperties(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(name="Armature", type=bpy.types.Object)  # noqa: F821
    reference_bone_name: bpy.props.StringProperty(name="Reference Bone")
    anim_id: bpy.props.IntProperty(name="Anim ID", default=-1)
    chain_index: bpy.props.IntProperty(name="Chain Index", default=-1)
    joint_index: bpy.props.IntProperty(name="Joint Index", default=-1)
    shape: bpy.props.StringProperty(name="Shape")  # noqa: F821


def get_chn_joint_preview_properties(bl_object):
    return bl_object.albam_chn_joint_preview


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


def find_chn_file_for_armature(armature):
    if armature is None:
        return None
    for bl_object in tuple(bpy.data.objects):
        if bl_object.type != "EMPTY" or not bl_object.get("_albam_chn_root", False):
            continue
        file_props = get_chn_file_properties(bl_object)
        if file_props and file_props.armature == armature:
            return bl_object
    return None
