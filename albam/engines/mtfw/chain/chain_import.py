"""RE5 chain-collision and chain-simulation import handlers."""

import bpy

from ..bone import get_anim_retarget
from ..structs.ccl_156 import Ccl156
from ..structs.chn import Chn
from ....exceptions import AlbamCheckFailure
from ....lib.kaitai_utils import parse
from ....registry import blender_registry
from .ccl_preview import rebuild_ccl_preview
from .chn_preview import rebuild_chn_previews
from .graph import decompose_edges
from .properties import (
    find_ccl_file_for_armature,
    find_chn_file_for_armature,
    get_ccl_bone_properties,
    get_ccl_file_properties,
    get_chn_file_properties,
)

CCL_MAGIC = b"CCL\x00"
CCL_VERSION = 0x80618
CCL_HEADER_SIZE = 16
CCL_RECORD_SIZE = 64
SHAPE_TO_INT = {"SPHERE": 0, "CAPSULE": 1, "AABB": 2, "OBB": 3}
CHN_MAGIC = b"CHN\x00"
CHN_VERSION = 0x80618
CHN_HEADER_SIZE = 16
CHN_CHAIN_INFO_SIZE = 32
CHN_JOINT_INFO_SIZE = 96


def _parse_ccl(data):
    if len(data) < CCL_HEADER_SIZE:
        raise AlbamCheckFailure(
            "This .ccl file appears to be truncated or corrupted",
            details=f"The file is only {len(data)} bytes long",
            solution="Re-extract the file from the game's archive and try importing it again",
        )
    if data[:4] != CCL_MAGIC:
        raise AlbamCheckFailure(
            "The selected file is not a supported .ccl resource",
            details=f"Expected CCL magic, found {data[:4]!r}",
            solution="Check that this is a chain-collision file from Resident Evil 5",
        )

    version = int.from_bytes(data[4:8], "little")
    count = int.from_bytes(data[8:12], "little")
    data_size = int.from_bytes(data[12:16], "little")
    expected_data_size = count * CCL_RECORD_SIZE
    expected_size = CCL_HEADER_SIZE + expected_data_size
    if version != CCL_VERSION:
        raise AlbamCheckFailure(
            "This .ccl version is not supported",
            details=f"Found version 0x{version:x}; RE5 CCL version 0x{CCL_VERSION:x} is supported",
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
    if len(data) < CHN_HEADER_SIZE:
        raise AlbamCheckFailure(
            "This .chn file appears to be truncated or corrupted",
            details=f"The file is only {len(data)} bytes long",
            solution="Re-extract the file from the game's archive and try again",
        )
    if data[:4] != CHN_MAGIC:
        raise AlbamCheckFailure(
            "The selected file is not a supported .chn resource",
            details=f"Expected CHN magic, found {data[:4]!r}",
            solution="Select an RE5 chain-simulation file with the CHN format",
        )

    version = int.from_bytes(data[4:8], "little")
    data_size = int.from_bytes(data[8:12], "little")
    num_chains = data[12]
    expected_size = CHN_HEADER_SIZE + data_size
    if version != CHN_VERSION:
        raise AlbamCheckFailure(
            "This .chn version is not supported",
            details=f"Found version 0x{version:x}; 0x{CHN_VERSION:x} is supported",
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
        table_end = CHN_HEADER_SIZE + CHN_CHAIN_INFO_SIZE * num_chains
        joint_ranges = []
        for chain_info in chn.chain_infos:
            if int(chain_info.chain_type) not in (1, 2):
                raise ValueError(
                    f"Chain {chain_info.index} has unsupported type {chain_info.chain_type}")
            joint_start = chain_info.joints_pos
            joint_end = joint_start + CHN_JOINT_INFO_SIZE * chain_info.num_joints
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


@blender_registry.register_import_function(app_id="re5", extension="ccl", albam_asset_type="PHYSICS")
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


@blender_registry.register_import_function(app_id="re5", extension="chn", albam_asset_type="PHYSICS")
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
