"""Import options and bone-property controls for RE5 CCL files."""

import json

import bpy

from ...registry import blender_registry
from .bone import get_anim_retarget
from .chain_preview import rebuild_ccl_preview
from .chain_props import (
    find_ccl_file_for_armature,
    get_ccl_bone_properties,
    get_ccl_file_properties,
    get_ccl_primitive_properties,
)


def _filter_armatures(self, obj):
    return obj is not None and obj.type == "ARMATURE"


@blender_registry.register_blender_prop_albam(name="import_options_chain")
class ImportOptionsChain(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(type=bpy.types.Object, poll=_filter_armatures)


@blender_registry.register_import_options_custom_draw_func(extension="ccl")
def draw_ccl_options(panel_instance, context):
    panel_instance.bl_label = "CCL Options"
    panel_instance.layout.prop(context.scene.albam.import_options_chain, "armature")


@blender_registry.register_import_options_custom_poll_func(extension="ccl")
def poll_ccl_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension="ccl")
def poll_import_operator_for_ccl(panel_class, context):
    return bool(context.scene.albam.import_options_chain.armature)


def _active_pose_bone(context):
    pose_bone = getattr(context, "active_pose_bone", None)
    if pose_bone is not None:
        return pose_bone
    armature = getattr(context, "active_object", None)
    if armature is None or armature.type != "ARMATURE" or armature.mode != "POSE":
        return None
    active_bone = armature.data.bones.active
    return armature.pose.bones.get(active_bone.name) if active_bone else None


def _draw_ccl_bone_editor(layout, pose_bone):
    bl_object = find_ccl_file_for_armature(pose_bone.id_data)
    if bl_object is None:
        return
    file_props = get_ccl_file_properties(bl_object)
    bone_props = get_ccl_bone_properties(pose_bone)
    layout.use_property_split = True
    layout.label(text=bl_object.name, icon="MESH_UVSPHERE")
    if file_props.unresolved_records:
        layout.label(
            text=f"{file_props.unresolved_records} records have no matching bone",
            icon="ERROR")
    if file_props.duplicate_joint_ids:
        layout.label(
            text=f"Duplicate Anim Retarget IDs: {file_props.duplicate_joint_ids}",
            icon="INFO")

    row = layout.row(align=True)
    row.template_list(
        "ALBAM_UL_CCLRecords", "", bone_props, "records",
        bone_props, "active_record_index", rows=3)
    buttons = row.column(align=True)
    buttons.operator("albam.ccl_add_record", icon="ADD", text="")
    buttons.operator("albam.ccl_remove_record", icon="REMOVE", text="")
    layout.operator("albam.ccl_refresh_preview", icon="FILE_REFRESH")

    index = bone_props.active_record_index
    if not 0 <= index < len(bone_props.records):
        return
    record = bone_props.records[index]
    raw_id = get_anim_retarget(pose_bone, "re5")
    layout.separator()
    layout.label(text=f"Reference bone: {pose_bone.name}", icon="BONE_DATA")
    layout.label(text=f"Anim ID: {raw_id or 'unmapped'}")
    if record.preview_object:
        layout.label(text=f"Bound object: {record.preview_object.name}", icon="OBJECT_DATA")
    else:
        layout.label(text="Preview object is not built", icon="ERROR")
    layout.prop(record, "attr")
    layout.prop(record, "shape")
    if record.shape == "CAPSULE":
        layout.prop(record, "pair_joint_no")
    layout.prop(record, "position")
    if record.shape != "SPHERE":
        layout.prop(record, "extent")
    if record.shape in {"SPHERE", "CAPSULE"}:
        layout.prop(record, "radius")
    if record.shape == "OBB":
        layout.prop(record, "angle")
    layout.prop(record, "id")


def _sidebar_target(context):
    pose_bone = _active_pose_bone(context)
    if pose_bone is not None and find_ccl_file_for_armature(pose_bone.id_data):
        return pose_bone.id_data, pose_bone

    active_object = getattr(context, "active_object", None)
    if active_object is None:
        return None, None
    if active_object.type == "ARMATURE":
        return (active_object, None) if find_ccl_file_for_armature(active_object) else (None, None)
    if active_object.type == "EMPTY" and active_object.albam_asset.extension == "ccl":
        file_props = get_ccl_file_properties(active_object)
        if file_props and file_props.armature:
            return file_props.armature, None
    return None, None


@blender_registry.register_blender_type
class ALBAM_UL_CCLRecords(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=f"{item.shape.title()} · record {item.record_index if item.record_index >= 0 else 'new'}")


@blender_registry.register_blender_type
class ALBAM_OT_CCLAddRecord(bpy.types.Operator):
    bl_idname = "albam.ccl_add_record"
    bl_label = "Add CCL Record"

    @classmethod
    def poll(cls, context):
        pose_bone = _active_pose_bone(context)
        if pose_bone is None:
            return False
        if find_ccl_file_for_armature(pose_bone.id_data) is None:
            return False
        return bool(get_anim_retarget(pose_bone, "re5"))

    def execute(self, context):
        pose_bone = _active_pose_bone(context)
        bone_props = get_ccl_bone_properties(pose_bone)
        record = bone_props.records.add()
        record.record_index = -1
        try:
            record.ref_joint_no = int(get_anim_retarget(pose_bone, "re5").split("_", 1)[0])
        except ValueError:
            bone_props.records.remove(len(bone_props.records) - 1)
            self.report({"ERROR"}, "The active bone has an invalid Anim Retarget ID")
            return {"CANCELLED"}
        record.attr = "1"
        record.shape = "SPHERE"
        record.pair_joint_no = 65535
        bone_props.active_record_index = len(bone_props.records) - 1
        bl_object = find_ccl_file_for_armature(pose_bone.id_data)
        rebuild_ccl_preview(bl_object)
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_CCLRemoveRecord(bpy.types.Operator):
    bl_idname = "albam.ccl_remove_record"
    bl_label = "Remove CCL Record"

    @classmethod
    def poll(cls, context):
        pose_bone = _active_pose_bone(context)
        if pose_bone is None:
            return False
        records = get_ccl_bone_properties(pose_bone).records
        index = get_ccl_bone_properties(pose_bone).active_record_index
        return bool(records and 0 <= index < len(records)
                    and find_ccl_file_for_armature(pose_bone.id_data))

    def execute(self, context):
        pose_bone = _active_pose_bone(context)
        bone_props = get_ccl_bone_properties(pose_bone)
        record = bone_props.records[bone_props.active_record_index]
        bl_object = find_ccl_file_for_armature(pose_bone.id_data)
        if record.record_index >= 0:
            try:
                removed = set(json.loads(bl_object.get("_albam_ccl_removed_records", "[]")))
            except (TypeError, ValueError):
                removed = set()
            removed.add(record.record_index)
            bl_object["_albam_ccl_removed_records"] = json.dumps(sorted(removed))
        bone_props.records.remove(bone_props.active_record_index)
        bone_props.active_record_index = min(
            bone_props.active_record_index, max(0, len(bone_props.records) - 1))
        rebuild_ccl_preview(bl_object)
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_CCLRefreshPreview(bpy.types.Operator):
    bl_idname = "albam.ccl_refresh_preview"
    bl_label = "Refresh CCL Preview"

    @classmethod
    def poll(cls, context):
        pose_bone = _active_pose_bone(context)
        return pose_bone is not None and bool(find_ccl_file_for_armature(pose_bone.id_data))

    def execute(self, context):
        pose_bone = _active_pose_bone(context)
        bl_object = find_ccl_file_for_armature(pose_bone.id_data)
        rebuild_ccl_preview(bl_object)
        return {"FINISHED"}

@blender_registry.register_blender_type
class ALBAM_PT_CCLSidebarEditor(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CCLSidebarEditor"
    bl_label = "Chain Collision"
    bl_category = "Albam [Beta]"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        armature, _ = _sidebar_target(context)
        return armature is not None

    def draw(self, context):
        armature, pose_bone = _sidebar_target(context)
        if pose_bone is None:
            self.layout.label(text=f"Select a bone on {armature.name} in Pose Mode")
            return
        _draw_ccl_bone_editor(self.layout, pose_bone)


@blender_registry.register_blender_type
class ALBAM_PT_CCLObjectBindings(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CCLObjectBindings"
    bl_label = "CCL Bone Binding (Albam)"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        bl_object = getattr(context, "object", None)
        if bl_object is None:
            return False
        if bl_object.type == "EMPTY" and bl_object.albam_asset.extension == "ccl":
            return True
        primitive = None
        if bl_object.get("_albam_ccl_preview", False):
            primitive = get_ccl_primitive_properties(bl_object)
        return bool(primitive and primitive.armature)

    def draw(self, context):
        bl_object = context.object
        layout = self.layout
        if bl_object.type == "EMPTY" and bl_object.albam_asset.extension == "ccl":
            file_props = get_ccl_file_properties(bl_object)
            armature_name = file_props.armature.name if file_props.armature else "Missing"
            layout.label(text=f"Armature: {armature_name}", icon="ARMATURE_DATA")
            layout.label(text=f"Records in file: {file_props.record_count}")
            if file_props.unresolved_records:
                layout.label(
                    text=f"Unmatched bone references: {file_props.unresolved_records}",
                    icon="ERROR")
            if file_props.duplicate_joint_ids:
                layout.label(text=f"Duplicate Anim IDs: {file_props.duplicate_joint_ids}",
                             icon="INFO")
            children = sorted(
                (child for child in bl_object.children
                 if child.get("_albam_ccl_preview", False)),
                key=lambda child: child.name,
            )
            if not children:
                layout.label(text="No primitive objects are linked to this CCL file", icon="ERROR")
            for child in children:
                props = get_ccl_primitive_properties(child)
                box = layout.box()
                box.label(text=child.name, icon="MESH_UVSPHERE")
                box.label(
                    text=f"Bone: {props.reference_bone_name}  ·  Anim ID: {props.anim_id}",
                    icon="BONE_DATA")
                if props.shape == "CAPSULE":
                    tail = props.pair_bone_name or f"joint {props.pair_joint_id}"
                    box.label(text=f"Tail bone: {tail}")
            return

        props = get_ccl_primitive_properties(bl_object)
        layout.label(text=f"Bone: {props.reference_bone_name}", icon="BONE_DATA")
        layout.label(text=f"Anim ID: {props.anim_id}")
        layout.label(text=f"Record: {props.record_index if props.record_index >= 0 else 'new'}")
        layout.label(text=f"Shape: {props.shape.title()}")
        if props.shape == "CAPSULE":
            tail = props.pair_bone_name or f"joint {props.pair_joint_id}"
            layout.label(text=f"Tail bone: {tail}")
