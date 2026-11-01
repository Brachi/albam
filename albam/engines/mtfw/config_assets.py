import bpy
import io
import struct
import zlib
import xml.etree.ElementTree as ET
from collections import defaultdict
from kaitaistruct import KaitaiStream
from mathutils import Vector
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile

from ...lib.kaitai_utils import check_recursive
from ...lib.mt_classes import (
    SDL_DTI_HASHES,
    MT_PROP_TYPES_RE5,
)
from .structs.xfs import Xfs
from .structs.sdl_156 import Sdl156
from .xfs.layout import build_xfs_lot_markers, write_xfs_lot_marker_changes

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

# SDL_DTI_HASHES stores each app's table as hash -> readable name. The reverse
# tables are used when writing names from XML back into binary SDL/XFS files.
RV_SDL_DTI_HASHES = {
    app_id: {name: dti_hash for dti_hash, name in dti_hashes.items()}
    for app_id, dti_hashes in SDL_DTI_HASHES.items()
}
RV_TRACK_TYPE = {v: k for k, v in TRACK_TYPE.items()}
RV_MT_PROP_TYPES_RE5 = {v: k for k, v in MT_PROP_TYPES_RE5.items()}


def _get_sdl_dti_hashes(app_id):
    try:
        return SDL_DTI_HASHES[app_id]
    except KeyError:
        supported_app_ids = ", ".join(sorted(SDL_DTI_HASHES))
        raise ValueError(
            f"No SDL DTI hash table for app_id {app_id!r}; "
            f"supported app_ids: {supported_app_ids}"
        ) from None


def _sdl_dti_name(value, app_id):
    return _get_sdl_dti_hashes(app_id).get(value, str(value))


SDL_TIMING_FRAME_TYPE = {
    "CONSTANT": 0,
    "OFFSET": 1,
    "TRIGGER": 2,
    "LINEAR": 3,
    "OFFSET_F": 4,
    "HERMITE": 5,
}
RV_SDL_TIMING_FRAME_TYPE = {
    value: name for name, value in SDL_TIMING_FRAME_TYPE.items()
}
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
SDL_SCALAR_CLASSES = {
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
    28: Sdl156.Event32,
}
SDL_VECTOR_CLASSES = {
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
SDL_VECTOR_FIELDS = {
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
SDL_DATA_STRIDE = {
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


XFS_EXTENSIONS = (
    "lot", "sce", "fsm", "lsp", "rvt", "seg", "smh", "lku",
    "lnk", "los", "lom", "cmi", "glp", "bmse",
)


def _sdl_data_struct_size(prop_type):
    prop_type_name = RV_MT_PROP_TYPES_RE5.get(prop_type)
    return SDL_DATA_STRIDE.get(prop_type_name)


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

    _build_sdl_infinite_lights(sdl, bl_object, app_id)

    xml = sdl_to_xml(sdl, app_id)
    ET.indent(xml, space="\t", level=0)
    buffer = io.StringIO()
    xml.write(buffer, encoding="unicode", xml_declaration=True)
    xml_string = buffer.getvalue()
    text = bpy.data.texts.new(bl_object_name + ".xml")
    bl_object["sdl"] = text.name
    text.from_string(xml_string)

    return bl_object


def _sdl_first_track_value(track):
    data = getattr(track, "data", None)
    return data[0] if getattr(track, "num_frames", 0) and data else None


def _sdl_track_vector(value, fields):
    if value is None:
        return None
    try:
        return tuple(float(getattr(value, field)) for field in fields)
    except (AttributeError, TypeError, ValueError):
        return None


def _sdl_light_properties(property_tracks):
    properties = {track.name: track for track in property_tracks}
    direction_track = properties.get("mDir")
    color_track = properties.get("mColor")
    diffuse_track = properties.get("mDiffuseFactor")
    if direction_track is None or color_track is None or diffuse_track is None:
        return None

    direction = _sdl_track_vector(
        _sdl_first_track_value(direction_track), ("x", "y", "z")
    )
    color_value = _sdl_first_track_value(color_track)
    color = _sdl_track_vector(color_value, ("r", "g", "b"))
    if color is None:
        color = _sdl_track_vector(color_value, ("x", "y", "z"))
    diffuse_value = _sdl_first_track_value(diffuse_track)
    diffuse_factor = getattr(diffuse_value, "val", None)

    if direction is None or color is None or diffuse_factor is None:
        return None
    try:
        return direction, color, float(diffuse_factor)
    except (TypeError, ValueError):
        return None


def _build_sdl_infinite_lights(sdl, parent_object, app_id):
    tracks_by_parent = defaultdict(list)
    for track in sdl.tracks:
        tracks_by_parent[track.parent].append(track)

    for track_index, track in enumerate(sdl.tracks):
        if _sdl_dti_name(getattr(track, "dti_ref", 0), app_id) != "uInfiniteLight":
            continue

        light_properties = _sdl_light_properties(tracks_by_parent.get(track_index, ()))
        if light_properties is None:
            continue
        direction, color, diffuse_factor = light_properties

        # MTFW uses Y-up coordinates; imported Blender scenes use Z-up.
        direction = Vector((direction[0], -direction[2], direction[1]))
        if direction.length_squared == 0:
            continue

        light_name = track.name or f"InfiniteLight_{track_index}"
        light_name = f"{parent_object.name}_{light_name}"
        light_data = bpy.data.lights.new(name=light_name, type="SUN")
        light_data.color = color
        light_data.energy = float(diffuse_factor)

        light_object = bpy.data.objects.new(light_name, light_data)
        light_object.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        light_object.parent = parent_object


def _dti_ref_to_value(track, app_id):
    dti_ref = getattr(track, "dti_ref", 0)
    if track.track_type in (2, 3):
        dti_ref = _sdl_dti_name(dti_ref, app_id)
    return str(dti_ref)


def sdl_to_xml(sdl, app_id):
    _get_sdl_dti_hashes(app_id)
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
            "dti_ref": _dti_ref_to_value(track, app_id),
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
                    RV_MT_PROP_TYPES_RE5.get(track.prop_type, "TYPE_UNKNOWN"),
                    {
                        "frame": str(timing_frame.frame),
                        "type": RV_SDL_TIMING_FRAME_TYPE.get(
                            timing_frame.type, str(timing_frame.type)
                        ),
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
                        _sdl_dti_name(value.ref_dti, app_id),
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

    sdl_bytes = xml_to_sdl_bytes(ET.fromstring(xml_text.as_string()), app_id)
    return [VirtualFileData(app_id, asset.relative_path, data_bytes=sdl_bytes)]


def _read_xml_int(element, name, default=None):
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


def _read_sdl_timing_frame_type(element):
    value = element.get("type")
    if value is None:
        child = element.find("type")
        value = child.text if child is not None else None
    if value is None:
        return SDL_TIMING_FRAME_TYPE["CONSTANT"]

    value_text = str(value).strip()
    type_name = value_text.upper()
    if type_name in SDL_TIMING_FRAME_TYPE:
        return SDL_TIMING_FRAME_TYPE[type_name]
    try:
        return int(value_text, 0)
    except ValueError as error:
        valid_names = ", ".join(SDL_TIMING_FRAME_TYPE)
        raise ValueError(
            f'Unknown SDL timing frame type {value!r} on <{element.tag}>; '
            f'expected one of {valid_names} or a numeric value'
        ) from error


def _read_xml_value(item, field="val"):
    value = item.get(field)
    if value is not None:
        return value
    child = item.find(field)
    if child is not None and child.text is not None:
        return child.text
    if item.text is not None:
        return item.text
    raise ValueError(f'Missing "{field}" value on <{item.tag}>')


def _read_xml_float_array(item, field, length):
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


def _sdl_value_to_int(value):
    try:
        return int(value, 0)
    except ValueError:
        return int(value)


def _sdl_prop_type_name(prop_type):
    return RV_MT_PROP_TYPES_RE5.get(prop_type, str(prop_type))


def _sdl_prop_type_value(value):
    if value in MT_PROP_TYPES_RE5:
        return MT_PROP_TYPES_RE5[value]
    return _sdl_value_to_int(value)


def _sdl_dti_value(value, app_id):
    dti = RV_SDL_DTI_HASHES[app_id].get(value)
    return dti if dti is not None else _sdl_value_to_int(value)


def _sdl_scalar_data_value(prop_type, item, stream, sdl, track):
    value = _read_xml_value(item, "value")
    if prop_type in (12, 13):
        value = float(value)
    else:
        value = _sdl_value_to_int(value)

    data_value = SDL_SCALAR_CLASSES[prop_type](stream, track, sdl)
    data_value.val = value
    return data_value


def _sdl_string_data_value(item, stream, sdl, track, value_offset):
    data_value = Sdl156.MtStr(stream, track, sdl)
    data_value.ptr = value_offset
    data_value.string = item.get("string", "")
    return data_value


def _sdl_hermite_curve_data_value(item, stream, sdl, track):
    data_value = Sdl156.Hermitecurve(stream, track, sdl)
    data_value.x = _read_xml_float_array(item, "x", 8)
    data_value.y = _read_xml_float_array(item, "y", 8)
    return data_value


def _sdl_vector_data_value(prop_type, item, stream, sdl, track):
    data_value = SDL_VECTOR_CLASSES[prop_type](stream, track, sdl)
    for field in SDL_VECTOR_FIELDS[prop_type]:
        setattr(data_value, field, float(_read_xml_value(item, field)))
    return data_value


def _sdl_resource_data_value(item, stream, sdl, track, value_offset, app_id):
    data_value = Sdl156.Resource(stream, track, sdl)
    path = item.get("ref_path")
    dti = item.get("ref_dti")
    if path is None and dti is None:
        data_value.ref_ofs = 0
    else:
        data_value.ref_ofs = value_offset
        data_value.ref_dti = _sdl_dti_value(dti or "0", app_id)
        data_value.ref_path = path or ""
    return data_value


def _get_sdl_data_value(
    prop_type, item, stream, sdl, track, value_offset, app_id
):
    if prop_type in SDL_VAL_TYPES:
        return _sdl_scalar_data_value(prop_type, item, stream, sdl, track)
    if prop_type == 14:
        return _sdl_string_data_value(item, stream, sdl, track, value_offset)
    if prop_type == 57:
        return _sdl_hermite_curve_data_value(item, stream, sdl, track)
    if prop_type in SDL_VECTOR_CLASSES:
        return _sdl_vector_data_value(prop_type, item, stream, sdl, track)
    if prop_type == 58:
        return _sdl_resource_data_value(
            item, stream, sdl, track, value_offset, app_id
        )
    raise ValueError(f"Unsupported SDL property type {prop_type}")


def _parse_sdl_xml_document(root_xml):
    if root_xml.tag != "sdl":
        raise ValueError('SDL XML root must be <sdl>')
    header_xml = root_xml.find("header")
    tracks_xml = root_xml.find("tracks")
    if header_xml is None or tracks_xml is None:
        raise ValueError('SDL XML must contain <header> and <tracks>')

    header = {
        "version": _read_xml_int(header_xml, "version", 17),
        "frame_max": _read_xml_int(header_xml, "frame_max", 0),
        "floor_frame": _read_xml_int(header_xml, "floor_frame", 0),
        "reserved": _read_xml_int(header_xml, "reserved", 0),
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
        track_elements.sort(key=lambda pair: _read_xml_int(pair[0], "index"))
        indices = [_read_xml_int(element, "index") for element, _ in track_elements]
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
        parent = _sdl_value_to_int(move_line)
        if not (0 <= parent <= 31 or parent == 0x3F):
            raise ValueError(f"SDL move_line on <{element.tag}> must be 0..31 or 63")
    elif track_type in SDL_ROOT_TRACK_TYPES:
        parent = 0
    elif element.get("parent") is not None:
        # Preserve explicit parent fields from XML created by earlier versions;
        # new XML expresses the same link by nesting.
        parent = _sdl_value_to_int(element.get("parent"))
    else:
        parent = (
            track_index_by_element[id(structural_parent)]
            if structural_parent is not None
            else 0
        )

    if not 0 <= parent <= 0xFFFFFFFF:
        raise ValueError(f"SDL parent value is outside its binary range: {parent}")
    if (
        track_type not in SDL_ROOT_TRACK_TYPES and
        track_type not in SDL_MOVE_LINE_TRACK_TYPES and
        (parent >= track_count or parent == track_index)
    ):
        raise ValueError(f"SDL parent index {parent} is invalid for track {track_index}")
    return parent


def _parse_sdl_track_entry(
    element, structural_parent, track_index, track_count, track_index_by_element,
    app_id,
):
    track_type = TRACK_TYPE[element.tag]
    data_xml = element.find("data")
    data_entry = list(data_xml) if data_xml is not None else []

    prop_type_attr = element.get("prop_type")
    if prop_type_attr is None:
        prop_type = next(
            (
                value
                for value, name in RV_MT_PROP_TYPES_RE5.items()
                if data_entry and name == data_entry[0].tag
            ),
            0,
        )
    else:
        prop_type = _sdl_prop_type_value(prop_type_attr)
    if data_entry and any(
        item.tag != RV_MT_PROP_TYPES_RE5.get(prop_type) for item in data_entry
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
        "dti_ref": _sdl_dti_value(element.get("dti_ref", "0"), app_id),
    }
    return track, data_entry


def _parse_sdl_track_entries(track_elements, track_index_by_element, app_id):
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
            app_id,
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
            data_entry and
            track["type"] > TRACK_TYPE["TYPE_OBJECT"] and
            data_struct_size is not None
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


def _write_sdl_bytes(header_values, tracks, track_data, layout, app_id):
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
            frame = _read_xml_int(item, "frame", 0)
            frame_type = _read_sdl_timing_frame_type(item)
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
                    _get_sdl_data_value(
                        track["prop_type"],
                        item,
                        stream,
                        sdl,
                        dst_track,
                        value_offset,
                        app_id,
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


def xml_to_sdl_bytes(root_xml, app_id):
    _get_sdl_dti_hashes(app_id)
    header_values, tracks_xml = _parse_sdl_xml_document(root_xml)
    track_elements, track_index_by_element = _collect_sdl_track_elements(tracks_xml)
    tracks, track_data = _parse_sdl_track_entries(
        track_elements, track_index_by_element, app_id
    )
    layout = _calculate_sdl_layout(tracks, track_data)
    return _write_sdl_bytes(header_values, tracks, track_data, layout, app_id)


XFS_EXTENSION_VERSIONS = {"fsm": 1, "lot": 4, "sce": 11, "lnk": 14}
XFS_PROPERTY_TYPES_BY_APP_ID = {
    "dmc4": MT_PROP_TYPES_RE5,
    "re5": MT_PROP_TYPES_RE5,
}
XFS_VECTOR_PROPERTY_TYPE_NAMES = frozenset({
    "TYPE_COLOR",
    "TYPE_POINT",
    "TYPE_RECT",
    "TYPE_MATRIX",
    "TYPE_VECTOR3",
    "TYPE_VECTOR4",
    "TYPE_QUATERNION",
    "TYPE_FLOAT2",
    "TYPE_FLOAT3",
    "TYPE_FLOAT4",
    "TYPE_FLOAT3x3",
    "TYPE_FLOAT4x3",
    "TYPE_FLOAT4x4",
    "TYPE_EASECURVE",
    "TYPE_LINE",
    "TYPE_LINESEGMENT",
    "TYPE_RAY",
    "TYPE_PLANE",
    "TYPE_SPHERE",
    "TYPE_CAPSULE",
    "TYPE_AABB",
    "TYPE_OBB",
    "TYPE_CYLINDER",
    "TYPE_RANGE",
    "TYPE_RANGEF",
})
XFS_SCALAR_READERS_BY_TYPE_NAME = {
    "TYPE_BOOL": KaitaiStream.read_u1,
    "TYPE_U8": KaitaiStream.read_u1,
    "TYPE_U16": KaitaiStream.read_u2le,
    "TYPE_U32": KaitaiStream.read_u4le,
    "TYPE_U64": KaitaiStream.read_u8le,
    "TYPE_S8": KaitaiStream.read_s1,
    "TYPE_S16": KaitaiStream.read_s2le,
    "TYPE_S32": KaitaiStream.read_s4le,
    "TYPE_S64": KaitaiStream.read_s8le,
    "TYPE_F32": KaitaiStream.read_f4le,
    "TYPE_F64": KaitaiStream.read_f8le,
}
XFS_SCALAR_SIZES_BY_TYPE_NAME = {
    "TYPE_BOOL": 1,
    "TYPE_U8": 1,
    "TYPE_U16": 2,
    "TYPE_U32": 4,
    "TYPE_U64": 8,
    "TYPE_S8": 1,
    "TYPE_S16": 2,
    "TYPE_S32": 4,
    "TYPE_S64": 8,
    "TYPE_F32": 4,
    "TYPE_F64": 8,
}
XFS_PROPERTY_SIZES_BY_TYPE_NAME = {
    "TYPE_CLASS": 4,
    "TYPE_CLASSREF": 4,
    "TYPE_STRING": 4,
    "TYPE_COLOR": 4,
    "TYPE_POINT": 8,
    "TYPE_RECT": 16,
    "TYPE_MATRIX": 64,
    "TYPE_VECTOR3": 16,
    "TYPE_VECTOR4": 16,
    "TYPE_QUATERNION": 16,
    "TYPE_FLOAT4": 16,
    "TYPE_AABB": 32,
    "TYPE_RANGE": 8,
    "TYPE_RANGEF": 8,
    "TYPE_CUSTOM": 64,
    "TYPE_HERMITECURVE": 64,
}
XFS_SCALAR_FORMATS_BY_TYPE_NAME = {
    "TYPE_BOOL": 'B',
    "TYPE_U8": 'B',
    "TYPE_U16": 'H',
    "TYPE_U32": 'I',
    "TYPE_U64": 'Q',
    "TYPE_S8": 'b',
    "TYPE_S16": 'h',
    "TYPE_S32": 'i',
    "TYPE_S64": 'q',
    "TYPE_F32": 'f',
    "TYPE_F64": 'd',
}

XFS_VECTOR_COMPONENT_NAMES = {
    "TYPE_COLOR": ("r", "g", "b", "a"),
    "TYPE_POINT": ("x", "y"),
    "TYPE_VECTOR3": ("x", "y", "z", "w"),
    "TYPE_VECTOR4": ("x", "y", "z", "w"),
    "TYPE_QUATERNION": ("x", "y", "z", "w"),
    "TYPE_FLOAT2": ("x", "y"),
    "TYPE_FLOAT3": ("x", "y", "z"),
    "TYPE_FLOAT4": ("x", "y", "z", "w"),
    "TYPE_RECT": ("left", "top", "right", "bottom"),
    "TYPE_MATRIX": tuple(
        f"m{row}{column}" for row in range(4) for column in range(4)
    ),
    "TYPE_FLOAT3x3": tuple(
        f"m{row}{column}" for row in range(3) for column in range(3)
    ),
    "TYPE_FLOAT4x3": tuple(
        f"m{row}{column}" for row in range(4) for column in range(3)
    ),
    "TYPE_FLOAT4x4": tuple(
        f"m{row}{column}" for row in range(4) for column in range(4)
    ),
    "TYPE_RANGE": ("min", "max"),
    "TYPE_RANGEF": ("min", "max"),
    "TYPE_AABB": ("min_x", "min_y", "min_z", "max_x", "max_y", "max_z"),
}


def _xfs_xml_type_name(type_id, property_type_info):
    type_name = property_type_info['reverse_property_types'].get(type_id)
    if type_name is None:
        return f"unknown_{type_id}"
    return type_name.removeprefix("TYPE_").lower()


def _xfs_vector_component_names(type_name, count):
    names = XFS_VECTOR_COMPONENT_NAMES.get(type_name, ())
    if count <= len(names):
        return names[:count]
    return names + tuple(f"v{i}" for i in range(len(names), count))


def _get_xfs_property_type_info(app_id):
    try:
        property_types = XFS_PROPERTY_TYPES_BY_APP_ID[app_id.lower()]
    except (AttributeError, KeyError) as error:
        raise ValueError(f'Unsupported XFS app id {app_id!r}') from error

    def to_ids(type_names):
        return {
            property_types[type_name]: value
            for type_name, value in type_names.items()
            if type_name in property_types
        }

    return {
        'property_types': property_types,
        'reverse_property_types': {
            type_id: type_name for type_name, type_id in property_types.items()
        },
        'vector_property_types': frozenset(
            property_types[name] for name in XFS_VECTOR_PROPERTY_TYPE_NAMES
        ),
        'scalar_readers': to_ids(XFS_SCALAR_READERS_BY_TYPE_NAME),
        'scalar_sizes': to_ids(XFS_SCALAR_SIZES_BY_TYPE_NAME),
        'property_sizes': {
            **to_ids(XFS_PROPERTY_SIZES_BY_TYPE_NAME),
            int(Xfs.PropertyType.resource): 4,
        },
        'scalar_formats': to_ids(XFS_SCALAR_FORMATS_BY_TYPE_NAME),
    }


def build_xfs_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
    assert app_id == "re5", "Currently only Resident Evil 5 is supported"
    extension = vfile.extension.lower()
    xfs_bytes = vfile.get_bytes()
    xfs = Xfs.from_bytes(xfs_bytes)
    xfs._read()
    bl_object_name = vfile.display_name
    bl_object = bpy.data.objects.new(name=bl_object_name, object_data=None)

    xml = XfsXmlImporter(xfs, extension, app_id).to_xml()
    if extension == "lot":
        build_xfs_lot_markers(bl_object, xml, context)
    ET.indent(xml, space="\t", level=0)
    buffer = io.StringIO()
    xml.write(buffer, encoding="unicode", xml_declaration=True)
    xml_string = buffer.getvalue()
    text = bpy.data.texts.new(bl_object_name + ".xml")
    bl_object[extension] = text.name
    text.from_string(xml_string)

    return bl_object


def export_xfs(bl_obj):
    asset = bl_obj.albam_asset
    app_id = asset.app_id
    extension = asset.extension.lower()
    xml_name = bl_obj.get(extension)
    if not xml_name:
        return []

    xml_text = bpy.data.texts.get(xml_name)
    if xml_text is None:
        raise ValueError(f'{extension.upper()} XML text "{xml_name}" is missing')

    xml = ET.fromstring(xml_text.as_string())
    if extension == "lot":
        write_xfs_lot_marker_changes(xml, bl_obj)
    xfs_bytes = to_xfs(xml, app_id)
    return [VirtualFileData(app_id, asset.relative_path, data_bytes=xfs_bytes)]


for xfs_extension in XFS_EXTENSIONS:
    blender_registry.register_import_function(
        app_id="re5", extension=xfs_extension, albam_asset_type="CONFIG"
    )(build_xfs_object)
    blender_registry.register_export_function(
        app_id="re5", extension=xfs_extension
    )(export_xfs)


class XfsXmlImporter:
    """Convert parsed XFS data to a compact, editable XML tree."""

    def __init__(self, xfs, extension, app_id):
        self.xfs = xfs
        self.extension = extension
        self.app_id = app_id
        self.dti_hashes = _get_sdl_dti_hashes(app_id)
        self.property_type_info = _get_xfs_property_type_info(app_id)

    def class_name_for_index(self, class_index):
        class_def = self.xfs.class_defs[class_index]
        return self.dti_hashes.get(class_def.type_hash, str(hex(class_def.type_hash)))

    def append_class_body(self, body, class_xml):
        for property_values in body.properties:
            self.append_property(class_xml, property_values)

    def append_reference_value(self, parent, value, property_name=None):
        attrib = {}
        if property_name is not None:
            attrib['name'] = property_name

        if value.is_null:
            attrib['value'] = 'None'
            ET.SubElement(parent, 'classref', attrib=attrib)
            return

        class_name = self.class_name_for_index(value.class_index)
        attrib.update({
            'type': class_name,
            'class_index': str(value.class_index),
        })
        if value.is_inline:
            attrib['id'] = str(value.index)
            class_xml = ET.SubElement(parent, 'classref', attrib=attrib)
            self.append_class_body(value.body, class_xml)
        else:
            attrib['ref'] = str(value.index)
            ET.SubElement(parent, 'classref', attrib=attrib)

    def append_simple_value(
        self, parent, tag_name, value, property_type, property_name=None
    ):
        property_type_info = self.property_type_info
        attrib = {}
        if property_name is not None:
            attrib['name'] = property_name

        if property_type == property_type_info['property_types'].get('TYPE_STRING'):
            attrib['value'] = value.value
        elif property_type == int(Xfs.PropertyType.resource):
            attrib['class'] = value.class_name
            attrib['path'] = value.path
        elif property_type in property_type_info['vector_property_types']:
            if len(value.value) % 4:
                raise ValueError(
                    f'XFS vector property has a value size of {len(value.value)} '
                    'bytes, not divisible by 4'
                )
            components = [
                struct.unpack_from('<f', value.value, offset)[0]
                for offset in range(0, len(value.value), 4)
            ]
            # A vector3 occupies 16 bytes in XFS. The fourth float is normally
            # zero padding, so keep it out of the editing view unless it matters.
            type_name = property_type_info['reverse_property_types'].get(
                property_type
            )
            if (
                type_name == 'TYPE_VECTOR3' and
                len(components) == 4 and
                components[3] == 0
            ):
                components.pop()
            names = _xfs_vector_component_names(type_name, len(components))
            attrib.update(
                {name: str(component) for name, component in zip(names, components)}
            )
        else:
            scalar_reader = property_type_info['scalar_readers'].get(property_type)
            if scalar_reader is None:
                attrib['value'] = value.value.hex()
                attrib['size'] = str(len(value.value))
                attrib['type_id'] = str(property_type)
                tag_name = 'raw'
            else:
                scalar_value = scalar_reader(KaitaiStream(io.BytesIO(value.value)))
                if property_type == property_type_info['property_types'].get('TYPE_BOOL'):
                    scalar_value = 'true' if scalar_value else 'false'
                else:
                    scalar_value = str(scalar_value)
                attrib['value'] = scalar_value

        ET.SubElement(parent, tag_name, attrib=attrib)

    def append_property(self, parent, property_values):
        property_type_info = self.property_type_info
        prop = property_values.property
        property_type = int(prop.type)
        tag_name = _xfs_xml_type_name(property_type, property_type_info)
        values = property_values.values
        is_reference = property_type in (
            property_type_info['property_types']['TYPE_CLASS'],
            property_type_info['property_types']['TYPE_CLASSREF'],
        )

        if len(values) == 1:
            if is_reference:
                self.append_reference_value(parent, values[0], prop.name)
            else:
                self.append_simple_value(
                    parent, tag_name, values[0], property_type, prop.name
                )
            return

        array_xml = ET.SubElement(
            parent,
            'array',
            attrib={'name': prop.name, 'type': tag_name},
        )
        if is_reference:
            for value in values:
                self.append_reference_value(array_xml, value)
        else:
            for value in values:
                self.append_simple_value(array_xml, tag_name, value, property_type)

    def to_xml(self):
        """Return an XML tree representing the XFS root and class metadata."""
        xfs = self.xfs
        root = ET.Element(
            'root',
            attrib={
                'app_id': self.app_id,
                'extension': self.extension,
                'version_major': str(xfs.header.version_major),
                'version_minor': str(xfs.header.version_minor),
            },
        )

        if xfs.data.num_roots != 1:
            raise ValueError(f'Expected one XFS root object, got {xfs.data.num_roots}')

        # The XFS root body is stored directly in the data section, outside the
        # object-reference index sequence.
        root_class = ET.SubElement(
            root,
            'class',
            attrib={'name': self.class_name_for_index(0), 'class_index': '0'},
        )
        self.append_class_body(xfs.data.root, root_class)

        # Preserve class definitions that have no instantiated object in the XML
        # tree, plus binary details that are not part of the editable values.
        metadata_xml = ET.SubElement(root, '_xfs_metadata')
        for class_index, class_def in enumerate(xfs.class_defs):
            class_xml = ET.SubElement(
                metadata_xml,
                'class_def',
                attrib={
                    'index': str(class_index),
                    'name': self.class_name_for_index(class_index),
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
                    },
                )

        return ET.ElementTree(root)


def from_xfs(xfs, extension, app_id):
    """Convert XFS data to a compact, editable XML tree."""
    return XfsXmlImporter(xfs, extension, app_id).to_xml()


class XfsXmlSerializer:
    """Build an XFS binary from its editable XML representation."""

    def __init__(self, xml, app_id=None):
        self.xml = xml.getroot() if isinstance(xml, ET.ElementTree) else xml
        if self.xml.tag != 'root':
            raise ValueError('XFS XML root must be <root>')
        self.app_id = (app_id or self.xml.attrib.get('app_id') or '').lower()
        if not self.app_id:
            raise ValueError('XFS app_id is required to select property type IDs')
        self.xml.set('app_id', self.app_id)
        self.property_type_info = _get_xfs_property_type_info(self.app_id)
        self.property_types = self.property_type_info['property_types']
        _get_sdl_dti_hashes(self.app_id)
        self.dti_hashes_by_name = RV_SDL_DTI_HASHES[self.app_id]

        root_classes = [child for child in self.xml if child.tag == 'class']
        if len(root_classes) != 1:
            raise ValueError(
                f'XFS XML must contain one root <class>, got {len(root_classes)}'
            )
        self.root_class = root_classes[0]
        self.class_defs = {}
        self.class_indexes_by_name = defaultdict(list)
        self.seen_instance_defs = set()
        self.output_object_ids = {}
        # The root body has no ObjectRef header, so inline object indexes start at 1.
        self.next_object_id = 1
        self.class_count = 0
        self._read_class_metadata()

    @staticmethod
    def _parse_int(value):
        try:
            return int(value, 0)
        except ValueError:
            return int(value, 10)

    def _read_class_metadata(self):
        metadata_xml = self.xml.find('_xfs_metadata')
        if metadata_xml is None:
            return

        for class_xml in metadata_xml.findall('class_def'):
            class_index = self._parse_int(class_xml.attrib['index'])
            class_name = class_xml.attrib['name']
            properties = []
            for prop_xml in class_xml.findall('property'):
                reserved = bytes.fromhex(prop_xml.attrib.get('reserved', ''))
                if not reserved:
                    reserved = bytes(16)
                if len(reserved) != 16:
                    raise ValueError(
                        f'XFS property {prop_xml.attrib.get("name")!r} '
                        'reserved field must be 16 bytes'
                    )
                properties.append({
                    'name': prop_xml.attrib['name'],
                    'type_id': self._parse_int(prop_xml.attrib['type_id']),
                    'flags': self._parse_int(prop_xml.attrib.get('flags', '0')),
                    'size': self._parse_int(prop_xml.attrib['size']),
                    'reserved': reserved,
                })
            self.class_defs[class_index] = {
                'name': class_name,
                'type_hash': self._parse_int(class_xml.attrib['type_hash']),
                'properties': properties,
            }
            self.class_indexes_by_name[class_name].append(class_index)

    @staticmethod
    def _class_name_for_node(class_xml):
        if class_xml.tag == 'classref':
            return class_xml.attrib.get('type', class_xml.attrib.get('name', ''))
        return class_xml.attrib.get('name', class_xml.attrib.get('type', ''))

    def _class_index_for_node(self, class_xml, create=False):
        if (
            class_xml.attrib.get('name') == 'null'
            or class_xml.attrib.get('value') == 'None'
            or class_xml.attrib.get('ref') is not None
        ):
            return None
        class_index_attr = class_xml.attrib.get('class_index')
        if class_index_attr is not None:
            class_index = self._parse_int(class_index_attr)
            if class_index not in self.class_defs and not create:
                raise ValueError(
                    f'XFS class {self._class_name_for_node(class_xml)!r} uses missing '
                    f'class index {class_index}'
                )
            return class_index

        class_name = self._class_name_for_node(class_xml)
        if self.class_indexes_by_name[class_name]:
            return self.class_indexes_by_name[class_name][0]
        if not create:
            raise ValueError(f'Unknown XFS class {class_name!r}')
        class_index = max(self.class_defs, default=-1) + 1
        self.class_indexes_by_name[class_name].append(class_index)
        return class_index

    def _parse_property_type(self, prop_xml, old_prop=None):
        if old_prop is not None and prop_xml.tag not in (
            'scalar', 'vector', 'array', 'raw'
        ):
            return old_prop['type_id']

        type_name = prop_xml.attrib.get('type')
        if prop_xml.tag not in ('scalar', 'vector', 'array', 'raw'):
            type_name = prop_xml.tag
        if prop_xml.tag == 'raw' and prop_xml.attrib.get('type_id') is not None:
            return self._parse_int(prop_xml.attrib['type_id'])
        try:
            return int(self.property_types[type_name])
        except (KeyError, TypeError):
            if type_name:
                type_key = type_name.lower()
                if not type_key.startswith('type_'):
                    type_key = 'type_' + type_key
                for known_name, known_id in self.property_types.items():
                    if known_name.lower() == type_key:
                        return int(known_id)
                try:
                    return self._parse_int(type_name)
                except ValueError:
                    pass
            if type_name and type_name.startswith('TYPE_UNKNOWN_'):
                try:
                    return self._parse_int(type_name[len('TYPE_UNKNOWN_'):])
                except ValueError:
                    pass
        if old_prop is not None:
            return old_prop['type_id']
        raise ValueError(f'Unknown XFS property type {type_name!r}')

    def _parse_property_def(self, prop_xml, old_prop=None):
        type_id = self._parse_property_type(prop_xml, old_prop)
        size_text = prop_xml.attrib.get('size')
        if size_text is not None:
            size = self._parse_int(size_text)
        elif old_prop is not None:
            size = old_prop['size']
        else:
            size = self.property_type_info['property_sizes'].get(
                type_id, self.property_type_info['scalar_sizes'].get(type_id)
            )
            if (
                size is None
                and type_id in self.property_type_info['vector_property_types']
            ):
                values = self._simple_value_nodes(prop_xml)
                if values:
                    size = len(self._vector_component_values(values[0], type_id)) * 4
            if size is None:
                values = self._simple_value_nodes(prop_xml)
                if values:
                    try:
                        size = len(bytes.fromhex(self._scalar_text(values[0])))
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
        flags = self._parse_int(flags_text) if flags_text is not None else default_flags
        reserved_text = prop_xml.attrib.get('reserved')
        reserved = (
            bytes.fromhex(reserved_text)
            if reserved_text is not None else default_reserved
        )
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

    def _hash_for_class(self, class_name):
        if class_name in self.dti_hashes_by_name:
            return self.dti_hashes_by_name[class_name]
        try:
            return self._parse_int(class_name)
        except ValueError:
            try:
                encoded = class_name.encode('ascii')
            except UnicodeEncodeError as error:
                raise ValueError(
                    f'XFS class name {class_name!r} must be ASCII'
                ) from error
            return (~zlib.crc32(encoded)) & 0x7FFFFFFF

    @staticmethod
    def _scalar_text(value_xml):
        if 'value' in value_xml.attrib:
            return value_xml.attrib['value']
        if 'val' in value_xml.attrib:
            return value_xml.attrib['val']
        if value_xml.text is not None:
            return value_xml.text
        raise ValueError(f'Missing XFS value on <{value_xml.tag}>')

    @staticmethod
    def _simple_value_nodes(prop_xml):
        if prop_xml.tag == 'array':
            return list(prop_xml)
        if prop_xml.tag == 'vector':
            vectors = prop_xml.findall('vec')
            if vectors:
                return vectors
            return [] if prop_xml.attrib.get('type') is not None else [prop_xml]
        if prop_xml.tag in ('scalar', 'string', 'resource'):
            items = prop_xml.findall('item')
            if items:
                return items
            return [] if prop_xml.attrib.get('type') is not None else [prop_xml]
        return [prop_xml]

    def _vector_component_values(self, value_xml, type_id):
        if value_xml.tag == 'vec':
            return [self._scalar_text(item) for item in value_xml.findall('item')]
        if value_xml.tag == 'vector':
            vectors = value_xml.findall('vec')
            if vectors:
                return self._vector_component_values(vectors[0], type_id)

        type_name = self.property_type_info['reverse_property_types'].get(type_id)
        names = XFS_VECTOR_COMPONENT_NAMES.get(type_name, ())
        component_names = [
            name for name in names if name in value_xml.attrib
        ]
        if not component_names:
            component_names = sorted(
                (
                    name for name in value_xml.attrib
                    if name.startswith('v') and name[1:].isdigit()
                ),
                key=lambda name: int(name[1:]),
            )
        if component_names:
            values = [value_xml.attrib[name] for name in component_names]
            generic_names = sorted(
                (
                    name for name in value_xml.attrib
                    if name.startswith('v') and name[1:].isdigit()
                ),
                key=lambda name: int(name[1:]),
            )
            values.extend(value_xml.attrib[name] for name in generic_names)
            return values
        if 'value' in value_xml.attrib:
            return [value_xml.attrib['value']]
        return []

    def _reference_value_nodes(self, prop_xml):
        if prop_xml.tag == 'array':
            return list(prop_xml)
        if prop_xml.tag == 'classref':
            legacy_values = prop_xml.findall('class')
            if legacy_values:
                return legacy_values
            if prop_xml.attrib.get('type') in ('TYPE_CLASS', 'TYPE_CLASSREF'):
                return []
            return [prop_xml]
        return prop_xml.findall('class')

    @staticmethod
    def _is_inline_reference(value_xml):
        if value_xml.attrib.get('name') == 'null':
            return False
        if value_xml.attrib.get('value') == 'None' or value_xml.attrib.get('ref') is not None:
            return False
        if value_xml.attrib.get('reference_index') is not None:
            return False
        if value_xml.tag == 'classref':
            if value_xml.findall('class'):
                return False
            return value_xml.attrib.get('type') not in (None, 'TYPE_CLASSREF', 'TYPE_CLASS')
        return True

    def _collect_inline_classes(self, class_xml):
        class_index = self._class_index_for_node(class_xml, create=True)
        class_name = self._class_name_for_node(class_xml)
        old_def = self.class_defs.get(class_index)
        old_props = old_def['properties'] if old_def is not None else []
        property_nodes = [child for child in class_xml if child.tag != '_xfs_metadata']
        properties = [
            self._parse_property_def(
                prop_xml,
                old_props[i] if i < len(old_props) else None,
            )
            for i, prop_xml in enumerate(property_nodes)
        ]

        if class_index in self.seen_instance_defs:
            current = self.class_defs[class_index]
            current_signature = [
                (p['name'], p['type_id'], p['flags'], p['size'], p['reserved'])
                for p in current['properties']
            ]
            new_signature = [
                (p['name'], p['type_id'], p['flags'], p['size'], p['reserved'])
                for p in properties
            ]
            if current_signature != new_signature:
                raise ValueError(
                    f'Inconsistent property definitions for XFS class {class_name!r}'
                )
        else:
            if old_def is None:
                self.class_defs[class_index] = {
                    'name': class_name,
                    'type_hash': self._hash_for_class(class_name),
                    'properties': properties,
                }
                if class_index not in self.class_indexes_by_name[class_name]:
                    self.class_indexes_by_name[class_name].append(class_index)
            else:
                old_def['name'] = class_name
                old_def['properties'] = properties
            self.seen_instance_defs.add(class_index)

        for prop_xml in property_nodes:
            prop_def = next(
                prop for prop in properties
                if prop['name'] == prop_xml.attrib.get('name', '')
            )
            if prop_def['type_id'] in (
                self.property_types.get('TYPE_CLASS'),
                self.property_types.get('TYPE_CLASSREF'),
            ):
                for value_xml in self._reference_value_nodes(prop_xml):
                    if self._is_inline_reference(value_xml):
                        self._collect_inline_classes(value_xml)

    def _prepare_class_definitions(self):
        self._collect_inline_classes(self.root_class)
        if self._class_index_for_node(self.root_class) != 0:
            raise ValueError('The root XFS object must use class index 0')
        if not self.class_defs:
            raise ValueError('XFS XML does not define any classes')

        self.class_count = max(self.class_defs) + 1
        if set(self.class_defs) != set(range(self.class_count)):
            raise ValueError('XFS class indexes must be contiguous from zero')
        if self.class_count > 0x7FFF:
            raise ValueError('XFS class count exceeds the object-reference tag capacity')

    @staticmethod
    def _pack_uint(value, bits, label):
        limit = (1 << bits) - 1
        if not 0 <= value <= limit:
            raise ValueError(f'{label} {value} does not fit in {bits} bits')
        return value.to_bytes(bits // 8, 'little')

    @staticmethod
    def _encode_ascii(value, label):
        if '\0' in value:
            raise ValueError(f'XFS {label} cannot contain NUL characters')
        try:
            return value.encode('ascii')
        except UnicodeEncodeError as error:
            raise ValueError(f'XFS {label} must be ASCII: {value!r}') from error

    @classmethod
    def _encode_terminated(cls, value, label):
        return cls._encode_ascii(value, label) + b'\0'

    def _node_class_index(self, class_xml):
        class_index_attr = class_xml.attrib.get('class_index')
        if class_index_attr is not None:
            class_index = self._parse_int(class_index_attr)
        else:
            class_name = self._class_name_for_node(class_xml)
            options = self.class_indexes_by_name[class_name]
            if len(options) != 1:
                raise ValueError(f'Cannot resolve class index for XFS class {class_name!r}')
            class_index = options[0]
        if class_index not in self.class_defs:
            raise ValueError(f'XFS object uses undefined class index {class_index}')
        return class_index

    def _get_object_source_id(self, class_xml):
        value = class_xml.attrib.get('id', class_xml.attrib.get('object_index'))
        return self._parse_int(value) if value is not None else None

    def _encode_reference(self, class_xml):
        class_name = class_xml.attrib.get('name', '')
        if (
            class_name == 'null'
            or class_xml.attrib.get('reference_kind') == 'null'
            or class_xml.attrib.get('value') == 'None'
        ):
            return (
                self._pack_uint(0xFFFE, 16, 'null-reference tag') +
                self._pack_uint(0, 16, 'null-reference index')
            )

        class_index = self._node_class_index(class_xml)
        reference_source_id = class_xml.attrib.get(
            'ref', class_xml.attrib.get('reference_index')
        )
        if reference_source_id is not None:
            reference_source_id = self._parse_int(reference_source_id)
            if reference_source_id not in self.output_object_ids:
                raise ValueError(
                    f'XFS back-reference points to object {reference_source_id}, '
                    'which has not been serialized yet'
                )
            tag = class_index * 2
            object_index = self.output_object_ids[reference_source_id]
            return self._pack_uint(tag, 16, 'back-reference tag') + self._pack_uint(
                object_index, 16, 'back-reference index'
            )

        object_index = self.next_object_id
        self.next_object_id += 1
        source_id = self._get_object_source_id(class_xml)
        if source_id is not None:
            if source_id in self.output_object_ids:
                raise ValueError(f'Duplicate XFS object index {source_id}')
            self.output_object_ids[source_id] = object_index

        body = self._encode_body(class_xml, class_index)
        size = len(body) + 4
        return (
            self._pack_uint(class_index * 2 + 1, 16, 'inline-reference tag') +
            self._pack_uint(object_index, 16, 'inline-reference index') +
            self._pack_uint(size, 32, 'inline-reference size') + body
        )

    def _encode_reference_values(self, prop_xml):
        values = self._reference_value_nodes(prop_xml)
        output = bytearray(self._pack_uint(len(values), 32, 'property value count'))
        for value_xml in values:
            output.extend(self._encode_reference(value_xml))
        return bytes(output)

    def _encode_string_values(self, prop_xml):
        values = self._simple_value_nodes(prop_xml)
        output = bytearray(self._pack_uint(len(values), 32, 'property value count'))
        for value_xml in values:
            output.extend(
                self._encode_terminated(self._scalar_text(value_xml), 'string value')
            )
        return bytes(output)

    def _encode_resource_values(self, prop_xml, prop_def):
        if prop_xml.tag == 'resource' and (
            'class' in prop_xml.attrib or 'path' in prop_xml.attrib
        ):
            values = [prop_xml]
        elif prop_xml.tag == 'resource' and prop_xml.attrib.get('type') is not None:
            items = prop_xml.findall('item')
            if len(items) % 2:
                raise ValueError(
                    f'XFS resource property {prop_def["name"]!r} must contain '
                    'class-name/path item pairs'
                )
            values = [
                {'class': items[i].attrib['val'], 'path': items[i + 1].attrib['val']}
                for i in range(0, len(items), 2)
            ]
        elif prop_xml.tag == 'array':
            values = list(prop_xml)
        else:
            items = prop_xml.findall('item')
            if len(items) % 2:
                raise ValueError(
                    f'XFS resource property {prop_def["name"]!r} must contain '
                    'class-name/path item pairs'
                )
            values = [
                {'class': items[i].attrib['val'], 'path': items[i + 1].attrib['val']}
                for i in range(0, len(items), 2)
            ]

        output = bytearray(self._pack_uint(len(values), 32, 'property value count'))
        for value_xml in values:
            if isinstance(value_xml, dict):
                class_name = value_xml['class']
                path = value_xml['path']
            else:
                class_name = value_xml.attrib.get('class', 'null')
                path = value_xml.attrib.get('path', '')
            output.extend(b'\x02')
            output.extend(self._encode_terminated(class_name, 'resource class name'))
            output.extend(self._encode_terminated(path, 'resource path'))
        return bytes(output)

    def _encode_vector_values(self, prop_xml, prop_def):
        if prop_xml.tag == 'scalar' and prop_xml.findall('item'):
            values = prop_xml.findall('item')
            output = bytearray(self._pack_uint(len(values), 32, 'property value count'))
            for value_xml in values:
                try:
                    vector_data = bytes.fromhex(value_xml.attrib['val'])
                except (KeyError, ValueError) as error:
                    raise ValueError(
                        f'Legacy XFS vector property {prop_def["name"]!r} '
                        'must contain a hex value'
                    ) from error
                if len(vector_data) != prop_def['size']:
                    raise ValueError(
                        f'XFS vector property {prop_def["name"]!r} has '
                        f'{len(vector_data)} bytes per value; expected {prop_def["size"]}'
                    )
                output.extend(vector_data)
            return bytes(output)

        values = self._simple_value_nodes(prop_xml)
        output = bytearray(self._pack_uint(len(values), 32, 'property value count'))
        for vector_xml in values:
            vector_data = bytearray()
            components = self._vector_component_values(
                vector_xml, prop_def['type_id']
            )
            if len(components) * 4 < prop_def['size']:
                components.extend(
                    ['0.0'] * ((prop_def['size'] - len(components) * 4) // 4)
                )
            for component in components:
                vector_data.extend(struct.pack('<f', float(component)))
            if len(vector_data) != prop_def['size']:
                raise ValueError(
                    f'XFS vector property {prop_def["name"]!r} has '
                    f'{len(vector_data)} bytes per value; expected {prop_def["size"]}'
                )
            output.extend(vector_data)
        return bytes(output)

    def _encode_scalar_values(self, prop_xml, prop_def):
        type_id = prop_def['type_id']
        values = self._simple_value_nodes(prop_xml)
        output = bytearray(self._pack_uint(len(values), 32, 'property value count'))
        value_format = self.property_type_info['scalar_formats'].get(type_id)
        for value_xml in values:
            value_text = self._scalar_text(value_xml)
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
            else:
                if type_id in (
                    self.property_types["TYPE_F32"],
                    self.property_types["TYPE_F64"],
                ):
                    scalar_value = float(value_text)
                elif type_id == self.property_types["TYPE_BOOL"]:
                    scalar_value = (
                        int(value_text.lower() == 'true')
                        if value_text.lower() in ('true', 'false')
                        else self._parse_int(value_text)
                    )
                else:
                    scalar_value = self._parse_int(value_text)
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

    def _encode_property_values(self, prop_xml, prop_def):
        type_id = prop_def['type_id']
        if type_id in (
            self.property_types["TYPE_CLASS"],
            self.property_types["TYPE_CLASSREF"],
        ):
            return self._encode_reference_values(prop_xml)
        if type_id == self.property_types["TYPE_STRING"]:
            return self._encode_string_values(prop_xml)
        if type_id == int(Xfs.PropertyType.resource):
            return self._encode_resource_values(prop_xml, prop_def)
        if type_id in self.property_type_info['vector_property_types']:
            return self._encode_vector_values(prop_xml, prop_def)
        return self._encode_scalar_values(prop_xml, prop_def)

    def _encode_body(self, class_xml, class_index):
        class_def = self.class_defs[class_index]
        properties = list(class_xml)
        expected = class_def['properties']
        if len(properties) != len(expected):
            raise ValueError(
                f'XFS class {class_def["name"]!r} has {len(properties)} XML properties, '
                f'but its class definition has {len(expected)}'
            )

        output = bytearray()
        for prop_xml, prop_def in zip(properties, expected):
            if prop_xml.attrib.get('name', '') != prop_def['name']:
                raise ValueError(
                    f'XFS property order/name mismatch in class {class_def["name"]!r}: '
                    f'{prop_xml.attrib.get("name")!r} != {prop_def["name"]!r}'
                )
            output.extend(self._encode_property_values(prop_xml, prop_def))
        return bytes(output)

    def _encode_data_section(self, root_body):
        return (
            self._pack_uint(1, 32, 'XFS root count') +
            self._pack_uint(len(root_body) + 4, 32, 'XFS data-section size') + root_body
        )

    def _build_class_table(self):
        name_table = bytearray()
        name_offsets = {}
        for class_index in range(self.class_count):
            for prop in self.class_defs[class_index]['properties']:
                prop_name = prop['name']
                if prop_name not in name_offsets:
                    name_offsets[prop_name] = len(name_table)
                    name_table.extend(self._encode_terminated(prop_name, 'property name'))

        offsets_size = self.class_count * 4
        class_defs_size = sum(
            8 + 24 * len(self.class_defs[i]['properties'])
            for i in range(self.class_count)
        )
        class_defs_data = bytearray()
        class_def_offsets = []
        for class_index in range(self.class_count):
            class_def = self.class_defs[class_index]
            class_def_offsets.append(offsets_size + len(class_defs_data))
            class_defs_data.extend(
                self._pack_uint(class_def['type_hash'], 32, 'class type hash')
            )
            properties = class_def['properties']
            class_defs_data.extend(
                self._pack_uint(len(properties), 32, 'class property count')
            )
            for prop in properties:
                name_offset = offsets_size + class_defs_size + name_offsets[prop['name']]
                class_defs_data.extend(
                    self._pack_uint(name_offset, 32, 'property name offset')
                )
                class_defs_data.extend(self._pack_uint(prop['type_id'], 8, 'property type'))
                class_defs_data.extend(self._pack_uint(prop['flags'], 8, 'property flags'))
                class_defs_data.extend(self._pack_uint(prop['size'], 16, 'property size'))
                class_defs_data.extend(prop['reserved'])

        offsets_data = b''.join(
            self._pack_uint(offset, 32, 'class-definition offset')
            for offset in class_def_offsets
        )
        return offsets_data, bytes(class_defs_data), bytes(name_table), offsets_size, class_defs_size

    def _build_header(self, offsets_size, class_defs_size, name_table_size):
        extension = self.xml.attrib.get('extension', 'lot').lower().lstrip('.')
        version_major = (
            self._parse_int(self.xml.attrib['version_major'])
            if 'version_major' in self.xml.attrib else 6
        )
        if 'version_minor' in self.xml.attrib:
            version_minor = self._parse_int(self.xml.attrib['version_minor'])
        elif extension in XFS_EXTENSION_VERSIONS:
            version_minor = XFS_EXTENSION_VERSIONS[extension]
        else:
            raise ValueError(f'No XFS version is known for extension {extension!r}')

        offset_data = offsets_size + class_defs_size + name_table_size
        return (
            b'XFS\0' +
            self._pack_uint(version_major, 16, 'XFS major version') +
            self._pack_uint(version_minor, 16, 'XFS minor version') +
            self._pack_uint(self.class_count, 32, 'XFS class count') +
            self._pack_uint(offset_data, 32, 'XFS data offset')
        )

    def serialize(self):
        self._prepare_class_definitions()
        root_class_index = self._node_class_index(self.root_class)
        root_body = self._encode_body(self.root_class, root_class_index)
        data_section = self._encode_data_section(root_body)
        (
            class_def_offsets,
            class_defs_data,
            name_table,
            offsets_size,
            class_defs_size,
        ) = self._build_class_table()
        header = self._build_header(offsets_size, class_defs_size, len(name_table))
        return header + class_def_offsets + class_defs_data + name_table + data_section


def to_xfs(xml, app_id=None):
    """Serialize XFS XML using the class-definition/data-section schema."""
    return XfsXmlSerializer(xml, app_id).serialize()
