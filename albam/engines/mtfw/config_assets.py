import bpy
import io
import struct
import zlib
import xml.etree.ElementTree as ET
from collections import defaultdict
from kaitaistruct import KaitaiStream
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile

from ...lib.kaitai_utils import check_recursive
from ...lib.mt_classes import (
    DTI_HASHES,
    MtPropertyType,
    MtPropertyTypeRE5,
    RV_DTI_HASHES,
    RV_MtPropertyType,
    RV_MTPROPERTY_RE5,
)
from ...lib import mt_types as mt
from .structs.xfs import Xfs
from .structs.sdl_156 import Sdl156

TRACK_TYPE = {
    "TYPE_UNKNOWN": 0,
    "TYPE_ROOT": 1,
    "TYPE_UNIT": 2,
    "TYPE_SYSTEM": 3,
    "TYPE_SCHEDULER": 4,
    "TYPE_OBJECT": 5,
    "TYPE_INT": 6,
    "TYPE_VECTOR": 7,
    "TYPE_FLOAT": 8,
    "TYPE_BOOL": 9,
    "TYPE_REF": 10,
    "TYPE_RESOURCE": 11,
    "TYPE_STRING": 12,
    "TYPE_EVENT": 13,
    "TYPE_MATRIX": 14,
}

RV_TRACK_TYPE = {v: k for k, v in TRACK_TYPE.items()}
SDL_ROOT_TRACK_TYPES = {
    TRACK_TYPE["TYPE_ROOT"],
    TRACK_TYPE["TYPE_UNIT"],
    TRACK_TYPE["TYPE_SYSTEM"],
    TRACK_TYPE["TYPE_SCHEDULER"],
}
SDL_MOVE_LINE_TRACK_TYPES = {
    TRACK_TYPE["TYPE_UNIT"],
    TRACK_TYPE["TYPE_SCHEDULER"],
}

SDL_VAL_TYPES = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 24, 28}
SDL_DATA_STRUCT_SIZES = {   # Straid
    "TYPE_CLASSREF": 4,
    "TYPE_BOOL": 4,  # multiple of four but 1 byte in array
    "TYPE_U8": 4,
    "TYPE_U16": 4,
    "TYPE_U32": 4,
    "TYPE_U64": 8,
    "TYPE_S8": 4,
    "TYPE_S16": 4,
    "TYPE_S32": 4,
    "TYPE_S64": 8,
    "TYPE_F32": 4,
    "TYPE_F64": 8,
    "TYPE_STRING": 4,
    "TYPE_COLOR": 16,
    "TYPE_VECTOR3": 16,
    "TYPE_VECTOR4": 16,
    "TYPE_QUATERNION": 16,
    "TYPE_EVENT": 4,
    "TYPE_EVENT32": 4,
    "TYPE_FLOAT2": 16,
    "TYPE_FLOAT3": 16,
    "TYPE_FLOAT4": 16,
    "TYPE_EASECURVE": 16,
    "TYPE_RANGEF": 16,
    "TYPE_HERMITECURVE": 64,
    "TYPE_CUSTOM": 4,
}


def _sdl_data_struct_size(prop_type):
    prop_type_name = RV_MTPROPERTY_RE5.get(prop_type)
    return SDL_DATA_STRUCT_SIZES.get(prop_type_name)


def _append_sdl_value_xml(parent_xml, value):
    for field_name, field_value in vars(value).items():
        if field_name.startswith("_") or field_name == "padding" or field_value is None:
            continue

        field_xml = ET.SubElement(parent_xml, field_name)
        if isinstance(field_value, (str, int, float, bool)):
            field_xml.text = str(field_value)
        else:
            _append_sdl_value_xml(field_xml, field_value)


@blender_registry.register_import_function(app_id="re5", extension="sdl", albam_asset_type="CONFIG")
def build_sheduler_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    assert app_id == "re5", "Currently only Resident Evil 5 is supported"
    sdl_bytes = vfile.get_bytes()
    sdl = Sdl156.from_bytes(sdl_bytes)
    sdl._read()
    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(name=bl_object_name, object_data=None)

    xml = _sdl_to_xml(sdl)
    ET.indent(xml, space="\t", level=0)
    buffer = io.StringIO()
    xml.write(buffer, encoding="unicode", xml_declaration=True)
    xml_string = buffer.getvalue()
    text = bpy.data.texts.new(bl_object_name + ".xml")
    bl_object["sdl"] = text.name
    text.from_string(xml_string)

    return bl_object


def _sdl_to_xml(sdl):
    root_xml = ET.Element("sdl")
    header_xml = ET.SubElement(root_xml, "header")

    ET.SubElement(header_xml, "version").text = str(sdl.header.version)
    ET.SubElement(header_xml, "frame_max").text = str(
        getattr(sdl.header, "frame_max", getattr(sdl.header, "frames", 0))
    )
    ET.SubElement(header_xml, "floor_frame").text = str(
        getattr(sdl.header, "floor_frame", 0)
    )
    ET.SubElement(header_xml, "reserved").text = str(getattr(sdl.header, "reserved", 0))

    tracks_xml = ET.SubElement(root_xml, "tracks")

    elements = []
    for track_id, track in enumerate(sdl.tracks):
        track_attributes = {
            "name": track.name,
            "index": str(track_id),
            "prop_type": _sdl_prop_type_name(getattr(track, "prop_type", 0)),
            "dti_ref": str(getattr(track, "dti_ref", 0)),
        }
        if track.track_type in SDL_MOVE_LINE_TRACK_TYPES:
            track_attributes["move_line"] = str(track.parent)
        track_el = ET.Element(
            RV_TRACK_TYPE.get(track.track_type, "TYPE_UNKNOWN"), track_attributes
        )
        if track.num_frames > 0:
            data_xml = ET.SubElement(track_el, "data")
            data = track.data or []
            timing_frames = track.timing_frames or []
            for frame_id in range(track.num_frames):
                timing_frame = timing_frames[frame_id]
                item_xml = ET.SubElement(
                    data_xml,
                    RV_MTPROPERTY_RE5.get(track.prop_type, "TYPE_UNKNOWN"),
                    {
                        "frame": str(timing_frame.frame),
                        "type": str(timing_frame.type),
                    },
                )
                if frame_id >= len(data):
                    continue

                value = data[frame_id]
                if track.prop_type == 57:
                    for field_name in ("x", "y"):
                        field_xml = ET.SubElement(item_xml, field_name)
                        for field_value in getattr(value, field_name):
                            ET.SubElement(field_xml, "value").text = str(field_value)
                elif track.prop_type in SDL_VAL_TYPES:
                    item_xml.set("value", str(getattr(value, "val", value)))
                elif track.track_type == TRACK_TYPE["TYPE_VECTOR"]:
                    _append_sdl_value_xml(item_xml, value)
                elif track.track_type == TRACK_TYPE["TYPE_RESOURCE"] and value.ref_ofs:
                    item_xml.set("ref_path", value.ref_path)
                    item_xml.set(
                        "ref_dti",
                        RV_DTI_HASHES.get(value.ref_dti, str(value.ref_dti)),
                    )
                elif track.prop_type == 14:
                    item_xml.set("string", value.string or "")

        elements.append(track_el)

    for track_id, track in enumerate(sdl.tracks):
        # Tracks 1..4 are always roots in the XML tree. UNIT and SCHEDULER
        # encode move_line in the binary `parent` field; nested property tracks
        # use it as an absolute track-table index.
        parent_id = None if track.track_type in SDL_ROOT_TRACK_TYPES else track.parent
        if parent_id is not None and 0 <= parent_id < len(elements) and parent_id != track_id:
            elements[parent_id].append(elements[track_id])
        else:
            tracks_xml.append(elements[track_id])

    tree = ET.ElementTree(root_xml)
    return tree


@blender_registry.register_export_function(app_id="re5", extension="sdl")
def export_sdl(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    xml_name = bl_obj.get("sdl", None)
    if not xml_name:
        return []

    xml_text = bpy.data.texts.get(xml_name)
    if xml_text is None:
        raise ValueError(f'SDL XML text "{xml_name}" is missing')

    sdl_bytes = _xml_to_sdl_bytes(ET.fromstring(xml_text.as_string()))
    return [VirtualFileData(app_id, asset.relative_path, data_bytes=sdl_bytes)]


def _xml_int(element, name, default=None):
    value = element.get(name)
    if value is None:
        child = element.find(name)
        if child is not None:
            value = child.text
    if value is None:
        if default is None:
            raise ValueError(f'Missing required "{name}" on <{element.tag}>')
        return default
    if isinstance(value, str) and value.lower() in ("true", "false"):
        return int(value.lower() == "true")
    return int(value, 0)


def _xml_value(item, field="val"):
    value = item.get(field)
    if value is not None:
        return value
    child = item.find(field)
    if child is not None and child.text is not None:
        return child.text
    if item.text is not None:
        return item.text
    raise ValueError(f'Missing "{field}" value on <{item.tag}>')


def _xml_float_array(item, field, length):
    field_xml = item.find(field)
    if field_xml is None:
        raise ValueError(f'Missing "{field}" values on <{item.tag}>')
    value_xml = field_xml.findall("value")
    if len(value_xml) != length:
        raise ValueError(
            f'Expected {length} values for "{field}" on <{item.tag}>, '
            f"got {len(value_xml)}"
        )
    try:
        return [float(value.text) for value in value_xml]
    except (TypeError, ValueError) as error:
        raise ValueError(f'Invalid float in "{field}" values on <{item.tag}>') from error


def _sdl_int_value(value):
    try:
        return int(value, 0)
    except ValueError:
        return int(value)


def _sdl_prop_type_name(prop_type):
    return RV_MTPROPERTY_RE5.get(prop_type, str(prop_type))


def _sdl_prop_type_value(value):
    if value in MtPropertyTypeRE5:
        return MtPropertyTypeRE5[value]
    return _sdl_int_value(value)


def _sdl_dti_value(value):
    dti = DTI_HASHES.get(value)
    return dti if dti is not None else _sdl_int_value(value)


def _sdl_data_value(prop_type, item, stream, sdl, track, value_offset):
    if prop_type in SDL_VAL_TYPES:
        value = _xml_value(item, "value")
        if prop_type in (12, 13):
            value = float(value)
        else:
            value = _sdl_int_value(value)
        if prop_type in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 24, 28):
            classes = {
                2: Sdl156.Classref,
                3: Sdl156.Bool,
                4: Sdl156.U8Value,
                5: Sdl156.U16,
                6: Sdl156.U32,
                7: Sdl156.U64,
                8: Sdl156.S8Value,
                9: Sdl156.S16,
                10: Sdl156.S32,
                11: Sdl156.S64,
                12: Sdl156.F32,
                13: Sdl156.F64,
                24: Sdl156.Event,
                28: Sdl156.Event32
            }
            data_value = classes[prop_type](stream, track, sdl)
            data_value.val = value
            return data_value
        return value

    if prop_type == 14:
        data_value = Sdl156.MtStr(stream, track, sdl)
        data_value.ptr = value_offset
        data_value.string = item.get("string", "")
        return data_value

    fields_by_type = {
        15: ("r", "g", "b", "a"),
        20: ("x", "y", "z"),
        21: ("x", "y", "z", "w"),
        22: ("x", "y", "z", "w"),
        34: ("x", "y"),
        35: ("x", "y", "z"),
        36: ("x", "y", "z", "w"),
        40: ("p1", "p2"),
        55: ("s", "r"),
    }
    classes = {
        15: Sdl156.Color,
        20: Sdl156.Vec3,
        21: Sdl156.Vec4,
        22: Sdl156.Quaternion,
        34: Sdl156.Float2,
        35: Sdl156.Float3,
        36: Sdl156.Float4,
        40: Sdl156.MtEasecurve,
        55: Sdl156.Rangef,
    }
    if prop_type == 57:
        data_value = Sdl156.Hermitecurve(stream, track, sdl)
        data_value.x = _xml_float_array(item, "x", 8)
        data_value.y = _xml_float_array(item, "y", 8)
        return data_value

    if prop_type in classes:
        data_value = classes[prop_type](stream, track, sdl)
        for field in fields_by_type[prop_type]:
            setattr(data_value, field, float(_xml_value(item, field)))
        return data_value

    if prop_type == 58:
        data_value = Sdl156.Resource(stream, track, sdl)
        path = item.get("ref_path")
        dti = item.get("ref_dti")
        if path is None and dti is None:
            data_value.ref_ofs = 0
        else:
            data_value.ref_ofs = value_offset
            data_value.ref_dti = _sdl_dti_value(dti or "0")
            data_value.ref_path = path or ""
        return data_value

    raise ValueError(f"Unsupported SDL property type {prop_type}")


def _parse_sdl_xml_document(root_xml):
    if root_xml.tag != "sdl":
        raise ValueError('SDL XML root must be <sdl>')
    header_xml = root_xml.find("header")
    tracks_xml = root_xml.find("tracks")
    if header_xml is None or tracks_xml is None:
        raise ValueError('SDL XML must contain <header> and <tracks>')

    header = {
        "version": _xml_int(header_xml, "version", 17),
        "frame_max": _xml_int(header_xml, "frame_max", 0),
        "floor_frame": _xml_int(header_xml, "floor_frame", 0),
        "reserved": _xml_int(header_xml, "reserved", 0),
    }
    if not 0 <= header["frame_max"] <= 0xFFFFFF:
        raise ValueError("SDL frame_max must fit in 24 bits")
    if header["floor_frame"] not in (0, 1):
        raise ValueError("SDL floor_frame must be 0 or 1")
    if not 0 <= header["reserved"] <= 0x7F:
        raise ValueError("SDL reserved must fit in 7 bits")
    return header, tracks_xml


def _collect_sdl_track_elements(tracks_xml):
    track_elements = []

    def collect_entries(element, structural_parent=None):
        for child in element:
            if child.tag == "data":
                continue
            if child.tag == "TYPE_UNKNOWN":
                raise ValueError("Cannot export an SDL track with unknown track type")
            if child.tag not in TRACK_TYPE:
                raise ValueError(f"Unknown element <{child.tag}> in SDL tracks")
            track_elements.append((child, structural_parent))
            collect_entries(child, child)

    collect_entries(tracks_xml)

    indexed = [element.get("index") is not None for element, _ in track_elements]
    if any(indexed) and not all(indexed):
        raise ValueError("SDL track index must be specified for every track or none")
    if all(indexed):
        track_elements.sort(key=lambda pair: _xml_int(pair[0], "index"))
        indices = [_xml_int(element, "index") for element, _ in track_elements]
        if indices != list(range(len(track_elements))):
            raise ValueError("SDL track indices must be unique and contiguous from zero")
    if not track_elements or track_elements[0][0].tag != "TYPE_ROOT":
        raise ValueError("SDL XML tracks must start with a TYPE_ROOT track")

    track_index_by_element = {
        id(element): track_index
        for track_index, (element, _) in enumerate(track_elements)
    }
    return track_elements, track_index_by_element


def _sdl_parent_from_xml(
    element, track_type, structural_parent, track_index, track_count,
    track_index_by_element,
):
    if track_type in SDL_MOVE_LINE_TRACK_TYPES:
        # Older generated XML used parent for this value. Keep accepting it
        # when move_line is absent so existing Blender text blocks remain exportable.
        move_line = element.get("move_line")
        if move_line is None:
            move_line = element.get("parent", "0")
        parent = _sdl_int_value(move_line)
        if not (0 <= parent <= 31 or parent == 0x3F):
            raise ValueError(f"SDL move_line on <{element.tag}> must be 0..31 or 63")
    elif track_type in SDL_ROOT_TRACK_TYPES:
        parent = 0
    elif element.get("parent") is not None:
        # Preserve explicit parent fields from XML created by earlier versions;
        # new XML expresses the same link by nesting.
        parent = _sdl_int_value(element.get("parent"))
    else:
        parent = (
            track_index_by_element[id(structural_parent)]
            if structural_parent is not None
            else 0
        )

    if not 0 <= parent <= 0xFFFFFFFF:
        raise ValueError(f"SDL parent value is outside its binary range: {parent}")
    if (
        track_type not in SDL_ROOT_TRACK_TYPES
        and track_type not in SDL_MOVE_LINE_TRACK_TYPES
        and (parent >= track_count or parent == track_index)
    ):
        raise ValueError(f"SDL parent index {parent} is invalid for track {track_index}")
    return parent


def _parse_sdl_track_entry(
    element, structural_parent, track_index, track_count, track_index_by_element,
):
    track_type = TRACK_TYPE[element.tag]
    data_xml = element.find("data")
    data_entry = list(data_xml) if data_xml is not None else []

    prop_type_attr = element.get("prop_type")
    if prop_type_attr is None:
        prop_type = next(
            (
                value
                for value, name in RV_MTPROPERTY_RE5.items()
                if data_entry and name == data_entry[0].tag
            ),
            0,
        )
    else:
        prop_type = _sdl_prop_type_value(prop_type_attr)
    if data_entry and any(
        item.tag != RV_MTPROPERTY_RE5.get(prop_type) for item in data_entry
    ):
        raise ValueError(
            f"Inconsistent property type on SDL track {element.get('name', '')!r}"
        )
    if len(data_entry) > 0xFFFF:
        raise ValueError("SDL tracks cannot contain more than 65535 frames")

    name = element.get("name", "")
    if "\0" in name:
        raise ValueError("SDL track names cannot contain NUL characters")
    parent = _sdl_parent_from_xml(
        element,
        track_type,
        structural_parent,
        track_index,
        track_count,
        track_index_by_element,
    )
    track = {
        "type": track_type,
        "prop_type": prop_type,
        "count": len(data_entry),
        "parent": parent,
        "name": name,
        "dti_ref": _sdl_dti_value(element.get("dti_ref", "0")),
    }
    return track, data_entry


def _parse_sdl_track_entries(track_elements, track_index_by_element):
    track_count = len(track_elements)
    tracks = []
    track_data = []
    for track_index, (element, structural_parent) in enumerate(track_elements):
        track, data_entry = _parse_sdl_track_entry(
            element,
            structural_parent,
            track_index,
            track_count,
            track_index_by_element,
        )
        tracks.append(track)
        track_data.append(data_entry)
    return tracks, track_data


def _calculate_sdl_layout(tracks, track_data):
    header_size = 20
    tracks_size = len(tracks) * 24
    cur_track_data = header_size + tracks_size
    for track, data_entry in zip(tracks, track_data):
        track["timing_offset"] = cur_track_data if data_entry else 0
        cur_track_data += len(data_entry) * 4
        data_struct_size = _sdl_data_struct_size(track["prop_type"])
        has_serialized_data = (
            data_entry
            and track["type"] > TRACK_TYPE["TYPE_OBJECT"]
            and data_struct_size is not None
        )
        if has_serialized_data:
            cur_track_data += (-cur_track_data) % 16
        track["data_offset"] = cur_track_data if has_serialized_data else 0
        if track["data_offset"]:
            if track["prop_type"] == 3:
                cur_track_data += (len(data_entry) + 3) // 4 * 4
            else:
                cur_track_data += len(data_entry) * data_struct_size
    cur_track_data += (-cur_track_data) % 4

    name_offsets = {}
    cur_names = 0
    for track in tracks:
        name = track["name"]
        if name not in name_offsets:
            name_offsets[name] = cur_names
            cur_names += len(name.encode("utf-8")) + 1

    custom_data_offset = cur_names
    for track, data_entry in zip(tracks, track_data):
        for item in data_entry:
            if track["prop_type"] == 14:
                value = item.get("string", "")
                if "\0" in value:
                    raise ValueError("SDL strings cannot contain NUL characters")
                cur_names += len(value.encode("utf-8")) + 1
            elif track["prop_type"] == 58 and (
                item.get("ref_path") is not None or item.get("ref_dti") is not None
            ):
                path = item.get("ref_path", "")
                if "\0" in path:
                    raise ValueError("SDL resource paths cannot contain NUL characters")
                cur_names += 4 + len(path.encode("utf-8")) + 1

    return {
        "ofs_names": cur_track_data,
        "custom_data_offset": custom_data_offset,
        "final_size": cur_track_data + cur_names,
        "name_offsets": name_offsets,
    }


def _write_sdl_bytes(header_values, tracks, track_data, layout):
    stream = KaitaiStream(io.BytesIO(bytearray(layout["final_size"])))
    sdl = Sdl156(stream)
    header = Sdl156.BaseHeader(stream, sdl, sdl)
    header.magic = b"SDL\0"
    header.version = header_values["version"]
    header.num_tracks = len(tracks)
    header.frame_max = header_values["frame_max"]
    header.floor_frame = bool(header_values["floor_frame"])
    header.reserved = header_values["reserved"]
    header.ofs_dti_table = 0
    header.ofs_names = layout["ofs_names"]
    sdl.header = header

    generated_tracks = []
    cur_names = layout["custom_data_offset"]
    for track, data_entry in zip(tracks, track_data):
        dst_track = Sdl156.Track(stream, sdl, sdl)
        dst_track.track_type = track["type"]
        dst_track.prop_type = track["prop_type"]
        dst_track.num_frames = track["count"]
        dst_track.parent = track["parent"]
        dst_track.ofs_name = layout["name_offsets"][track["name"]]
        dst_track.dti_ref = track["dti_ref"]
        dst_track.ofs_timing = track["timing_offset"]
        dst_track.ofs_data = track["data_offset"]

        timing_frames = []
        data_values = []
        for item_index, item in enumerate(data_entry):
            frame = _xml_int(item, "frame", 0)
            frame_type = _xml_int(item, "type", 0)
            if not 0 <= frame <= 0xFFFFFF or not 0 <= frame_type <= 0xFF:
                raise ValueError("SDL timing frame/type is outside its binary range")
            timing = Sdl156.TimingFrame(stream, dst_track, sdl)
            timing.frame = frame
            timing.type = frame_type
            timing_frames.append(timing)

            data_struct_size = _sdl_data_struct_size(track["prop_type"])
            if track["type"] > TRACK_TYPE["TYPE_OBJECT"] and data_struct_size is not None:
                value_offset = track["data_offset"] + item_index * data_struct_size
                if track["prop_type"] == 14:
                    value_offset = cur_names
                elif track["prop_type"] == 58 and (
                    item.get("ref_path") is not None or item.get("ref_dti") is not None
                ):
                    value_offset = cur_names
                data_values.append(
                    _sdl_data_value(
                        track["prop_type"],
                        item,
                        stream,
                        sdl,
                        dst_track,
                        value_offset,
                    )
                )
            if track["prop_type"] == 14:
                cur_names += len(item.get("string", "").encode("utf-8")) + 1
            elif track["prop_type"] == 58 and (
                item.get("ref_path") is not None or item.get("ref_dti") is not None
            ):
                cur_names += 4 + len(item.get("ref_path", "").encode("utf-8")) + 1

        dst_track.name = track["name"]
        dst_track.timing_frames = timing_frames
        dst_track.data = data_values
        generated_tracks.append(dst_track)

    sdl.tracks = generated_tracks
    check_recursive(sdl)
    sdl._write(stream)
    return stream.to_byte_array()


def _xml_to_sdl_bytes(root_xml):
    header_values, tracks_xml = _parse_sdl_xml_document(root_xml)
    track_elements, track_index_by_element = _collect_sdl_track_elements(tracks_xml)
    tracks, track_data = _parse_sdl_track_entries(
        track_elements, track_index_by_element
    )
    layout = _calculate_sdl_layout(tracks, track_data)
    return _write_sdl_bytes(header_values, tracks, track_data, layout)



@blender_registry.register_import_function(app_id="re5", extension="lot", albam_asset_type="CONFIG")
def build_xfs_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    assert app_id == "re5", "Currently only Resident Evil 5 is supported"
    xfs_bytes = vfile.get_bytes()
    xfs = Xfs.from_bytes(xfs_bytes)
    xfs._read()
    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(name=bl_object_name, object_data=None)

    xml = from_xfs(xfs, "lot")
    ET.indent(xml, space="\t", level=0)
    buffer = io.StringIO()
    xml.write(buffer, encoding="unicode", xml_declaration=True)
    xml_string = buffer.getvalue()
    text = bpy.data.texts.new(bl_object_name + ".xml")
    bl_object["lot"] = bl_object_name + ".xml"
    text.from_string(xml_string)

    return bl_object


@blender_registry.register_export_function(app_id="re5", extension="lot")
def export_lot(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    xml_name = bl_obj.get("lot", None)
    if not xml_name:
        return []

    xml_text = bpy.data.texts.get(xml_name)
    if xml_text is None:
        raise ValueError(f'LOT XML text "{xml_name}" is missing')

    xfs_bytes = to_xfs(ET.fromstring(xml_text.as_string()))
    return [VirtualFileData(app_id, asset.relative_path, data_bytes=xfs_bytes)]


# XFS XML conversion helpers.
def from_xfs(xml, extension):
    root = ET.Element(
        'root',
        attrib={
            'extension': extension,
            'version_major': str(xml.header.version_major),
            'version_minor': str(xml.header.version_minor),
        },
    )

    if xml.data.num_roots != 1:
        raise ValueError(f'Expected one XFS root object, got {xml.data.num_roots}')

    def append_class(body, class_index, parent, object_index=None):
        class_def = xml.class_defs[class_index]
        class_name = RV_DTI_HASHES.get(class_def.type_hash, str(hex(class_def.type_hash)))
        class_attrib = {
            'name': class_name,
            'class_index': str(class_index),
        }
        if object_index is not None:
            class_attrib['object_index'] = str(object_index)
        class_xml = ET.SubElement(parent, 'class', attrib=class_attrib)

        for property_values in body.properties:
            prop = property_values.property
            prop_type = int(prop.type)
            prop_attrib = {
                'type': RV_MtPropertyType.get(prop_type, f'TYPE_UNKNOWN_{prop_type}'),
                'name': prop.name,
                'size': str(prop.size),
                'flags': str(prop.flags),
                'reserved': prop.reserved.hex(),
            }

            if prop_type in (1, 2):
                prop_xml = ET.SubElement(class_xml, 'classref', attrib=prop_attrib)
                for value in property_values.values:
                    if value.is_null:
                        ET.SubElement(
                            prop_xml,
                            'class',
                            attrib={
                                'name': 'null',
                                'reference_kind': 'null',
                            },
                        )
                    elif value.is_inline:
                        append_class(
                            value.body,
                            value.class_index,
                            prop_xml,
                            object_index=value.index,
                        )
                    else:
                        reference_class = xml.class_defs[value.class_index]
                        reference_name = RV_DTI_HASHES.get(
                            reference_class.type_hash,
                            str(hex(reference_class.type_hash)),
                        )
                        ET.SubElement(
                            prop_xml,
                            'class',
                            attrib={
                                'name': reference_name,
                                'class_index': str(value.class_index),
                                'reference_index': str(value.index),
                            },
                        )
            elif prop_type == int(Xfs.PropertyType.string):
                prop_xml = ET.SubElement(class_xml, 'string', attrib=prop_attrib)
                for value in property_values.values:
                    ET.SubElement(prop_xml, 'item', attrib={'val': value.value})
            elif prop_type == int(Xfs.PropertyType.resource):
                prop_xml = ET.SubElement(class_xml, 'resource', attrib=prop_attrib)
                for value in property_values.values:
                    ET.SubElement(prop_xml, 'item', attrib={'val': value.class_name})
                    ET.SubElement(prop_xml, 'item', attrib={'val': value.path})
            elif prop_type in mt.type_to_class:
                prop_xml = ET.SubElement(class_xml, 'vector', attrib=prop_attrib)
                for value in property_values.values:
                    vec_xml = ET.SubElement(prop_xml, 'vec')
                    if len(value.value) % 4:
                        raise ValueError(
                            f'XFS vector property {prop.name!r} has a value size '
                            f'of {len(value.value)} bytes, not divisible by 4'
                        )
                    for offset in range(0, len(value.value), 4):
                        component = struct.unpack_from('<f', value.value, offset)[0]
                        ET.SubElement(vec_xml, 'item', attrib={'val': str(component)})
            else:
                prop_xml = ET.SubElement(class_xml, 'scalar', attrib=prop_attrib)
                scalar_reader = mt.scalar_type_map.get(prop_type)
                for value in property_values.values:
                    if scalar_reader is None:
                        scalar_value = value.value.hex()
                    else:
                        scalar_value = str(
                            scalar_reader(KaitaiStream(io.BytesIO(value.value)))
                        )
                    ET.SubElement(prop_xml, 'item', attrib={'val': scalar_value})

    # The XFS root body is stored directly in the data section, outside the
    # object-reference index sequence.
    append_class(xml.data.root, 0, root)

    # Preserve class definitions that have no instantiated object in the XML
    # tree, along with the metadata needed to rebuild the class table exactly.
    metadata_xml = ET.SubElement(root, '_xfs_metadata')
    for class_index, class_def in enumerate(xml.class_defs):
        class_name = RV_DTI_HASHES.get(class_def.type_hash, str(hex(class_def.type_hash)))
        class_xml = ET.SubElement(
            metadata_xml,
            'class_def',
            attrib={
                'index': str(class_index),
                'name': class_name,
                'type_hash': str(class_def.type_hash),
            },
        )
        for prop in class_def.properties:
            ET.SubElement(
                class_xml,
                'property',
                attrib={
                    'name': prop.name,
                    'type_id': str(int(prop.type)),
                    'flags': str(prop.flags),
                    'size': str(prop.size),
                    'reserved': prop.reserved.hex(),
                },
            )

    tree = ET.ElementTree(root)
    return tree


def to_xfs(xml):
    """Serialize XFS XML using the class-definition/data-section schema."""
    if isinstance(xml, ET.ElementTree):
        xml = xml.getroot()
    if xml.tag != 'root':
        raise ValueError('XFS XML root must be <root>')

    root_classes = [child for child in xml if child.tag == 'class']
    if len(root_classes) != 1:
        raise ValueError(f'XFS XML must contain one root <class>, got {len(root_classes)}')
    root_class = root_classes[0]

    def parse_int(value):
        try:
            return int(value, 0)
        except ValueError:
            return int(value, 10)

    metadata_xml = xml.find('_xfs_metadata')
    class_defs = {}
    class_indexes_by_name = defaultdict(list)
    if metadata_xml is not None:
        for class_xml in metadata_xml.findall('class_def'):
            class_index = parse_int(class_xml.attrib['index'])
            class_name = class_xml.attrib['name']
            props = []
            for prop_xml in class_xml.findall('property'):
                reserved = bytes.fromhex(prop_xml.attrib.get('reserved', ''))
                if len(reserved) != 16:
                    raise ValueError(
                        f'XFS property {prop_xml.attrib.get("name")!r} '
                        'reserved field must be 16 bytes'
                    )
                props.append({
                    'name': prop_xml.attrib['name'],
                    'type_id': parse_int(prop_xml.attrib['type_id']),
                    'flags': parse_int(prop_xml.attrib.get('flags', '0')),
                    'size': parse_int(prop_xml.attrib['size']),
                    'reserved': reserved,
                })
            class_defs[class_index] = {
                'name': class_name,
                'type_hash': parse_int(class_xml.attrib['type_hash']),
                'properties': props,
            }
            class_indexes_by_name[class_name].append(class_index)

    def class_index_for_node(class_xml, create=False):
        if class_xml.attrib.get('name') == 'null':
            return None
        class_index_attr = class_xml.attrib.get('class_index')
        if class_index_attr is not None:
            class_index = parse_int(class_index_attr)
            if class_index not in class_defs and not create:
                raise ValueError(
                    f'XFS class {class_xml.attrib.get("name")!r} uses missing '
                    f'class index {class_index}'
                )
            return class_index

        class_name = class_xml.attrib['name']
        if class_indexes_by_name[class_name]:
            return class_indexes_by_name[class_name][0]
        if not create:
            raise ValueError(f'Unknown XFS class {class_name!r}')
        class_index = max(class_defs, default=-1) + 1
        class_indexes_by_name[class_name].append(class_index)
        return class_index

    def parse_property_type(prop_xml, old_prop=None):
        type_name = prop_xml.attrib.get('type')
        if type_name is None and old_prop is not None:
            return old_prop['type_id']
        try:
            return int(MtPropertyType[type_name])
        except (KeyError, TypeError):
            if type_name:
                try:
                    return parse_int(type_name)
                except ValueError:
                    pass
            if type_name and type_name.startswith('TYPE_UNKNOWN_'):
                try:
                    return parse_int(type_name[len('TYPE_UNKNOWN_'):])
                except ValueError:
                    pass
        raise ValueError(f'Unknown XFS property type {type_name!r}')

    fixed_property_sizes = {
        1: 4, 2: 4, 3: 1, 4: 1, 5: 2, 6: 4,
        8: 1, 9: 2, 10: 4, 12: 4, 14: 4, 15: 4,
        16: 8, 18: 16, 19: 64, 20: 16, 21: 16, 22: 16,
        36: 16, 47: 32, 54: 8, 55: 8, 57: 64, 58: 4,
    }

    def parse_property_def(prop_xml, old_prop=None):
        type_id = parse_property_type(prop_xml, old_prop)
        size_text = prop_xml.attrib.get('size')
        if size_text is not None:
            size = parse_int(size_text)
        elif old_prop is not None:
            size = old_prop['size']
        else:
            size = fixed_property_sizes.get(type_id, mt.scalar_bytes_num.get(type_id))
            if size is None and type_id in mt.type_to_class:
                vectors = prop_xml.findall('vec')
                size = len(vectors[0].findall('item')) * 4 if vectors else None
            if size is None:
                values = prop_xml.findall('item')
                if values:
                    try:
                        size = len(bytes.fromhex(values[0].attrib['val']))
                    except (KeyError, ValueError):
                        size = None
        if size is None:
            raise ValueError(
                f'Cannot determine XFS property size for {prop_xml.attrib.get("name")!r}'
            )

        if old_prop is not None:
            default_flags = old_prop['flags']
            default_reserved = old_prop['reserved']
        else:
            default_flags = 0
            default_reserved = bytes(16)
        flags_text = prop_xml.attrib.get('flags')
        flags = parse_int(flags_text) if flags_text is not None else default_flags
        reserved_text = prop_xml.attrib.get('reserved')
        reserved = bytes.fromhex(reserved_text) if reserved_text is not None else default_reserved
        if len(reserved) != 16:
            raise ValueError(
                f'XFS property {prop_xml.attrib.get("name")!r} reserved field must be 16 bytes'
            )
        return {
            'name': prop_xml.attrib.get('name', old_prop['name'] if old_prop else ''),
            'type_id': type_id,
            'flags': flags,
            'size': size,
            'reserved': reserved,
        }

    def hash_for_class(class_name):
        if class_name in DTI_HASHES:
            return DTI_HASHES[class_name]
        try:
            return parse_int(class_name)
        except ValueError:
            try:
                encoded = class_name.encode('ascii')
            except UnicodeEncodeError as error:
                raise ValueError(f'XFS class name {class_name!r} must be ASCII') from error
            return (~zlib.crc32(encoded)) & 0x7FFFFFFF

    seen_instance_defs = set()

    def collect_inline_classes(class_xml):
        class_index = class_index_for_node(class_xml, create=True)
        class_name = class_xml.attrib['name']
        old_def = class_defs.get(class_index)
        old_props = old_def['properties'] if old_def is not None else []
        property_nodes = list(class_xml)
        props = [
            parse_property_def(
                prop_xml,
                old_props[i] if i < len(old_props) else None,
            )
            for i, prop_xml in enumerate(property_nodes)
        ]

        if class_index in seen_instance_defs:
            current = class_defs[class_index]
            current_signature = [
                (p['name'], p['type_id'], p['flags'], p['size'], p['reserved'])
                for p in current['properties']
            ]
            new_signature = [
                (p['name'], p['type_id'], p['flags'], p['size'], p['reserved'])
                for p in props
            ]
            if current_signature != new_signature:
                raise ValueError(
                    f'Inconsistent property definitions for XFS class {class_name!r}'
                )
        else:
            if old_def is None:
                class_defs[class_index] = {
                    'name': class_name,
                    'type_hash': hash_for_class(class_name),
                    'properties': props,
                }
                if class_index not in class_indexes_by_name[class_name]:
                    class_indexes_by_name[class_name].append(class_index)
            else:
                old_def['name'] = class_name
                old_def['properties'] = props
            seen_instance_defs.add(class_index)

        for prop_xml in property_nodes:
            for value_xml in prop_xml.findall('class'):
                if (
                    value_xml.attrib.get('name') != 'null'
                    and 'reference_index' not in value_xml.attrib
                ):
                    collect_inline_classes(value_xml)

    collect_inline_classes(root_class)
    if class_index_for_node(root_class) != 0:
        raise ValueError('The root XFS object must use class index 0')

    if not class_defs:
        raise ValueError('XFS XML does not define any classes')
    class_count = max(class_defs) + 1
    if set(class_defs) != set(range(class_count)):
        raise ValueError('XFS class indexes must be contiguous from zero')
    if class_count > 0x7FFF:
        raise ValueError('XFS class count exceeds the object-reference tag capacity')

    def pack_uint(value, bits, label):
        limit = (1 << bits) - 1
        if not 0 <= value <= limit:
            raise ValueError(f'{label} {value} does not fit in {bits} bits')
        return value.to_bytes(bits // 8, 'little')

    def encode_ascii(value, label):
        if '\0' in value:
            raise ValueError(f'XFS {label} cannot contain NUL characters')
        try:
            return value.encode('ascii')
        except UnicodeEncodeError as error:
            raise ValueError(f'XFS {label} must be ASCII: {value!r}') from error

    def encode_terminated(value, label):
        return encode_ascii(value, label) + b'\0'

    scalar_formats = {
        3: 'B', 4: 'B', 5: 'H', 6: 'I', 7: 'Q',
        8: 'b', 9: 'h', 10: 'i', 11: 'q', 12: 'f', 13: 'd',
    }
    # The root body has no ObjectRef header, so inline object indexes start at 1.
    output_object_ids = {}
    next_object_id = 1

    def get_object_source_id(class_xml):
        value = class_xml.attrib.get('object_index')
        return parse_int(value) if value is not None else None

    def node_class_index(class_xml):
        class_index_attr = class_xml.attrib.get('class_index')
        if class_index_attr is not None:
            class_index = parse_int(class_index_attr)
        else:
            class_name = class_xml.attrib['name']
            options = class_indexes_by_name[class_name]
            if len(options) != 1:
                raise ValueError(f'Cannot resolve class index for XFS class {class_name!r}')
            class_index = options[0]
        if class_index not in class_defs:
            raise ValueError(f'XFS object uses undefined class index {class_index}')
        return class_index

    def encode_reference(class_xml):
        nonlocal next_object_id
        class_name = class_xml.attrib.get('name', '')
        if class_name == 'null' or class_xml.attrib.get('reference_kind') == 'null':
            return (
                pack_uint(0xFFFE, 16, 'null-reference tag')
                + pack_uint(0, 16, 'null-reference index')
            )

        class_index = node_class_index(class_xml)
        reference_source_id = class_xml.attrib.get('reference_index')
        if reference_source_id is not None:
            reference_source_id = parse_int(reference_source_id)
            if reference_source_id not in output_object_ids:
                raise ValueError(
                    f'XFS back-reference points to object {reference_source_id}, '
                    'which has not been serialized yet'
                )
            tag = class_index * 2
            object_index = output_object_ids[reference_source_id]
            return pack_uint(tag, 16, 'back-reference tag') + pack_uint(
                object_index, 16, 'back-reference index'
            )

        object_index = next_object_id
        next_object_id += 1
        source_id = get_object_source_id(class_xml)
        if source_id is not None:
            if source_id in output_object_ids:
                raise ValueError(f'Duplicate XFS object index {source_id}')
            output_object_ids[source_id] = object_index

        body = encode_body(class_xml, class_index)
        size = len(body) + 4
        return (
            pack_uint(class_index * 2 + 1, 16, 'inline-reference tag')
            + pack_uint(object_index, 16, 'inline-reference index')
            + pack_uint(size, 32, 'inline-reference size')
            + body
        )

    def encode_body(class_xml, class_index):
        class_def = class_defs[class_index]
        properties = list(class_xml)
        expected = class_def['properties']
        if len(properties) != len(expected):
            raise ValueError(
                f'XFS class {class_def["name"]!r} has {len(properties)} XML properties, '
                f'but its class definition has {len(expected)}'
            )

        output = bytearray()
        for prop_xml, prop_def in zip(properties, expected):
            type_id = prop_def['type_id']
            if prop_xml.attrib.get('name', '') != prop_def['name']:
                raise ValueError(
                    f'XFS property order/name mismatch in class {class_def["name"]!r}: '
                    f'{prop_xml.attrib.get("name")!r} != {prop_def["name"]!r}'
                )
            if type_id in (1, 2):
                values = prop_xml.findall('class')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                for value_xml in values:
                    output.extend(encode_reference(value_xml))
            elif type_id == int(Xfs.PropertyType.string):
                values = prop_xml.findall('item')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                for value_xml in values:
                    output.extend(encode_terminated(value_xml.attrib['val'], 'string value'))
            elif type_id == int(Xfs.PropertyType.resource):
                values = prop_xml.findall('item')
                if len(values) % 2:
                    raise ValueError(
                        f'XFS resource property {prop_def["name"]!r} must contain '
                        'class-name/path item pairs'
                    )
                output.extend(pack_uint(len(values) // 2, 32, 'property value count'))
                for i in range(0, len(values), 2):
                    output.extend(b'\x02')
                    output.extend(encode_terminated(values[i].attrib['val'], 'resource class name'))
                    output.extend(encode_terminated(values[i + 1].attrib['val'], 'resource path'))
            elif type_id in mt.type_to_class:
                values = prop_xml.findall('vec')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                for vector_xml in values:
                    vector_data = bytearray()
                    for component in vector_xml.findall('item'):
                        vector_data.extend(struct.pack('<f', float(component.attrib['val'])))
                    if len(vector_data) != prop_def['size']:
                        raise ValueError(
                            f'XFS vector property {prop_def["name"]!r} has '
                            f'{len(vector_data)} bytes per value; expected {prop_def["size"]}'
                        )
                    output.extend(vector_data)
            else:
                values = prop_xml.findall('item')
                output.extend(pack_uint(len(values), 32, 'property value count'))
                value_format = scalar_formats.get(type_id)
                for value_xml in values:
                    value_text = value_xml.attrib['val']
                    if value_format is None:
                        try:
                            raw_value = bytes.fromhex(value_text)
                        except ValueError as error:
                            raise ValueError(
                                f'Unsupported XFS scalar type {type_id} needs a hex value'
                            ) from error
                        if len(raw_value) != prop_def['size']:
                            raise ValueError(
                                f'XFS raw property {prop_def["name"]!r} has '
                                f'{len(raw_value)} bytes; expected {prop_def["size"]}'
                            )
                        output.extend(raw_value)
                    else:
                        scalar_value = (
                            float(value_text)
                            if type_id in (12, 13)
                            else parse_int(value_text)
                        )
                        try:
                            raw_value = struct.pack('<' + value_format, scalar_value)
                        except (struct.error, OverflowError) as error:
                            raise ValueError(
                                f'Invalid value {value_text!r} for XFS property '
                                f'{prop_def["name"]!r}'
                            ) from error
                        if len(raw_value) != prop_def['size']:
                            raise ValueError(
                                f'XFS property {prop_def["name"]!r} encodes to '
                                f'{len(raw_value)} bytes; expected {prop_def["size"]}'
                            )
                        output.extend(raw_value)
        return bytes(output)

    root_class_index = node_class_index(root_class)
    root_body = encode_body(root_class, root_class_index)
    data_section = (
        pack_uint(1, 32, 'XFS root count')
        + pack_uint(len(root_body) + 4, 32, 'XFS data-section size')
        + root_body
    )

    name_table = bytearray()
    name_offsets = {}
    for class_index in range(class_count):
        for prop in class_defs[class_index]['properties']:
            prop_name = prop['name']
            if prop_name not in name_offsets:
                name_offsets[prop_name] = len(name_table)
                name_table.extend(encode_terminated(prop_name, 'property name'))

    offsets_size = class_count * 4
    class_defs_data = bytearray()
    class_def_offsets = []
    class_defs_size = sum(8 + 24 * len(class_defs[i]['properties']) for i in range(class_count))
    for class_index in range(class_count):
        class_def = class_defs[class_index]
        class_def_offsets.append(offsets_size + len(class_defs_data))
        class_defs_data.extend(pack_uint(class_def['type_hash'], 32, 'class type hash'))
        properties = class_def['properties']
        class_defs_data.extend(pack_uint(len(properties), 32, 'class property count'))
        for prop in properties:
            name_offset = offsets_size + class_defs_size + name_offsets[prop['name']]
            class_defs_data.extend(pack_uint(name_offset, 32, 'property name offset'))
            class_defs_data.extend(pack_uint(prop['type_id'], 8, 'property type'))
            class_defs_data.extend(pack_uint(prop['flags'], 8, 'property flags'))
            class_defs_data.extend(pack_uint(prop['size'], 16, 'property size'))
            class_defs_data.extend(prop['reserved'])

    extension = xml.attrib.get('extension', 'lot').lower().lstrip('.')
    extension_versions = {'fsm': 1, 'lot': 4, 'sce': 11, 'lnk': 14}
    if 'version_major' in xml.attrib:
        version_major = parse_int(xml.attrib['version_major'])
    else:
        version_major = 6
    if 'version_minor' in xml.attrib:
        version_minor = parse_int(xml.attrib['version_minor'])
    elif extension in extension_versions:
        version_minor = extension_versions[extension]
    else:
        raise ValueError(f'No XFS version is known for extension {extension!r}')

    offset_data = offsets_size + class_defs_size + len(name_table)
    header = (
        b'XFS\0'
        + pack_uint(version_major, 16, 'XFS major version')
        + pack_uint(version_minor, 16, 'XFS minor version')
        + pack_uint(class_count, 32, 'XFS class count')
        + pack_uint(offset_data, 32, 'XFS data offset')
    )
    class_def_offsets_data = b''.join(
        pack_uint(offset, 32, 'class-definition offset') for offset in class_def_offsets
    )
    return header + class_def_offsets_data + bytes(class_defs_data) + bytes(name_table) + data_section
