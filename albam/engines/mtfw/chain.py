"""RE5 chain-collision (.ccl) and chain-simulation (.chn) import and export."""

import json
import math
from io import BytesIO

import bpy
from kaitaistruct import KaitaiStream

from .bone import get_anim_retarget
from .chain_preview import rebuild_ccl_preview
from .chn_graph import decompose_edges, ordered_links_from_strands
from .chain_props import (
    find_ccl_file_for_armature,
    find_chn_file_for_armature,
    get_ccl_bone_properties,
    get_ccl_file_properties,
    get_chn_file_properties,
)
from .chn_preview import rebuild_chn_previews
from .structs.ccl_156 import Ccl156
from .structs.chn import Chn
from ...exceptions import AlbamCheckFailure
from ...lib.kaitai_utils import check_recursive, parse
from ...registry import blender_registry
from ...vfs import VirtualFileData


_CCL_MAGIC = b"CCL\x00"
_CCL_VERSION = 0x80618
_CCL_HEADER_SIZE = 16
_CCL_RECORD_SIZE = 64
_SHAPE_TO_INT = {"SPHERE": 0, "CAPSULE": 1, "AABB": 2, "OBB": 3}
_CHN_MAGIC = b"CHN\x00"
_CHN_VERSION = 0x80618
_CHN_HEADER_SIZE = 16
_CHN_CHAIN_INFO_SIZE = 32
_CHN_JOINT_INFO_SIZE = 96


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


def _parse_chn(data):
    if len(data) < _CHN_HEADER_SIZE:
        raise AlbamCheckFailure(
            "This .chn file appears to be truncated or corrupted",
            details=f"The file is only {len(data)} bytes long",
            solution="Re-extract the file from the game's archive and try again",
        )
    if data[:4] != _CHN_MAGIC:
        raise AlbamCheckFailure(
            "The selected file is not a supported .chn resource",
            details=f"Expected CHN magic, found {data[:4]!r}",
            solution="Select an RE5 chain-simulation file with the CHN format",
        )

    version = int.from_bytes(data[4:8], "little")
    data_size = int.from_bytes(data[8:12], "little")
    num_chains = data[12]
    expected_size = _CHN_HEADER_SIZE + data_size
    if version != _CHN_VERSION:
        raise AlbamCheckFailure(
            "This .chn version is not supported",
            details=f"Found version 0x{version:x}; 0x{_CHN_VERSION:x} is supported",
            solution="Use a .chn file from a supported MT Framework game",
        )
    if len(data) != expected_size:
        raise AlbamCheckFailure(
            "This .chn file has an inconsistent size",
            details=(f"Header declares {data_size} data bytes, but the file contains {len(data)} "
                     f"bytes; expected {expected_size}"),
            solution="Re-extract the .chn file and try importing it again",
        )

    try:
        chn = parse(Chn, data)
        table_end = _CHN_HEADER_SIZE + _CHN_CHAIN_INFO_SIZE * num_chains
        joint_ranges = []
        for chain_info in chn.chain_infos:
            if int(chain_info.chain_type) not in (1, 2):
                raise ValueError(
                    f"Chain {chain_info.index} has unsupported type {chain_info.chain_type}")
            joint_start = chain_info.joints_pos
            joint_end = joint_start + _CHN_JOINT_INFO_SIZE * chain_info.num_joints
            if chain_info.num_joints and (joint_start < table_end or joint_end > expected_size):
                raise ValueError(
                    f"Chain {chain_info.index} joint range {joint_start:#x}..{joint_end:#x} "
                    f"is outside the CHN data section")
            if chain_info.num_joints:
                joint_ranges.append((joint_start, joint_end, chain_info.index))
            # Resolve each lazy instance now so malformed offsets fail during import.
            _ = chain_info.joints
            for joint_index, joint in enumerate(chain_info.joints):
                if int(joint.col_shape) not in (1, 2):
                    raise ValueError(
                        f"Chain {chain_info.index} joint {joint_index} has unsupported "
                        f"collision shape {joint.col_shape}")
                if joint.node_num > 8:
                    raise ValueError(
                        f"Chain {chain_info.index} joint {joint_index} declares "
                        f"{joint.node_num} nodes; CHN supports at most 8")
        joint_ranges.sort()
        for previous, current in zip(joint_ranges, joint_ranges[1:]):
            if current[0] < previous[1]:
                raise ValueError(
                    f"Chain {previous[2]} and chain {current[2]} joint data overlap")
        return chn
    except AlbamCheckFailure:
        raise
    except Exception as ex:
        raise AlbamCheckFailure(
            "This .chn file could not be parsed",
            details=f"{type(ex).__name__}: {ex}",
            solution="Check that this is a valid RE5 CHN resource",
        ) from ex


def _load_chn_joint(dst, src, chain_index, joint_index, source_joint_index=None):
    dst.chain_index = chain_index
    dst.joint_index = joint_index
    dst.source_joint_index = (joint_index if source_joint_index is None else source_joint_index)
    dst.source_ref_joint_no = int(src.ref_joint_no)
    dst.raw_node_num = int(src.node_num)
    dst.raw_node_slots = bytes(src.node_joint_no).hex()
    dst.preview_object = None
    dst.ref_joint_no = src.ref_joint_no
    dst.attr = str(src.attr)
    dst.min_angle = (src.min_angle.x, src.min_angle.y, src.min_angle.z)
    dst.spring_coef = src.spring_coef
    dst.max_angle = (src.max_angle.x, src.max_angle.y, src.max_angle.z)
    dst.dumping_coef = src.dumping_coef
    dst.mass = src.mass
    dst.restrict_flag = src.restrict_flag
    dst.col_shape = "CAPSULE" if int(src.col_shape) == 2 else "SPHERE"
    dst.col_radius = src.col_radius
    dst.air_regist = src.air_regist
    dst.friction = src.friction
    dst.soft_coef = src.soft_coef
    dst.bend_regist = src.bend_regist


def _chn_joint_id_from_bone(pose_bone):
    raw_id = get_anim_retarget(pose_bone, "re5")
    if not raw_id:
        raise AlbamCheckFailure(
            f"Bone {pose_bone.name!r} has no animation joint ID",
            details="CHN joints address bones through the model's Anim Retarget IDs",
            solution="Set an Anim Retarget ID on this bone before exporting its CHN joint",
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
            f"Bone {pose_bone.name!r} has an out-of-range CHN joint ID",
            details=f"Joint ID {joint_id} does not fit the CHN u2 field",
            solution="Set an Anim Retarget ID between 0 and 65535",
        )
    return joint_id


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


@blender_registry.register_import_function(
    app_id="re5", extension="chn", albam_asset_type="PHYSICS")
def load_chn(vfile, context) -> bpy.types.Object:
    if vfile.app_id != "re5":
        raise AlbamCheckFailure(
            "CHN import is currently supported for Resident Evil 5",
            details=f"The selected app is {vfile.app_id!r}",
            solution="Select Resident Evil 5 and import the corresponding .chn file",
        )
    armature = context.scene.albam.import_options_chain.armature
    if armature is None or armature.type != "ARMATURE":
        raise AlbamCheckFailure(
            "Choose a skeleton before importing this .chn file",
            details="CHN joint IDs refer to bones in the model skeleton",
            solution="Select the target armature in the CHN import options",
        )
    if find_chn_file_for_armature(armature):
        raise AlbamCheckFailure(
            f"Armature {armature.name!r} already has an imported .chn file",
            details="CHN joint data is stored on the armature's pose bones",
            solution="Use the existing CHN settings, or remove that CHN file before importing a replacement",
        )

    chn = _parse_chn(vfile.get_bytes())
    joint_map, duplicate_ids = _bone_map(armature)
    for pose_bone in armature.pose.bones:
        bone_props = get_ccl_bone_properties(pose_bone)
        bone_props.chn_joints.clear()
        bone_props.active_chn_joint_index = 0
    unresolved = 0
    unresolved_links = 0
    total_joints = 0
    bl_object = bpy.data.objects.new(vfile.display_name, None)
    bl_object.empty_display_type = "PLAIN_AXES"
    bl_object.empty_display_size = 0.01
    bl_object.hide_render = True
    bl_object["_albam_chn_root"] = True
    bl_object["_albam_chn_suppress_update"] = True

    file_props = get_chn_file_properties(bl_object)
    file_props.armature = armature
    file_props.chain_count = len(chn.chain_infos)
    file_props.duplicate_joint_ids = ", ".join(map(str, sorted(duplicate_ids)))
    for chain_index, chain_info in enumerate(chn.chain_infos):
        total_joints += chain_info.num_joints
        chain_props = file_props.chains.add()
        chain_props.chain_index = chain_index
        chain_props.num_joints = chain_info.num_joints
        chain_props.chain_type = int(chain_info.chain_type)
        chain_props.grav_scaler = chain_info.grav_scaler
        chain_props.time_scaler = chain_info.time_scaler
        chain_props.dump_scaler = chain_info.dump_scaler
        chain_props.topology_dirty = False
        chain_records = []
        for joint_index, src_joint in enumerate(chain_info.joints):
            pose_bone = joint_map.get(src_joint.ref_joint_no)
            if pose_bone is None:
                joint_props = file_props.orphans.add()
                unresolved += 1
            else:
                joint_props = get_ccl_bone_properties(pose_bone).chn_joints.add()
            node_count = min(max(int(src_joint.node_num), 0), len(src_joint.node_joint_no))
            unresolved += sum(
                1 for node_joint_no in src_joint.node_joint_no[:node_count]
                if node_joint_no not in joint_map)
            _load_chn_joint(joint_props, src_joint, chain_index, joint_index)
            chain_records.append(joint_props)

        anim_ids = [record.ref_joint_no for record in chain_records]
        # Duplicate IDs make the graph ambiguous. Keep the original slots for
        # lossless export and leave strand authoring empty until the user fixes it.
        known_ids = set(anim_ids)
        edges = []
        for record in chain_records:
            try:
                raw_slots = bytes.fromhex(record.raw_node_slots)
            except ValueError:
                raw_slots = b""
            node_count = min(max(record.raw_node_num, 0), len(raw_slots))
            unresolved_links += sum(
                1 for target_id in raw_slots[:node_count]
                if target_id not in known_ids
            )
            edges.extend(
                (record.ref_joint_no, target_id)
                for target_id in raw_slots[:node_count]
                if target_id in known_ids and target_id != record.ref_joint_no
            )
        if len(anim_ids) == len(known_ids):
            for strand_index, strand_data in enumerate(decompose_edges(anim_ids, edges)):
                strand = chain_props.strands.add()
                strand.strand_index = strand_index
                strand.closed = strand_data["closed"]
                strand.name = f"Strand {strand_index + 1}"
                for anim_id in strand_data["joints"]:
                    strand.joints.add().anim_id = anim_id

    file_props.total_joints = total_joints
    file_props.unresolved_joints = unresolved
    file_props.unresolved_links = unresolved_links
    bl_object["_albam_chn_suppress_update"] = False
    rebuild_chn_previews(bl_object)
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
            "Invalid chain vector value",
            details=f"Chain coordinates and angles must be finite, found {values!r}",
            solution="Replace NaN or infinity values with finite numbers",
        )
    dst.x, dst.y, dst.z = values


def _chn_uint(value, bits, label):
    try:
        result = int(value)
    except (TypeError, ValueError) as ex:
        raise AlbamCheckFailure(
            f"Invalid CHN {label}",
            details=f"Expected an unsigned {bits}-bit integer, found {value!r}",
            solution=f"Enter a whole number from 0 to {(1 << bits) - 1}",
        ) from ex
    if not 0 <= result < (1 << bits):
        raise AlbamCheckFailure(
            f"Invalid CHN {label}",
            details=f"{result} does not fit the unsigned {bits}-bit field",
            solution=f"Enter a whole number from 0 to {(1 << bits) - 1}",
        )
    return result


def _chn_finite(value, label):
    result = float(value)
    if not math.isfinite(result):
        raise AlbamCheckFailure(
            f"Invalid CHN {label}",
            details=f"Expected a finite number, found {result!r}",
            solution="Replace NaN or infinity with a finite number",
        )
    return result


def _chn_record_anim_id(record, pose_bone):
    if pose_bone is not None:
        return _chn_joint_id_from_bone(pose_bone)
    return _chn_uint(record.ref_joint_no, 16, "reference Anim ID")


def _build_chn_topology(ordered_records, chain_index):
    """Build an undirected path graph from consecutive JointInfo slots."""
    anim_ids = [
        _chn_record_anim_id(record, pose_bone)
        for record, pose_bone in ordered_records
    ]
    if len(anim_ids) != len(set(anim_ids)):
        raise AlbamCheckFailure(
            f"Chain Info {chain_index} has duplicate joint Anim IDs",
            details=f"Joint IDs in this Chain Info are {anim_ids}",
            solution="Give each joint in the Chain Info a unique Anim Retarget ID",
        )

    topology = []
    for index in range(len(anim_ids)):
        neighbor_ids = []
        if index > 0:
            neighbor_ids.append(anim_ids[index - 1])
        if index + 1 < len(anim_ids):
            neighbor_ids.append(anim_ids[index + 1])
        encoded_neighbors = tuple(
            _chn_uint(anim_id, 8, "node joint ID") for anim_id in neighbor_ids)
        padded_neighbors = encoded_neighbors + (0,) * (8 - len(encoded_neighbors))
        topology.append((len(encoded_neighbors), padded_neighbors))
    return topology


def _chn_topology_for_chain(chain_props, ordered_records, chain_index):
    """Choose exact source slots, authored strands, or the legacy path fallback."""
    anim_ids = [
        _chn_record_anim_id(record, pose_bone)
        for record, pose_bone in ordered_records
    ]
    identity_changed = any(
        anim_id != (record.source_ref_joint_no
                    if record.source_ref_joint_no >= 0 else record.ref_joint_no)
        for anim_id, (record, _pose_bone) in zip(anim_ids, ordered_records)
    )
    if not chain_props.topology_dirty:
        raw_topology = []
        for record, _pose_bone in ordered_records:
            if record.raw_node_num < 0:
                raw_topology = []
                break
            try:
                slots = tuple(bytes.fromhex(record.raw_node_slots))
            except ValueError:
                slots = ()
            if len(slots) != 8 or not 0 <= record.raw_node_num <= 8:
                raw_topology = []
                break
            # Only the first node_num entries are meaningful. Real files often
            # carry 0xCD in the unused tail (the MSVC debug-heap fill pattern),
            # so normalize that tail instead of treating it as CHN data.
            node_count = record.raw_node_num
            raw_topology.append((node_count, slots[:node_count] + (0,) * (8 - node_count)))
        if len(raw_topology) == len(ordered_records) and not identity_changed:
            return raw_topology

        # Scenes saved before the strand model have no raw slot cache. Preserve
        # their former export behavior until they are rebuilt or edited.
        if not chain_props.strands:
            return _build_chn_topology(ordered_records, chain_index)

    if len(anim_ids) != len(set(anim_ids)):
        raise AlbamCheckFailure(
            f"Chain Info {chain_index} has duplicate joint Anim IDs",
            details=f"Joint IDs in this Chain Info are {anim_ids}",
            solution="Give each joint in the Chain Info a unique Anim Retarget ID",
        )
    records_by_id = set(anim_ids)
    id_remap = {
        (record.source_ref_joint_no
         if record.source_ref_joint_no >= 0 else record.ref_joint_no): anim_id
        for anim_id, (record, _pose_bone) in zip(anim_ids, ordered_records)
    }
    authored_strands = []
    for strand in chain_props.strands:
        ids = [id_remap.get(joint.anim_id, joint.anim_id) for joint in strand.joints]
        missing = [anim_id for anim_id in ids if anim_id not in records_by_id]
        if missing:
            raise AlbamCheckFailure(
                f"Chain Info {chain_index} has a strand pointing to a missing joint",
                details=f"Strand references Anim IDs {sorted(set(missing))}",
                solution="Remove the missing IDs from the strand or add those joints to the ChainInfo",
            )
        authored_strands.append({"joints": ids, "closed": strand.closed})

    raw_links = {}
    for anim_id, (record, _pose_bone) in zip(anim_ids, ordered_records):
        if record.raw_node_num < 0:
            continue
        try:
            slots = bytes.fromhex(record.raw_node_slots)
        except ValueError:
            slots = b""
        if len(slots) == 8 and 0 <= record.raw_node_num <= 8:
            raw_links[anim_id] = {
                id_remap.get(target, target)
                for target in slots[:record.raw_node_num]
            }
    ordered_links = ordered_links_from_strands(authored_strands, raw_links)

    topology_by_id = {}
    for anim_id in anim_ids:
        neighbors = ordered_links.get(anim_id, [])
        if len(neighbors) > 8:
            raise AlbamCheckFailure(
                "A CHN joint has too many graph links",
                details=f"Anim ID {anim_id} has {len(neighbors)} links; CHN supports at most 8",
                solution="Split the graph or remove links until each joint has at most 8 neighbors",
            )
        encoded = tuple(_chn_uint(target, 8, "node joint ID") for target in neighbors)
        topology_by_id[anim_id] = (len(encoded), encoded + (0,) * (8 - len(encoded)))
    return [topology_by_id[anim_id] for anim_id in anim_ids]


def _apply_chn_joint(dst, record, pose_bone, topology):
    node_count = _chn_uint(topology[0], 8, "node count")
    if node_count > 8:
        raise AlbamCheckFailure(
            "Invalid CHN node count",
            details=f"A joint can reference at most 8 nodes, found {node_count}",
            solution="Set Node Count to a value from 0 to 8",
        )
    node_joint_ids = topology[1]
    if len(node_joint_ids) != 8:
        raise AlbamCheckFailure(
            "Invalid CHN node joint list",
            details=f"Expected 8 node IDs, found {len(node_joint_ids)}",
            solution="Keep all 8 Node Joint IDs fields",
        )

    dst.attr = _chn_uint(record.attr, 32, "attribute mask")
    dst.ref_joint_no = (
        _chn_joint_id_from_bone(pose_bone) if pose_bone is not None
        else _chn_uint(record.ref_joint_no, 16, "reference Anim ID"))
    dst.node_num = node_count
    _set_vec3(dst.min_angle, record.min_angle)
    dst.spring_coef = _chn_finite(record.spring_coef, "spring coefficient")
    _set_vec3(dst.max_angle, record.max_angle)
    dst.dumping_coef = _chn_finite(record.dumping_coef, "damping coefficient")
    dst.mass = _chn_finite(record.mass, "mass")
    dst.restrict_flag = _chn_uint(record.restrict_flag, 8, "restrict flag")
    dst.col_shape = {"SPHERE": 1, "CAPSULE": 2}.get(record.col_shape)
    if dst.col_shape is None:
        raise AlbamCheckFailure(
            "Invalid CHN collision shape",
            details=f"Unknown CHN collision shape {record.col_shape!r}",
            solution="Choose Sphere or Capsule",
        )
    dst.col_radius = _chn_finite(record.col_radius, "collision radius")
    dst.air_regist = _chn_finite(record.air_regist, "air resistance")
    dst.node_joint_no = list(node_joint_ids)
    dst.friction = _chn_finite(record.friction, "friction")
    dst.soft_coef = _chn_finite(record.soft_coef, "soft coefficient")
    dst.bend_regist = _chn_finite(record.bend_regist, "bend resistance")


def _serialize_chn(chn):
    """Serialize updated CHN chains, preserving source record reserve fields."""
    chn.num_chain_infos = len(chn.chain_infos)
    data_size = _CHN_CHAIN_INFO_SIZE * len(chn.chain_infos)
    for chain_info in chn.chain_infos:
        chain_info.num_joints = len(chain_info._m_joints)
        data_size += _CHN_JOINT_INFO_SIZE * chain_info.num_joints
    if data_size > 0xFFFFFFFF:
        raise AlbamCheckFailure(
            "The CHN data is too large to export",
            details=f"The serialized data section would be {data_size} bytes",
            solution="Reduce the number of joint records in the CHN chains",
        )
    chn.data_size = data_size

    next_joint_pos = _CHN_HEADER_SIZE + _CHN_CHAIN_INFO_SIZE * len(chn.chain_infos)
    for chain_info in chn.chain_infos:
        chain_info.joint_info_offset = next_joint_pos - chain_info.position
        chain_info._invalidate_joints_pos()
        next_joint_pos += _CHN_JOINT_INFO_SIZE * chain_info.num_joints

    stream = KaitaiStream(BytesIO(bytearray(_CHN_HEADER_SIZE + data_size)))
    chn._io = stream
    for chain_info in chn.chain_infos:
        chain_info._io = stream
        for joint in chain_info._m_joints:
            joint._io = stream
            joint.min_angle._io = stream
            joint.max_angle._io = stream

    check_recursive(chn)
    # Write the header tables first, then each lazy joint array at its new offset.
    chn._write__seq()
    for chain_info in chn.chain_infos:
        stream.seek(chain_info.joints_pos)
        for joint in chain_info._m_joints:
            joint._write__seq()
    return stream.to_byte_array()


def _new_chn_joint(parent, root):
    joint = Chn.JointInfo(_parent=parent, _root=root)
    joint.reserve0 = 0
    joint.reserve1 = [0, 0]
    joint.min_angle = Chn.Vec3(_parent=joint, _root=root)
    joint.min_angle.x = joint.min_angle.y = joint.min_angle.z = 0.0
    joint.spring_coef = 0.0
    joint.max_angle = Chn.Vec3(_parent=joint, _root=root)
    joint.max_angle.x = joint.max_angle.y = joint.max_angle.z = 0.0
    joint.dumping_coef = 0.0
    joint.mass = 0.0
    joint.restrict_flag = 0
    joint.col_shape = 1
    joint.reserve2 = b"\x00\x00"
    joint.col_radius = 1.0
    joint.air_regist = 0.0
    joint.node_joint_no = [0] * 8
    joint.friction = 0.0
    joint.soft_coef = 0.0
    joint.bend_regist = 0.0
    joint.reserve = [0, 0, 0]
    return joint


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


@blender_registry.register_export_function(app_id="re5", extension="chn")
def export_chn(bl_object):
    asset = bl_object.albam_asset
    if asset.app_id != "re5" or asset.extension != "chn":
        raise AlbamCheckFailure(
            "This object is not a supported RE5 CHN asset",
            details=f"Asset app/extension: {asset.app_id!r}/{asset.extension!r}",
            solution="Select a CHN asset imported for Resident Evil 5",
        )

    original_bytes = asset.original_bytes
    chn = _parse_chn(original_bytes)
    file_props = get_chn_file_properties(bl_object)
    armature = file_props.armature if file_props else None
    if armature is None or armature.type != "ARMATURE":
        raise AlbamCheckFailure(
            "The skeleton used by this CHN file is missing",
            details="The CHN file object no longer points to its imported armature",
            solution="Restore the armature pointer on the CHN file properties",
        )
    if len(file_props.chains) != len(chn.chain_infos):
        raise AlbamCheckFailure(
            "The CHN chain settings no longer match the source file",
            details=(f"File contains {len(chn.chain_infos)} chains, but Albam has "
                     f"{len(file_props.chains)} chain settings"),
            solution="Re-import the CHN file to restore its chain settings",
        )

    chain_props_by_index = {}
    for chain_props in file_props.chains:
        chain_index = chain_props.chain_index
        if not 0 <= chain_index < len(chn.chain_infos) or chain_index in chain_props_by_index:
            raise AlbamCheckFailure(
                "The CHN chain settings have invalid indices",
                details=f"Found duplicate or out-of-range chain index {chain_index}",
                solution="Re-import the CHN file to restore its chain settings",
            )
        chain_props_by_index[chain_index] = chain_props

    joints_by_chain = {index: [] for index in range(len(chn.chain_infos))}
    for pose_bone in armature.pose.bones:
        for record in get_ccl_bone_properties(pose_bone).chn_joints:
            if not 0 <= record.chain_index < len(chn.chain_infos):
                raise AlbamCheckFailure(
                    "A bone CHN joint points to a missing chain",
                    details=f"Bone {pose_bone.name!r} refers to chain {record.chain_index}",
                    solution="Attach the joint to an existing chain before exporting",
                )
            joints_by_chain[record.chain_index].append((record, pose_bone))
    for record in file_props.orphans:
        if not 0 <= record.chain_index < len(chn.chain_infos):
            raise AlbamCheckFailure(
                "An orphan CHN joint points to a missing chain",
                details=f"Orphan record refers to chain {record.chain_index}",
                solution="Attach the orphan to an existing chain before exporting",
            )
        joints_by_chain[record.chain_index].append((record, None))

    for chain_index, chain_info in enumerate(chn.chain_infos):
        chain_props = chain_props_by_index.get(chain_index)
        if chain_props is None:
            raise AlbamCheckFailure(
                "A CHN chain setting is missing",
                details=f"No settings are stored for chain {chain_index}",
                solution="Re-import the CHN file to restore all chain settings",
            )
        if not 0 <= chain_props.num_joints <= 0xFF:
            raise AlbamCheckFailure(
                "Invalid CHN joint count",
                details=f"Chain {chain_index} has {chain_props.num_joints} joint slots",
                solution="Use a joint count from 0 to 255",
            )
        chain_info.chain_type = _chn_uint(chain_props.chain_type, 8, "chain type")
        chain_info.grav_scaler = _chn_finite(chain_props.grav_scaler, "gravity scale")
        chain_info.time_scaler = _chn_finite(chain_props.time_scaler, "time scale")
        chain_info.dump_scaler = _chn_finite(chain_props.dump_scaler, "damping scale")

        chain_records = joints_by_chain[chain_index]
        if len(chain_records) != chain_props.num_joints:
            raise AlbamCheckFailure(
                f"Chain {chain_index} has missing or extra bone assignments",
                details=(f"Header declares {chain_props.num_joints} joints, but "
                         f"{len(chain_records)} bone/orphan records are assigned"),
                solution="Attach one bone or orphan record for every joint index in the chain",
            )
        ordered_records = [None] * chain_props.num_joints
        seen_source_indices = set()
        for record, pose_bone in chain_records:
            if record.chain_index != chain_index:
                raise AlbamCheckFailure(
                    "A CHN joint is stored under the wrong chain",
                    details=(f"Chain {chain_index} contains a record marked for chain "
                             f"{record.chain_index}"),
                    solution="Restore the original chain assignment before exporting",
                )
            if not 0 <= record.joint_index < chain_props.num_joints:
                raise AlbamCheckFailure(
                    f"Chain {chain_index} has an invalid joint index",
                    details=f"Joint index {record.joint_index} is outside the chain",
                    solution="Use contiguous joint indices from 0 to the chain size minus 1",
                )
            if ordered_records[record.joint_index] is not None:
                raise AlbamCheckFailure(
                    f"Chain {chain_index} has duplicate joint indices",
                    details=f"Joint index {record.joint_index} appears more than once",
                    solution="Keep one CHN joint assignment for each joint index",
                )
            if record.source_joint_index < -1:
                raise AlbamCheckFailure(
                    f"Chain {chain_index} has an invalid source joint reference",
                    details=f"Source joint index {record.source_joint_index} is below -1",
                    solution="Re-import the CHN file to restore its source joint mapping",
                )
            if record.source_joint_index >= 0:
                if (record.source_joint_index >= chain_info.num_joints or
                        record.source_joint_index in seen_source_indices):
                    raise AlbamCheckFailure(
                        f"Chain {chain_index} has invalid source joint references",
                        details=f"Source joint index {record.source_joint_index} is invalid or repeated",
                        solution="Re-import the CHN file to restore its source joint mapping",
                    )
                seen_source_indices.add(record.source_joint_index)
            ordered_records[record.joint_index] = (record, pose_bone)

        if any(item is None for item in ordered_records):
            missing = [index for index, item in enumerate(ordered_records) if item is None]
            raise AlbamCheckFailure(
                f"Chain {chain_index} has gaps in its joint indices",
                details=f"Missing joint indices: {missing}",
                solution="Use a contiguous sequence of joint indices starting at zero",
            )

        topology = _chn_topology_for_chain(chain_props, ordered_records, chain_index)
        source_joints = list(chain_info.joints)
        output_joints = []
        for joint_index, (record, pose_bone) in enumerate(ordered_records):
            if record.source_joint_index >= 0:
                dst = source_joints[record.source_joint_index]
            else:
                dst = _new_chn_joint(chain_info, chn)
            _apply_chn_joint(dst, record, pose_bone, topology[joint_index])
            output_joints.append(dst)
        chain_info.num_joints = len(output_joints)
        chain_info.joints = output_joints

    output_bytes = _serialize_chn(chn)
    vfile = VirtualFileData(asset.app_id, asset.relative_path, data_bytes=output_bytes)
    return [vfile]


# Importing these modules runs their Blender registration decorators.
from . import chain_ui as _chain_ui  # noqa: E402,F401
