"""Import options and bone-property controls for RE5 chain files."""

import json
import math

import bpy

from ....registry import blender_registry
from ..bone import get_anim_retarget
from .ccl_preview import rebuild_ccl_preview
from .graph import decompose_edges, remove_node_from_strands
from .properties import (
    find_ccl_file_for_armature,
    find_chn_file_for_armature,
    get_ccl_bone_properties,
    get_ccl_file_properties,
    get_ccl_primitive_properties,
    get_chn_file_properties,
    get_chn_joint_preview_properties,
)
from .chn_preview import rebuild_chn_previews


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


@blender_registry.register_import_options_custom_draw_func(extension="chn")
def draw_chn_options(panel_instance, context):
    panel_instance.bl_label = "CHN Options"
    panel_instance.layout.prop(context.scene.albam.import_options_chain, "armature")


@blender_registry.register_import_options_custom_poll_func(extension="chn")
def poll_chn_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension="chn")
def poll_import_operator_for_chn(panel_class, context):
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


def _pose_bone_for_anim_id(armature, anim_id):
    "Get bone name by Anim ID"
    if armature is None or armature.type != "ARMATURE":
        return None
    for pose_bone in sorted(armature.pose.bones, key=lambda bone: bone.name):
        raw_id = get_anim_retarget(pose_bone, "re5")
        if not raw_id:
            continue
        try:
            bone_anim_id = int(raw_id.split("_", 1)[0])
        except ValueError:
            continue
        if bone_anim_id == anim_id:
            return pose_bone
    return None


def _sync_preview_bone_name(preview_object, primitive_props):
    armature = primitive_props.armature
    if armature is None or armature.type != "ARMATURE":
        return primitive_props.reference_bone_name

    for pose_bone in armature.pose.bones:
        bone_props = get_ccl_bone_properties(pose_bone)
        if any(record.preview_object == preview_object for record in bone_props.records):
            if primitive_props.reference_bone_name != pose_bone.name:
                primitive_props.reference_bone_name = pose_bone.name
                preview_object["albam_ccl_bone_name"] = pose_bone.name
            return pose_bone.name
    return primitive_props.reference_bone_name


def _sync_chn_preview_bone_name(preview_object, preview_props):
    armature = preview_props.armature
    if armature is None or armature.type != "ARMATURE":
        return preview_props.reference_bone_name
    for pose_bone in armature.pose.bones:
        if any(record.preview_object == preview_object
               for record in get_ccl_bone_properties(pose_bone).chn_joints):
            preview_props.reference_bone_name = pose_bone.name
            return pose_bone.name
    return preview_props.reference_bone_name


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
        row = layout.row(align=True)
        row.prop(record, "pair_joint_no")
        tail_bone = _pose_bone_for_anim_id(file_props.armature, record.pair_joint_no)
        if tail_bone is None:
            row.label(text="Bone not found", icon="ERROR")
        else:
            row.label(text=tail_bone.name)
    layout.prop(record, "position")
    if record.shape != "SPHERE":
        layout.prop(record, "extent")
    if record.shape in {"SPHERE", "CAPSULE"}:
        layout.prop(record, "radius")
    if record.shape == "OBB":
        layout.prop(record, "angle")
    layout.prop(record, "id")


def _draw_chn_joint_fields(layout, record, show_reference_id=True):
    if show_reference_id:
        layout.prop(record, "ref_joint_no")
    layout.prop(record, "attr_constraint")
    layout.prop(record, "attr_attached")
    layout.prop(record, "attr_no_rotate")
    layout.separator()
    layout.prop(record, "min_angle")
    layout.prop(record, "spring_coef")
    layout.prop(record, "max_angle")
    layout.prop(record, "dumping_coef")
    layout.prop(record, "mass")
    layout.prop(record, "restrict_flag")
    layout.prop(record, "col_shape")
    layout.prop(record, "col_radius")
    layout.prop(record, "air_regist")
    layout.prop(record, "friction")
    layout.prop(record, "soft_coef")
    layout.prop(record, "bend_regist")


CHN_JOINT_COPY_FIELDS = (
    "attr",
    "min_angle",
    "spring_coef",
    "max_angle",
    "dumping_coef",
    "mass",
    "restrict_flag",
    "col_shape",
    "col_radius",
    "air_regist",
    "friction",
    "soft_coef",
    "bend_regist",
)
CHN_JOINT_COPY_VECTOR_FIELDS = {"min_angle", "max_angle"}
CHN_JOINT_CLIPBOARD_KEY = "_albam_chn_joint_settings"


def _copy_chn_joint_settings(record):
    settings = {}
    for field in CHN_JOINT_COPY_FIELDS:
        value = getattr(record, field)
        settings[field] = list(value) if field in CHN_JOINT_COPY_VECTOR_FIELDS else value
    return settings


def _paste_chn_joint_settings(record, settings):
    if not isinstance(settings, dict):
        raise ValueError("Clipboard CHN joint settings are invalid")
    missing_fields = set(CHN_JOINT_COPY_FIELDS) - settings.keys()
    if missing_fields:
        raise ValueError(f"CHN settings are missing fields: {', '.join(sorted(missing_fields))}")

    values = {}
    for field in CHN_JOINT_COPY_FIELDS:
        value = settings[field]
        if field in CHN_JOINT_COPY_VECTOR_FIELDS:
            if (not isinstance(value, (list, tuple)) or len(value) != 3 or
                    any(not _is_finite_number(component) for component in value)):
                raise ValueError(f"CHN setting {field} must have three values")
            value = tuple(value)
        elif field == "attr":
            if not isinstance(value, str):
                raise ValueError("CHN setting attr must be a string")
        elif field == "col_shape":
            if not isinstance(value, str) or value not in {"SPHERE", "CAPSULE"}:
                raise ValueError("CHN setting col_shape is invalid")
        elif field == "restrict_flag":
            if (not isinstance(value, int) or isinstance(value, bool) or
                    not 0 <= value <= 255):
                raise ValueError("CHN setting restrict_flag must be between 0 and 255")
        elif not _is_finite_number(value) or (field == "col_radius" and value < 0):
            raise ValueError(f"CHN setting {field} must be a valid number")
        values[field] = value

    for field, value in values.items():
        setattr(record, field, value)


def _is_finite_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool) and
            math.isfinite(value))


def _active_chn_bone_record(context):
    pose_bone = _active_pose_bone(context)
    if pose_bone is None or find_chn_file_for_armature(pose_bone.id_data) is None:
        return None
    bone_props = get_ccl_bone_properties(pose_bone)
    index = bone_props.active_chn_joint_index
    if not 0 <= index < len(bone_props.chn_joints):
        return None
    return pose_bone, bone_props.chn_joints[index]


@blender_registry.register_blender_type
class ALBAM_OT_CHNCopyJointSettings(bpy.types.Operator):
    bl_idname = "albam.chn_copy_joint_settings"
    bl_label = "Copy CHN Joint Settings"
    bl_description = "Copy editable settings from the active CHN joint"

    @classmethod
    def poll(cls, context):
        return _active_chn_bone_record(context) is not None

    def execute(self, context):
        active = _active_chn_bone_record(context)
        if active is None:
            self.report({"ERROR"}, "No active CHN joint on the selected bone")
            return {"CANCELLED"}
        _, record = active
        context.scene.albam.clipboard.update_buffer({
            CHN_JOINT_CLIPBOARD_KEY: {
                "version": 1,
                "settings": _copy_chn_joint_settings(record),
            }
        })
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_CHNPasteJointSettings(bpy.types.Operator):
    bl_idname = "albam.chn_paste_joint_settings"
    bl_label = "Paste CHN Joint Settings"
    bl_description = "Paste settings into the active CHN joint, preserving its identity"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return _active_chn_bone_record(context) is not None

    def execute(self, context):
        active = _active_chn_bone_record(context)
        if active is None:
            self.report({"ERROR"}, "No active CHN joint on the selected bone")
            return {"CANCELLED"}

        payload = context.scene.albam.clipboard.get_buffer().get(CHN_JOINT_CLIPBOARD_KEY)
        if not isinstance(payload, dict) or payload.get("version") != 1:
            self.report({"ERROR"}, "Clipboard does not contain copied CHN joint settings")
            return {"CANCELLED"}
        settings = payload.get("settings")
        if not isinstance(settings, dict):
            self.report({"ERROR"}, "Clipboard CHN joint settings are invalid")
            return {"CANCELLED"}

        pose_bone, record = active
        root_object = find_chn_file_for_armature(pose_bone.id_data)
        was_suppressed = root_object.get("_albam_chn_suppress_update", False)
        root_object["_albam_chn_suppress_update"] = True
        try:
            _paste_chn_joint_settings(record, settings)
        except ValueError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        finally:
            root_object["_albam_chn_suppress_update"] = was_suppressed

        if not was_suppressed:
            rebuild_chn_previews(root_object)
        return {"FINISHED"}


def _draw_chn_bone_editor(layout, pose_bone):
    root_object = find_chn_file_for_armature(pose_bone.id_data)
    if root_object is None:
        return
    bone_props = get_ccl_bone_properties(pose_bone)
    layout.use_property_split = True
    layout.label(text=root_object.name, icon="PHYSICS")

    row = layout.row(align=True)
    row.template_list(
        "ALBAM_UL_CHNJointItems", "", bone_props, "chn_joints",
        bone_props, "active_chn_joint_index", rows=3)
    buttons = row.column(align=True)
    buttons.operator("albam.chn_remove_joint", icon="REMOVE", text="")
    buttons.separator()
    buttons.operator("albam.chn_copy_joint_settings", icon="COPYDOWN", text="")
    buttons.operator("albam.chn_paste_joint_settings", icon="PASTEDOWN", text="")
    layout.operator(
        "albam.chn_add_strand_from_selection", icon="ADD",
        text="Create New Strand from Selected Bones")
    layout.operator(
        "albam.chn_link_bones_to_strand", icon="CON_TRACKTO",
        text="Link Selected Bones to Existing Strand")

    index = bone_props.active_chn_joint_index
    if not 0 <= index < len(bone_props.chn_joints):
        return
    record = bone_props.chn_joints[index]
    layout.separator()
    layout.label(text=f"Bone Name: {pose_bone.name}", icon="BONE_DATA")
    raw_anim_id = get_anim_retarget(pose_bone, "re5")
    layout.label(text=f"Anim ID: {raw_anim_id or 'unmapped'}")
    layout.label(text=f"Chain Info {record.chain_index} · Joint {record.joint_index}")
    if record.preview_object:
        layout.label(text=f"Preview: {record.preview_object.name}", icon="OBJECT_DATA")
    _draw_chn_joint_fields(layout, record, show_reference_id=False)


@blender_registry.register_blender_type
class ALBAM_UL_CCLRecords(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(
            text=f"{item.shape.title()} · record {item.record_index if item.record_index >= 0 else 'new'}")


# List in pose bone panel
@blender_registry.register_blender_type
class ALBAM_UL_CHNJointItems(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        owner = getattr(data, "id_data", None)
        owner_is_file = getattr(owner, "type", None) == "EMPTY"
        label = f"Chain Info {item.chain_index}"
        if owner_is_file:
            label += f" · Anim {item.ref_joint_no}"
        strand_names = _chn_strand_names_for_joint(owner, item)
        label += f" → {', '.join(strand_names) if strand_names else 'Unassigned'}"
        label += f" → Joint {item.joint_index}"
        layout.label(
            text=label, icon="BONE_DATA")


@blender_registry.register_blender_type
class ALBAM_UL_CHNChains(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        chain_type = {1: "Chain", 2: "Shake"}.get(item.chain_type, f"Type {item.chain_type}")
        layout.label(
            text=f"Chain Info {index} · Type: {chain_type} · {item.num_joints} joints",
            icon="PHYSICS")


@blender_registry.register_blender_type
class ALBAM_UL_CHNStrands(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ids = [joint.anim_id for joint in item.joints]
        summary = " → ".join(str(anim_id) for anim_id in ids[:5])
        if len(ids) > 5:
            summary += " → …"
        if item.closed:
            summary += " · closed"
        name = item.name or f"Strand {index + 1}"
        layout.label(text=f"{name} · {summary or 'empty'}", icon="CON_TRACKTO")


def _chn_strand_names_for_joint(owner, joint):
    if getattr(owner, "type", None) == "EMPTY" and owner.get("_albam_chn_root", False):
        root_object = owner
    elif getattr(owner, "type", None) == "ARMATURE":
        root_object = find_chn_file_for_armature(owner)
    else:
        root_object = None
    if root_object is None:
        return []

    file_props = get_chn_file_properties(root_object)
    chain = next((item for item in file_props.chains
                  if item.chain_index == joint.chain_index), None)
    if chain is None:
        return []

    anim_ids = {joint.ref_joint_no}
    if joint.source_ref_joint_no >= 0:
        anim_ids.add(joint.source_ref_joint_no)
    armature = file_props.armature
    if armature is not None and armature.type == "ARMATURE":
        for pose_bone in armature.pose.bones:
            if not any(record.chain_index == joint.chain_index and
                       record.joint_index == joint.joint_index
                       for record in get_ccl_bone_properties(pose_bone).chn_joints):
                continue
            raw_id = get_anim_retarget(pose_bone, "re5")
            if raw_id:
                try:
                    anim_ids.add(int(raw_id.split("_", 1)[0]))
                except ValueError:
                    pass
            break

    return [
        strand.name or f"Strand {index + 1}"
        for index, strand in enumerate(chain.strands)
        if any(item.anim_id in anim_ids for item in strand.joints)
    ]


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
        return bool(records and 0 <= index < len(records) and
                    find_ccl_file_for_armature(pose_bone.id_data))

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


def _chn_records_for_chain(root_object, chain_index):
    file_props = get_chn_file_properties(root_object)
    armature = file_props.armature
    records = []
    if armature is not None:
        for pose_bone in armature.pose.bones:
            records.extend(
                (record, pose_bone)
                for record in get_ccl_bone_properties(pose_bone).chn_joints
                if record.chain_index == chain_index
            )
    records.extend((record, None) for record in file_props.orphans
                   if record.chain_index == chain_index)
    return records


def _replace_chn_strands(chain_props, strand_data):
    chain_props.strands.clear()
    for strand_index, data in enumerate(strand_data):
        strand = chain_props.strands.add()
        strand.strand_index = strand_index
        strand.closed = bool(data.get("closed", False))
        strand.name = data.get("name") or f"Strand {strand_index + 1}"
        for anim_id in data.get("joints", ()):
            strand.joints.add().anim_id = anim_id
    chain_props.active_strand_index = min(
        chain_props.active_strand_index, max(0, len(chain_props.strands) - 1))


def _append_chn_strand(chain_props, anim_ids, closed=False, name=None):
    strand = chain_props.strands.add()
    strand.strand_index = len(chain_props.strands) - 1
    strand.name = name or f"Strand {strand.strand_index + 1}"
    strand.closed = closed
    for anim_id in anim_ids:
        strand.joints.add().anim_id = anim_id
    chain_props.active_strand_index = strand.strand_index
    return strand


def _remove_chn_joint_from_strands(chain_props, anim_id):
    current = [
        {"joints": [joint.anim_id for joint in strand.joints], "closed": strand.closed,
         "name": strand.name}
        for strand in chain_props.strands
    ]
    updated = remove_node_from_strands(current, anim_id)
    _replace_chn_strands(chain_props, updated)
    chain_props.topology_dirty = True


def _strand_ids_for_removed_joint(record, pose_bone, chain_records):
    source_id = (record.source_ref_joint_no
                 if record.source_ref_joint_no >= 0 else record.ref_joint_no)
    source_ids = {
        item.source_ref_joint_no if item.source_ref_joint_no >= 0 else item.ref_joint_no
        for item, _bone in chain_records
    }
    ids = {source_id}
    candidates = [record.ref_joint_no]
    anim_id = _chn_anim_id(pose_bone) if pose_bone is not None else None
    if anim_id is not None:
        candidates.append(anim_id)
    ids.update(candidate for candidate in candidates
               if candidate == source_id or candidate not in source_ids)
    return ids


def _rebuild_chn_strands_from_raw(chain_props, records):
    if not records:
        return False
    anim_ids = [record.ref_joint_no for record, _pose_bone in records]
    if len(anim_ids) != len(set(anim_ids)):
        return False
    known = set(anim_ids)
    edges = []
    for record, _pose_bone in records:
        try:
            slots = bytes.fromhex(record.raw_node_slots)
        except ValueError:
            slots = b""
        if len(slots) != 8 or not 0 <= record.raw_node_num <= 8:
            return False
        edges.extend(
            (record.ref_joint_no, target)
            for target in slots[:record.raw_node_num]
            if target in known and target != record.ref_joint_no
        )
    _replace_chn_strands(chain_props, decompose_edges(anim_ids, edges))
    chain_props.topology_dirty = False
    return True


def _autofill_chn_strands_from_hierarchy(chain_props, records):
    id_by_bone = {}
    anim_ids = []
    for record, pose_bone in records:
        anim_id = _chn_anim_id(pose_bone) if pose_bone is not None else record.ref_joint_no
        if anim_id is None:
            continue
        anim_ids.append(anim_id)
        if pose_bone is not None:
            id_by_bone[pose_bone.name] = anim_id
    if len(anim_ids) != len(set(anim_ids)):
        return False
    edges = []
    for record, pose_bone in records:
        if pose_bone is None or pose_bone.parent is None:
            continue
        parent_id = id_by_bone.get(pose_bone.parent.name)
        child_id = id_by_bone.get(pose_bone.name)
        if parent_id is not None and child_id is not None:
            edges.append((parent_id, child_id))
    _replace_chn_strands(chain_props, decompose_edges(anim_ids, edges))
    chain_props.topology_dirty = True
    return True


def _chn_chain_enum_items(self, context):
    pose_bone = _active_pose_bone(context)
    root_object = find_chn_file_for_armature(pose_bone.id_data) if pose_bone else None
    if root_object is None:
        return [("0", "No CHN file", "Import a CHN file onto this skeleton first")]
    file_props = get_chn_file_properties(root_object)
    return [
        (str(chain.chain_index), f"Chain Info {chain.chain_index}",
         f"Add or link joints in Chain Info {chain.chain_index}")
        for chain in file_props.chains
    ] or [("0", "No Chain Info entries", "The imported CHN file has no Chain Info entries")]


CHN_NEW_CHAIN_INFO_OPTION = "__NEW_CHAIN_INFO__"


def _chn_chain_enum_items_with_new(self, context):
    items = _chn_chain_enum_items(self, context)
    if items and items[0][2] == "Import a CHN file onto this skeleton first":
        return items
    items = [item for item in items if item[1] != "No Chain Info entries"]
    items.append((CHN_NEW_CHAIN_INFO_OPTION, "New Chain Info",
                  "Create a new Chain Info entry for this strand"))
    return items


def _chn_chain_enum_items_with_strands(self, context):
    pose_bone = _active_pose_bone(context)
    root_object = find_chn_file_for_armature(pose_bone.id_data) if pose_bone else None
    if root_object is None:
        return [("0", "No CHN file", "Import a CHN file onto this skeleton first")]
    file_props = get_chn_file_properties(root_object)
    return [
        (str(chain.chain_index), f"Chain Info {chain.chain_index}",
         f"Choose a strand from Chain Info {chain.chain_index}")
        for chain in file_props.chains if chain.strands
    ] or [("0", "No strands", "Create a strand before linking bones to it")]


def _chn_strand_enum_items(self, context):
    pose_bone = _active_pose_bone(context)
    root_object = find_chn_file_for_armature(pose_bone.id_data) if pose_bone else None
    if root_object is None:
        return [("0", "No CHN file", "Import a CHN file onto this skeleton first")]
    try:
        chain_index = int(self.chain_index)
    except (TypeError, ValueError):
        return [("0", "Choose a Chain Info", "Select a Chain Info entry first")]
    chain = next((item for item in get_chn_file_properties(root_object).chains
                  if item.chain_index == chain_index), None)
    if chain is None or not chain.strands:
        return [("0", "No strands", "Choose a Chain Info that contains a strand")]
    return [
        (str(index), strand.name or f"Strand {index + 1}",
         f"{len(strand.joints)} joints")
        for index, strand in enumerate(chain.strands)
    ]


def _chn_anim_id(pose_bone):
    raw_id = get_anim_retarget(pose_bone, "re5")
    if not raw_id:
        return None
    try:
        return int(raw_id.split("_", 1)[0])
    except ValueError:
        return None


def _active_chn_chain(root_object):
    file_props = get_chn_file_properties(root_object)
    if not 0 <= file_props.active_chain_index < len(file_props.chains):
        return None
    return file_props.chains[file_props.active_chain_index]


@blender_registry.register_blender_type
class ALBAM_OT_CHNRebuildStrands(bpy.types.Operator):
    bl_idname = "albam.chn_rebuild_strands"
    bl_label = "Rebuild Strands from Raw Links"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        root = getattr(context, "object", None)
        return bool(root and root.get("_albam_chn_root", False) and _active_chn_chain(root))

    def execute(self, context):
        root = context.object
        chain = _active_chn_chain(root)
        if not _rebuild_chn_strands_from_raw(
                chain, _chn_records_for_chain(root, chain.chain_index)):
            self.report({"ERROR"}, "Raw node slots are missing or Anim IDs are duplicated")
            return {"CANCELLED"}
        rebuild_chn_previews(root)
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_CHNAutoFillLinks(bpy.types.Operator):
    bl_idname = "albam.chn_autofill_links"
    bl_label = "Auto-fill Strands from Bone Hierarchy"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        root = getattr(context, "object", None)
        return bool(root and root.get("_albam_chn_root", False) and _active_chn_chain(root))

    def execute(self, context):
        root = context.object
        chain = _active_chn_chain(root)
        if not _autofill_chn_strands_from_hierarchy(
                chain, _chn_records_for_chain(root, chain.chain_index)):
            self.report({"ERROR"}, "Duplicate Anim IDs prevent an unambiguous graph")
            return {"CANCELLED"}
        rebuild_chn_previews(root)
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_CHNRemoveStrand(bpy.types.Operator):
    bl_idname = "albam.chn_remove_strand"
    bl_label = "Remove Strand"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        root = getattr(context, "object", None)
        chain = _active_chn_chain(root) if root and root.get("_albam_chn_root", False) else None
        return bool(chain and 0 <= chain.active_strand_index < len(chain.strands))

    def execute(self, context):
        root = context.object
        chain = _active_chn_chain(root)
        chain.strands.remove(chain.active_strand_index)
        for index, strand in enumerate(chain.strands):
            strand.strand_index = index
        chain.active_strand_index = min(
            chain.active_strand_index, max(0, len(chain.strands) - 1))
        chain.topology_dirty = True
        rebuild_chn_previews(root)
        return {"FINISHED"}


def _selected_bone_path(context, active_bone):
    selected = list(getattr(context, "selected_pose_bones", ()) or (active_bone,))
    if active_bone not in selected:
        selected.append(active_bone)
    selected_names = {bone.name for bone in selected}
    children = {bone.name: [] for bone in selected}
    roots = []
    for bone in selected:
        if bone.parent is not None and bone.parent.name in selected_names:
            children[bone.parent.name].append(bone)
        else:
            roots.append(bone)
    if len(roots) != 1:
        return None
    ordered = []
    current = roots[0]
    while current is not None:
        ordered.append(current)
        descendants = children[current.name]
        if len(descendants) > 1:
            return None
        current = descendants[0] if descendants else None
    return ordered if len(ordered) == len(selected) else None


def _create_chn_joint_for_bone(pose_bone, chain_index, anim_id):
    bone_props = get_ccl_bone_properties(pose_bone)
    joint = bone_props.chn_joints.add()
    joint.chain_index = chain_index
    joint.joint_index = -1
    joint.source_joint_index = -1
    joint.source_ref_joint_no = anim_id
    joint.ref_joint_no = anim_id
    joint.attr = "0"
    bone_props.active_chn_joint_index = len(bone_props.chn_joints) - 1
    return joint


@blender_registry.register_blender_type
class ALBAM_OT_CHNAddStrandFromSelection(bpy.types.Operator):
    bl_idname = "albam.chn_add_strand_from_selection"
    bl_label = "Create New Strand from Selected Bones"
    bl_options = {"UNDO"}

    chain_index: bpy.props.EnumProperty(
        name="Target Chain Info", items=_chn_chain_enum_items_with_new)

    @classmethod
    def poll(cls, context):
        pose_bone = _active_pose_bone(context)
        return bool(pose_bone and find_chn_file_for_armature(pose_bone.id_data))

    def invoke(self, context, event):
        pose_bone = _active_pose_bone(context)
        root = find_chn_file_for_armature(pose_bone.id_data)
        if root:
            file_props = get_chn_file_properties(root)
            if file_props.chains:
                selected = min(file_props.active_chain_index, len(file_props.chains) - 1)
                self.chain_index = str(file_props.chains[selected].chain_index)
            else:
                self.chain_index = CHN_NEW_CHAIN_INFO_OPTION
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        self.layout.prop(self, "chain_index")

    def execute(self, context):
        active_bone = _active_pose_bone(context)
        root = find_chn_file_for_armature(active_bone.id_data)
        path = _selected_bone_path(context, active_bone)
        if path is None:
            self.report({"ERROR"}, "Select one unbranched parent-to-child bone path")
            return {"CANCELLED"}
        file_props = get_chn_file_properties(root)
        create_new_chain = self.chain_index == CHN_NEW_CHAIN_INFO_OPTION
        if create_new_chain:
            chain_index = len(file_props.chains)
            if chain_index >= 0xFF:
                self.report({"ERROR"}, "A CHN file cannot contain more than 255 Chain Info entries")
                return {"CANCELLED"}
            chain = None
        else:
            try:
                chain_index = int(self.chain_index)
            except ValueError:
                chain_index = -1
            chain = next((item for item in file_props.chains
                          if item.chain_index == chain_index), None)
        if not create_new_chain and chain is None:
            self.report({"ERROR"}, "Choose an existing Chain Info entry or New Chain Info")
            return {"CANCELLED"}

        anim_ids = [_chn_anim_id(bone) for bone in path]
        if any(anim_id is None or not 0 <= anim_id <= 0xFFFF for anim_id in anim_ids):
            self.report({"ERROR"}, "Every selected bone needs a numeric Anim Retarget ID")
            return {"CANCELLED"}
        if len(anim_ids) != len(set(anim_ids)):
            self.report({"ERROR"}, "Selected bones have duplicate Anim IDs")
            return {"CANCELLED"}

        chain_records = _chn_records_for_chain(root, chain_index)
        known_ids = {
            _chn_anim_id(bone) if bone is not None else record.ref_joint_no
            for record, bone in chain_records
        }
        if len(known_ids) != len(chain_records):
            self.report({"ERROR"}, "The Chain Info already contains duplicate Anim IDs")
            return {"CANCELLED"}
        current_joint_count = chain.num_joints if chain is not None else 0
        if current_joint_count + sum(anim_id not in known_ids for anim_id in anim_ids) > 0xFF:
            self.report({"ERROR"}, "A Chain Info entry cannot contain more than 255 joints")
            return {"CANCELLED"}

        root["_albam_chn_suppress_update"] = True
        if create_new_chain:
            chain = file_props.chains.add()
            chain.chain_index = chain_index
            chain.topology_dirty = True
            file_props.chain_count = len(file_props.chains)
            file_props.active_chain_index = chain_index
        for position, (bone, anim_id) in enumerate(zip(path, anim_ids)):
            existing = next((record for record in get_ccl_bone_properties(bone).chn_joints
                             if record.chain_index == chain_index), None)
            if existing is None:
                existing = _create_chn_joint_for_bone(bone, chain_index, anim_id)
                existing.joint_index = chain.num_joints
                chain.num_joints += 1
                file_props.total_joints += 1
            existing.attr_constraint = position == 0
            existing.attr_attached = position != 0
        _append_chn_strand(chain, anim_ids)
        chain.topology_dirty = True
        file_props.active_chain_index = chain_index
        root["_albam_chn_suppress_update"] = False
        rebuild_chn_previews(root)
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_CHNLinkBonesToStrand(bpy.types.Operator):
    bl_idname = "albam.chn_link_bones_to_strand"
    bl_label = "Link Selected Bones to Existing Strand"
    bl_options = {"UNDO"}

    chain_index: bpy.props.EnumProperty(
        name="Target Chain Info", items=_chn_chain_enum_items_with_strands)
    strand_index: bpy.props.EnumProperty(
        name="Target Strand", items=_chn_strand_enum_items)

    @classmethod
    def poll(cls, context):
        pose_bone = _active_pose_bone(context)
        if pose_bone is None:
            return False
        root_object = find_chn_file_for_armature(pose_bone.id_data)
        file_props = get_chn_file_properties(root_object) if root_object else None
        return bool(file_props and any(chain.strands for chain in file_props.chains))

    def invoke(self, context, event):
        pose_bone = _active_pose_bone(context)
        root_object = find_chn_file_for_armature(pose_bone.id_data)
        file_props = get_chn_file_properties(root_object)
        chain = next((item for item in file_props.chains
                      if item.chain_index == file_props.active_chain_index and item.strands), None)
        if chain is None:
            chain = next(item for item in file_props.chains if item.strands)
        self.chain_index = str(chain.chain_index)
        self.strand_index = str(min(chain.active_strand_index, len(chain.strands) - 1))
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        self.layout.prop(self, "chain_index")
        self.layout.prop(self, "strand_index")

    def execute(self, context):
        active_bone = _active_pose_bone(context)
        root_object = find_chn_file_for_armature(active_bone.id_data)
        path = _selected_bone_path(context, active_bone)
        if path is None:
            self.report({"ERROR"}, "Select one unbranched parent-to-child bone path")
            return {"CANCELLED"}

        file_props = get_chn_file_properties(root_object)
        try:
            chain_index = int(self.chain_index)
            strand_index = int(self.strand_index)
        except (TypeError, ValueError):
            self.report({"ERROR"}, "Choose both a Chain Info and a strand")
            return {"CANCELLED"}
        chain = next((item for item in file_props.chains
                      if item.chain_index == chain_index), None)
        if chain is None or not 0 <= strand_index < len(chain.strands):
            self.report({"ERROR"}, "Choose an existing Chain Info and strand")
            return {"CANCELLED"}
        strand = chain.strands[strand_index]

        anim_ids = [_chn_anim_id(bone) for bone in path]
        if any(anim_id is None or not 0 <= anim_id <= 0xFFFF for anim_id in anim_ids):
            self.report({"ERROR"}, "Every selected bone needs a numeric Anim Retarget ID")
            return {"CANCELLED"}
        if len(anim_ids) != len(set(anim_ids)):
            self.report({"ERROR"}, "Selected bones have duplicate Anim IDs")
            return {"CANCELLED"}

        chain_records = _chn_records_for_chain(root_object, chain_index)
        current_ids = []
        for record, bone in chain_records:
            current_id = _chn_anim_id(bone) if bone is not None else None
            current_ids.append(record.ref_joint_no if current_id is None else current_id)
        if len(current_ids) != len(set(current_ids)):
            self.report({"ERROR"}, "The Chain Info already contains duplicate Anim IDs")
            return {"CANCELLED"}
        known_ids = set(current_ids)
        if chain.num_joints + sum(anim_id not in known_ids for anim_id in anim_ids) > 0xFF:
            self.report({"ERROR"}, "A Chain Info entry cannot contain more than 255 joints")
            return {"CANCELLED"}

        id_remap = {}
        for record, pose_bone in chain_records:
            current_id = _chn_anim_id(pose_bone) if pose_bone is not None else None
            if current_id is None:
                current_id = record.ref_joint_no
            source_id = (record.source_ref_joint_no
                         if record.source_ref_joint_no >= 0 else record.ref_joint_no)
            id_remap[source_id] = current_id
        strand_ids = [id_remap.get(joint.anim_id, joint.anim_id) for joint in strand.joints]
        overlap = 0
        for count in range(min(len(strand_ids), len(anim_ids)), 0, -1):
            if strand_ids[-count:] == anim_ids[:count]:
                overlap = count
                break
        if set(strand_ids).intersection(anim_ids) and overlap == 0:
            self.report(
                {"ERROR"},
                "The selected path overlaps this strand; start from its last bone",
            )
            return {"CANCELLED"}
        ids_to_link = anim_ids[overlap:]
        if not ids_to_link:
            self.report({"INFO"}, "The selected bones are already at the end of this strand")
            return {"CANCELLED"}

        was_suppressed = root_object.get("_albam_chn_suppress_update", False)
        root_object["_albam_chn_suppress_update"] = True
        try:
            for path_index in range(overlap, len(path)):
                bone = path[path_index]
                anim_id = anim_ids[path_index]
                existing = next((record for record in get_ccl_bone_properties(bone).chn_joints
                                 if record.chain_index == chain_index), None)
                if existing is None:
                    existing = _create_chn_joint_for_bone(bone, chain_index, anim_id)
                    existing.joint_index = chain.num_joints
                    chain.num_joints += 1
                    file_props.total_joints += 1
                is_first_joint = not strand_ids and path_index == overlap
                existing.attr_constraint = is_first_joint
                existing.attr_attached = not is_first_joint
                strand.joints.add().anim_id = anim_id
                get_ccl_bone_properties(bone).active_chn_joint_index = next(
                    index for index, record in enumerate(
                        get_ccl_bone_properties(bone).chn_joints)
                    if record.chain_index == chain_index
                )
            chain.topology_dirty = True
            chain.active_strand_index = strand_index
            file_props.active_chain_index = chain_index
        finally:
            root_object["_albam_chn_suppress_update"] = was_suppressed

        if not was_suppressed:
            rebuild_chn_previews(root_object)
        return {"FINISHED"}


def _compact_chn_chain(root_object, chain_index, removed_joint_index):
    file_props = get_chn_file_properties(root_object)
    armature = file_props.armature
    root_object["_albam_chn_suppress_update"] = True
    for pose_bone in armature.pose.bones:
        for record in get_ccl_bone_properties(pose_bone).chn_joints:
            if (record.chain_index == chain_index and record.joint_index > removed_joint_index):
                record.joint_index -= 1
    for record in file_props.orphans:
        if record.chain_index == chain_index and record.joint_index > removed_joint_index:
            record.joint_index -= 1
    chain_props = next(
        chain for chain in file_props.chains if chain.chain_index == chain_index)
    chain_props.num_joints -= 1
    file_props.total_joints -= 1
    root_object["_albam_chn_suppress_update"] = False
    rebuild_chn_previews(root_object)


@blender_registry.register_blender_type
class ALBAM_OT_CHNRemoveJoint(bpy.types.Operator):
    bl_idname = "albam.chn_remove_joint"
    bl_label = "Remove Bone from Chain Info"

    @classmethod
    def poll(cls, context):
        pose_bone = _active_pose_bone(context)
        if pose_bone is None:
            return False
        props = get_ccl_bone_properties(pose_bone)
        return (0 <= props.active_chn_joint_index < len(props.chn_joints) and
                find_chn_file_for_armature(pose_bone.id_data) is not None)

    def execute(self, context):
        pose_bone = _active_pose_bone(context)
        bone_props = get_ccl_bone_properties(pose_bone)
        record = bone_props.chn_joints[bone_props.active_chn_joint_index]
        root_object = find_chn_file_for_armature(pose_bone.id_data)
        chain_index, joint_index = record.chain_index, record.joint_index
        chain_props = next(
            chain for chain in get_chn_file_properties(root_object).chains
            if chain.chain_index == chain_index)
        chain_records = _chn_records_for_chain(root_object, chain_index)
        ids_to_remove = _strand_ids_for_removed_joint(record, pose_bone, chain_records)
        for joint_id in ids_to_remove:
            _remove_chn_joint_from_strands(chain_props, joint_id)
        bone_props.chn_joints.remove(bone_props.active_chn_joint_index)
        bone_props.active_chn_joint_index = min(
            bone_props.active_chn_joint_index, max(0, len(bone_props.chn_joints) - 1))
        _compact_chn_chain(root_object, chain_index, joint_index)
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_CHNRemoveOrphan(bpy.types.Operator):
    bl_idname = "albam.chn_remove_orphan"
    bl_label = "Remove Unmatched CHN Joint"

    @classmethod
    def poll(cls, context):
        root_object = getattr(context, "object", None)
        if root_object is None or not root_object.get("_albam_chn_root", False):
            return False
        file_props = get_chn_file_properties(root_object)
        return 0 <= file_props.active_orphan_index < len(file_props.orphans)

    def execute(self, context):
        root_object = context.object
        file_props = get_chn_file_properties(root_object)
        record = file_props.orphans[file_props.active_orphan_index]
        chain_index, joint_index = record.chain_index, record.joint_index
        chain_props = next(chain for chain in file_props.chains
                           if chain.chain_index == chain_index)
        chain_records = _chn_records_for_chain(root_object, chain_index)
        ids_to_remove = _strand_ids_for_removed_joint(record, None, chain_records)
        for joint_id in ids_to_remove:
            _remove_chn_joint_from_strands(chain_props, joint_id)
        root_object["_albam_chn_suppress_update"] = True
        file_props.orphans.remove(file_props.active_orphan_index)
        file_props.active_orphan_index = min(
            file_props.active_orphan_index, max(0, len(file_props.orphans) - 1))
        root_object["_albam_chn_suppress_update"] = False
        _compact_chn_chain(root_object, chain_index, joint_index)
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
class ALBAM_OT_CHNRefreshPreview(bpy.types.Operator):
    bl_idname = "albam.chn_refresh_preview"
    bl_label = "Refresh CHN Preview"

    @classmethod
    def poll(cls, context):
        bl_object = getattr(context, "object", None)
        if bl_object and bl_object.get("_albam_chn_root", False):
            return True
        return bool(bl_object and bl_object.type == "ARMATURE" and
                    find_chn_file_for_armature(bl_object))

    def execute(self, context):
        bl_object = context.object
        root_object = (bl_object if bl_object.get("_albam_chn_root", False)
                       else find_chn_file_for_armature(bl_object))
        rebuild_chn_previews(root_object)
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_PT_CCLBoneProperties(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CCLBoneProperties"
    bl_label = "Chain Physics (Albam)"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        pose_bone = _active_pose_bone(context)
        return (pose_bone is not None and
                (find_ccl_file_for_armature(pose_bone.id_data) is not None or
                 find_chn_file_for_armature(pose_bone.id_data) is not None))

    def draw(self, context):
        pose_bone = _active_pose_bone(context)
        has_ccl = find_ccl_file_for_armature(pose_bone.id_data) is not None
        has_chn = find_chn_file_for_armature(pose_bone.id_data) is not None
        if has_ccl:
            _draw_ccl_bone_editor(self.layout, pose_bone)
        if has_ccl and has_chn:
            self.layout.separator()
        if has_chn:
            _draw_chn_bone_editor(self.layout, pose_bone)


@blender_registry.register_blender_type
class ALBAM_PT_CCLObjectBindings(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CCLObjectBindings"
    bl_label = "Chain File Settings (Albam)"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        bl_object = getattr(context, "object", None)
        if bl_object is None:
            return False
        if (bl_object.get("_albam_chn_joint_preview", False) or bl_object.get("_albam_chn_root", False)):
            return True
        if (bl_object.type == "EMPTY" and bl_object.albam_asset.extension in {"ccl", "chn"}):
            return True
        primitive = None
        if bl_object.get("_albam_ccl_preview", False):
            primitive = get_ccl_primitive_properties(bl_object)
        return bool(primitive and primitive.armature)

    def draw(self, context):
        bl_object = context.object
        layout = self.layout
        if bl_object.get("_albam_chn_joint_preview", False):
            _draw_chn_joint_preview_binding(layout, bl_object)
            return
        if bl_object.type == "EMPTY" and bl_object.get("_albam_chn_root", False):
            _draw_chn_file_editor(layout, bl_object)
            return
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
                bone_name = _sync_preview_bone_name(child, props)
                box = layout.box()
                box.label(text=child.name, icon="MESH_UVSPHERE")
                box.label(
                    text=f"Bone Name: {bone_name}  ·  Anim ID: {props.anim_id}",
                    icon="BONE_DATA")
                if props.shape == "CAPSULE":
                    tail = props.pair_bone_name or f"joint {props.pair_joint_id}"
                    box.label(text=f"Tail bone: {tail}")
            return

        props = get_ccl_primitive_properties(bl_object)
        bone_name = _sync_preview_bone_name(bl_object, props)
        layout.label(text=f"Bone Name: {bone_name}")
        layout.label(text=f"Anim ID: {props.anim_id}")
        layout.label(text=f"Record: {props.record_index if props.record_index >= 0 else 'new'}")
        layout.label(text=f"Shape: {props.shape.title()}")
        if props.shape == "CAPSULE":
            tail = props.pair_bone_name or f"joint {props.pair_joint_id}"
            layout.label(text=f"Tail bone: {tail}")


def _draw_chn_file_editor(layout, bl_object):
    file_props = get_chn_file_properties(bl_object)
    layout.use_property_split = True
    armature_name = file_props.armature.name if file_props.armature else "Missing"
    layout.label(text=f"Armature: {armature_name}", icon="ARMATURE_DATA")
    layout.label(text=f"Chain Info entries: {file_props.chain_count}")
    layout.label(text=f"Joints in file: {file_props.total_joints}")
    if file_props.unresolved_joints:
        layout.label(
            text=f"Unmatched bone references: {file_props.unresolved_joints}",
            icon="ERROR")
    if file_props.unresolved_links:
        layout.label(
            text=f"Links to joints outside their Chain Info: {file_props.unresolved_links}",
            icon="ERROR")
    if file_props.duplicate_joint_ids:
        layout.label(text=f"Duplicate Anim IDs: {file_props.duplicate_joint_ids}", icon="INFO")
    row = layout.row(align=True)
    row.template_list(
        "ALBAM_UL_CHNChains", "", file_props, "chains",
        file_props, "active_chain_index", rows=4)
    layout.operator("albam.chn_refresh_preview", icon="FILE_REFRESH")
    layout.prop(file_props, "show_angle_limits")
    if file_props.show_angle_limits:
        layout.label(text="Angle axes: X red · Y green · Z blue")
    layout.prop(file_props, "show_strand_links")
    if file_props.show_strand_links:
        layout.label(text="Arrows follow the stored strand order")
        layout.label(text="Strand colors cycle: orange · magenta · yellow")
    chain_index = file_props.active_chain_index
    if 0 <= chain_index < len(file_props.chains):
        chain = file_props.chains[chain_index]
        layout.label(text=f"Chain Info {chain.chain_index} · {chain.num_joints} joints")
        layout.label(text=f"Graph strands: {len(chain.strands)}" +
                     (" · modified" if chain.topology_dirty else " · source links"))
        layout.prop(chain, "chain_type")
        layout.prop(chain, "grav_scaler")
        layout.prop(chain, "time_scaler")
        layout.prop(chain, "dump_scaler")
        layout.template_list(
            "ALBAM_UL_CHNStrands", "", chain, "strands",
            chain, "active_strand_index", rows=4)
        layout.operator("albam.chn_remove_strand", icon="REMOVE", text="Remove Strand")
        row = layout.row(align=True)
        row.operator("albam.chn_rebuild_strands", icon="FILE_REFRESH")
        row.operator("albam.chn_autofill_links", icon="CON_TRACKTO")

    if file_props.orphans:
        layout.separator()
        layout.label(text="Joints without a matching bone", icon="ERROR")
        row = layout.row(align=True)
        row.template_list(
            "ALBAM_UL_CHNJointItems", "orphans", file_props, "orphans",
            file_props, "active_orphan_index", rows=3)
        row.operator("albam.chn_remove_orphan", icon="REMOVE", text="")
        orphan_index = file_props.active_orphan_index
        if 0 <= orphan_index < len(file_props.orphans):
            _draw_chn_joint_fields(layout, file_props.orphans[orphan_index])

    previews = sorted(
        (child for child in bl_object.children
         if child.get("_albam_chn_joint_preview", False)),
        key=lambda child: child.name,
    )
    angle_previews = [
        child for child in bl_object.children
        if child.get("_albam_chn_angle_preview", False)
    ]
    strand_previews = [
        child for child in bl_object.children
        if child.get("_albam_chn_strand_preview", False)
    ]
    if previews:
        layout.separator()
        layout.label(
            text=f"Collision previews: {len(previews)}", icon="MESH_DATA")
    if angle_previews:
        layout.label(
            text=f"Angle limit arcs: {len(angle_previews)}")
    if strand_previews:
        layout.label(text=f"Strand link previews: {len(strand_previews)}")


def _draw_chn_joint_preview_binding(layout, bl_object):
    props = get_chn_joint_preview_properties(bl_object)
    armature_name = props.armature.name if props.armature else "Missing"
    bone_name = _sync_chn_preview_bone_name(bl_object, props)
    layout.label(text=f"Armature: {armature_name}", icon="ARMATURE_DATA")
    layout.label(text=f"Bone Name: {bone_name}", icon="BONE_DATA")
    layout.label(text=f"Anim ID: {props.anim_id}")
    layout.label(text=f"Chain Info: {props.chain_index} · Joint: {props.joint_index}")
    layout.label(text=f"Shape: {props.shape.title()}")
