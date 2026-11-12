"""RE5 chain-collision (.ccl) import and export."""

import json
import math
from io import BytesIO

import bpy
from kaitaistruct import KaitaiStream

from . import chain_props as _chain_props  # register the PropertyGroups
from .bone import get_anim_retarget
from .chain_preview import rebuild_ccl_preview
from .chain_props import (
    find_ccl_file_for_armature,
    get_ccl_bone_properties,
    get_ccl_file_properties,
)
from .structs.ccl_156 import Ccl156
from ...exceptions import AlbamCheckFailure
from ...lib.kaitai_utils import check_recursive, parse
from ...registry import blender_registry
from ...vfs import VirtualFileData


_CCL_MAGIC = b"CCL\x00"
_CCL_VERSION = 0x80618
_CCL_HEADER_SIZE = 16
_CCL_RECORD_SIZE = 64
_SHAPE_TO_INT = {"SPHERE": 0, "CAPSULE": 1, "AABB": 2, "OBB": 3}


def _parse_ccl(data):
    if len(data) < _CCL_HEADER_SIZE:
        raise AlbamCheckFailure(
            "This .ccl file appears to be truncated or corrupted",
            details=f"The file is only {len(data)} bytes long",
            solution="Re-extract the file from the game's archive and try importing it again",
        )
    if data[:4] != _CCL_MAGIC:
        raise AlbamCheckFailure(
            "The selected file is not a supported .ccl resource",
            details=f"Expected CCL magic, found {data[:4]!r}",
            solution="Check that this is a chain-collision file from Resident Evil 5",
        )

    version = int.from_bytes(data[4:8], "little")
    count = int.from_bytes(data[8:12], "little")
    data_size = int.from_bytes(data[12:16], "little")
    expected_data_size = count * _CCL_RECORD_SIZE
    expected_size = _CCL_HEADER_SIZE + expected_data_size
    if version != _CCL_VERSION:
        raise AlbamCheckFailure(
            "This .ccl version is not supported",
            details=f"Found version 0x{version:x}; RE5 CCL version 0x{_CCL_VERSION:x} is supported",
            solution="Use a CCL file from a supported game/version",
        )
    if data_size != expected_data_size or len(data) != expected_size:
        raise AlbamCheckFailure(
            "This .ccl file has an inconsistent size",
            details=(f"Header declares {count} records ({data_size} data bytes), but the file "
                     f"contains {len(data)} bytes; expected {expected_size}"),
            solution="Re-extract the file from the game's archive and try again",
        )
    try:
        return parse(Ccl156, data)
    except Exception as ex:
        raise AlbamCheckFailure(
            "This .ccl file could not be parsed",
            details=f"{type(ex).__name__}: {ex}",
            solution="Check that the file is a valid RE5 chain-collision resource",
        ) from ex


def _joint_id_from_bone(pose_bone):
    raw_id = get_anim_retarget(pose_bone, "re5")
    if not raw_id:
        raise AlbamCheckFailure(
            f"Bone {pose_bone.name!r} has no animation joint ID",
            details="CCL records address bones through the model's Anim Retarget IDs",
            solution="Set an Anim Retarget ID on this bone before exporting its CCL record",
        )
    try:
        joint_id = int(raw_id.split("_", 1)[0])
    except ValueError as ex:
        raise AlbamCheckFailure(
            f"Bone {pose_bone.name!r} has an invalid animation joint ID",
            details=f"Anim Retarget is {raw_id!r}",
            solution="Set Anim Retarget to a numeric bone ID used by the model",
        ) from ex
    if not 0 <= joint_id <= 0xFFFF:
        raise AlbamCheckFailure(
            f"Bone {pose_bone.name!r} has an out-of-range CCL joint ID",
            details=f"Joint ID {joint_id} does not fit the CCL u2 field",
            solution="Set an Anim Retarget ID between 0 and 65535",
        )
    return joint_id


def _bone_map(armature):
    result = {}
    duplicates = set()
    for pose_bone in sorted(armature.pose.bones, key=lambda bone: bone.name):
        raw_id = get_anim_retarget(pose_bone, "re5")
        if not raw_id:
            continue
        try:
            joint_id = int(raw_id.split("_", 1)[0])
        except ValueError:
            continue
        if joint_id in result:
            duplicates.add(joint_id)
            continue
        result[joint_id] = pose_bone
    return result, duplicates


def _load_record(dst, src, record_index):
    dst.record_index = record_index
    dst.ref_joint_no = src.ref_joint_no
    dst.attr = str(src.attr)
    dst.pair_joint_no = src.pair_joint_no
    dst.shape = {
        0: "SPHERE", 1: "CAPSULE", 2: "AABB", 3: "OBB",
    }.get(int(src.shape), "SPHERE")
    dst.position = (src.position.x, src.position.y, src.position.z)
    dst.id = str(src.id)
    dst.extent = (src.extent.x, src.extent.y, src.extent.z)
    dst.radius = src.radius
    dst.angle = (src.angle.x, src.angle.y, src.angle.z)


@blender_registry.register_import_function(
    app_id="re5", extension="ccl", albam_asset_type="PHYSICS")
def load_ccl(vfile, context) -> bpy.types.Object:
    if vfile.app_id != "re5":
        raise AlbamCheckFailure(
            "CCL import is currently supported for Resident Evil 5",
            details=f"The selected app is {vfile.app_id!r}",
            solution="Select Resident Evil 5 and import the corresponding CCL file",
        )
    armature = context.scene.albam.import_options_chain.armature
    if armature is None or armature.type != "ARMATURE":
        raise AlbamCheckFailure(
            "Choose a skeleton before importing this .ccl file",
            details="CCL joint IDs refer to bones in the model skeleton",
            solution="Select the target armature in the CCL import options",
        )
    if find_ccl_file_for_armature(armature):
        raise AlbamCheckFailure(
            f"Armature {armature.name!r} already has an imported .ccl file",
            details="Bone properties currently hold one CCL record set per armature",
            solution="Use the existing CCL preview, or remove it before importing a replacement",
        )

    ccl = _parse_ccl(vfile.get_bytes())
    joint_map, duplicate_ids = _bone_map(armature)
    for pose_bone in armature.pose.bones:
        bone_props = get_ccl_bone_properties(pose_bone)
        bone_props.records.clear()
        bone_props.active_record_index = 0
    unresolved = 0
    for record_index, src_record in enumerate(ccl.col_infos):
        pose_bone = joint_map.get(src_record.ref_joint_no)
        if pose_bone is None:
            unresolved += 1
            continue
        if int(src_record.shape) == 1 and src_record.pair_joint_no not in joint_map:
            unresolved += 1
        bone_props = get_ccl_bone_properties(pose_bone)
        _load_record(bone_props.records.add(), src_record, record_index)

    bl_object = bpy.data.objects.new(vfile.display_name, None)
    bl_object.empty_display_type = "PLAIN_AXES"
    bl_object.empty_display_size = 0.01
    file_props = get_ccl_file_properties(bl_object)
    file_props.armature = armature
    file_props.record_count = len(ccl.col_infos)
    file_props.unresolved_records = unresolved
    file_props.duplicate_joint_ids = ", ".join(map(str, sorted(duplicate_ids)))
    # The empty carries the Albam asset; individual child meshes form the preview.
    bl_object.hide_render = True
    rebuild_ccl_preview(bl_object)
    return bl_object


def _uint32(value, label):
    try:
        result = int(value)
    except (TypeError, ValueError) as ex:
        raise AlbamCheckFailure(
            f"Invalid CCL {label}",
            details=f"Expected an unsigned 32-bit integer, found {value!r}",
            solution=f"Enter a whole number from 0 to {0xFFFFFFFF}",
        ) from ex
    if not 0 <= result <= 0xFFFFFFFF:
        raise AlbamCheckFailure(
            f"Invalid CCL {label}",
            details=f"{result} does not fit the unsigned 32-bit field",
            solution=f"Enter a whole number from 0 to {0xFFFFFFFF}",
        )
    return result


def _set_vec3(dst, values):
    values = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in values):
        raise AlbamCheckFailure(
            "Invalid CCL vector value",
            details=f"CCL coordinates and angles must be finite, found {values!r}",
            solution="Replace NaN or infinity values with finite numbers",
        )
    dst.x, dst.y, dst.z = values


def _apply_record(dst, pose_bone, record):
    dst.attr = _uint32(record.attr, "attribute")
    dst.ref_joint_no = _joint_id_from_bone(pose_bone)
    if not 0 <= record.pair_joint_no <= 0xFFFF:
        raise AlbamCheckFailure(
            "Invalid CCL tail joint ID",
            details=f"{record.pair_joint_no} does not fit the u2 field",
            solution="Enter a whole number from 0 to 65535",
        )
    dst.pair_joint_no = record.pair_joint_no
    shape = _SHAPE_TO_INT.get(record.shape)
    if shape is None:
        raise AlbamCheckFailure(
            "Invalid CCL collision shape",
            details=f"Unknown shape {record.shape!r}",
            solution="Choose Sphere, Capsule, AABB, or OBB",
        )
    dst.shape = Ccl156.Shape(shape)
    _set_vec3(dst.position, record.position)
    dst.id = _uint32(record.id, "ID")
    _set_vec3(dst.extent, record.extent)
    dst.radius = float(record.radius)
    if not math.isfinite(dst.radius) or dst.radius < 0.0:
        raise AlbamCheckFailure(
            "Invalid CCL radius",
            details=f"Radius must be finite and non-negative, found {dst.radius!r}",
            solution="Enter a finite radius of zero or greater",
        )
    _set_vec3(dst.angle, record.angle)


def _new_record(parent, pose_bone, record):
    dst = Ccl156.ColInfo(_parent=parent, _root=parent)
    dst.reserve = b"\x00\x00\x00"
    dst.reserve1 = 0.0
    dst.reserve2 = 0.0
    dst.position = Ccl156.Vec3(_parent=dst, _root=parent)
    dst.extent = Ccl156.Vec3(_parent=dst, _root=parent)
    dst.angle = Ccl156.Vec3(_parent=dst, _root=parent)
    _apply_record(dst, pose_bone, record)
    return dst


@blender_registry.register_export_function(app_id="re5", extension="ccl")
def export_ccl(bl_object):
    asset = bl_object.albam_asset
    if asset.app_id != "re5" or asset.extension != "ccl":
        raise AlbamCheckFailure(
            "This preview is not a supported RE5 CCL asset",
            details=f"Asset app/extension: {asset.app_id!r}/{asset.extension!r}",
            solution="Select a CCL preview imported for Resident Evil 5",
        )
    ccl = _parse_ccl(asset.original_bytes)
    file_props = get_ccl_file_properties(bl_object)
    armature = file_props.armature if file_props else None
    if armature is None or armature.type != "ARMATURE":
        raise AlbamCheckFailure(
            "The skeleton used by this CCL file is missing",
            details="The CCL preview no longer points to its imported armature",
            solution="Restore the armature pointer on the preview's Albam custom properties",
        )

    removed_indices = set()
    try:
        removed_indices = {
            int(i) for i in json.loads(bl_object.get("_albam_ccl_removed_records", "[]"))
        }
    except (TypeError, ValueError):
        pass

    edited_records = {}
    new_records = []
    for pose_bone in armature.pose.bones:
        bone_props = get_ccl_bone_properties(pose_bone)
        for record in bone_props.records:
            if record.record_index < 0:
                new_records.append((pose_bone, record))
                continue
            if record.record_index >= len(ccl.col_infos):
                raise AlbamCheckFailure(
                    "A CCL bone record points outside the source file",
                    details=f"Record index {record.record_index}, file has {len(ccl.col_infos)} records",
                    solution="Re-import the CCL file to restore its record mapping",
                )
            if record.record_index in edited_records:
                raise AlbamCheckFailure(
                    "Two bones contain the same CCL record",
                    details=f"Record index {record.record_index} is assigned more than once",
                    solution="Keep each imported CCL record on its original bone",
                )
            edited_records[record.record_index] = (pose_bone, record)

    out_records = []
    for record_index, src_record in enumerate(ccl.col_infos):
        if record_index in removed_indices:
            continue
        edit = edited_records.get(record_index)
        if edit:
            _apply_record(src_record, edit[0], edit[1])
        out_records.append(src_record)

    for pose_bone, record in sorted(new_records, key=lambda pair: pair[0].name):
        out_records.append(_new_record(ccl, pose_bone, record))

    if len(out_records) > 0xFFFFFFFF or len(out_records) * _CCL_RECORD_SIZE > 0xFFFFFFFF:
        raise AlbamCheckFailure(
            "The CCL file contains too many records to export",
            details=f"Record count is {len(out_records)}",
            solution="Remove records until the file fits the CCL size fields",
        )
    ccl.num_col_infos = len(out_records)
    ccl.data_size = len(out_records) * _CCL_RECORD_SIZE
    ccl.col_infos = out_records

    check_recursive(ccl)
    stream = KaitaiStream(BytesIO(bytearray(_CCL_HEADER_SIZE + ccl.data_size)))
    ccl._write(stream)
    vfile = VirtualFileData(asset.app_id, asset.relative_path,
                            data_bytes=stream.to_byte_array())
    return [vfile]


# Importing these modules runs their Blender registration decorators.
from . import chain_ui as _chain_ui  # noqa: E402,F401
