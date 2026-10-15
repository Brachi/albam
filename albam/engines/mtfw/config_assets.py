import bpy
import io
import xml.etree.ElementTree as ET
from kaitaistruct import KaitaiStream
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile

from ...lib.xml_parser import from_xfs, to_xfs
from ...lib.kaitai_utils import check_recursive
from ...lib.mt_classes import DTI_HASHES, RV_DTI_HASHES, RV_MTPROPERTY_RE5
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

SDL_VAL_TYPES = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 24, 28}
SDL_DATA_STRUCT_SIZES = {   # Padding included
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

    # xml = from_sdl(sdl)
    xml = _sdl_to_xml(sdl)
    ET.indent(xml, space="\t", level=0)
    buffer = io.StringIO()
    xml.write(buffer, encoding="unicode", xml_declaration=True)
    xml_string = buffer.getvalue()
    text = bpy.data.texts.new(bl_object_name + ".xml")
    bl_object["sdl"] = bl_object_name + ".xml"
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
        track_el = ET.Element(
            RV_TRACK_TYPE.get(track.track_type, "TYPE_UNKNOWN"),
            {
                "name": track.name,
                "index": str(track_id),
                "parent": str(track.parent),
                "prop_type": str(getattr(track, "prop_type", 0)),
                "dti_ref": str(getattr(track, "dti_ref", 0)),
            },
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

    ET.SubElement(header_xml, "reserved").text = str(getattr(sdl.header, "reserved", 0))

    top_level_types = {
        TRACK_TYPE["TYPE_ROOT"],
        TRACK_TYPE["TYPE_UNIT"],
        TRACK_TYPE["TYPE_SCHEDULER"],
    }
    for track_id, track in enumerate(sdl.tracks):
        # TYPE_UNIT and TYPE_SCHEDULER store a different link in `parent`;
        # treating it as a tree parent nests units under their own properties.
        # For the remaining track types, `parent` is a zero-based index into
        # the complete track table (including TYPE_ROOT).
        parent_id = None if track.track_type in top_level_types else track.parent
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


def _xml_to_sdl_bytes(root_xml):
    if root_xml.tag != "sdl":
        raise ValueError('SDL XML root must be <sdl>')
    header_xml = root_xml.find("header")
    tracks_xml = root_xml.find("tracks")
    if header_xml is None or tracks_xml is None:
        raise ValueError('SDL XML must contain <header> and <tracks>')

    version = _xml_int(header_xml, "version", 17)
    frame_max = _xml_int(header_xml, "frame_max", 0)
    floor_frame = _xml_int(header_xml, "floor_frame", 0)
    reserved = _xml_int(header_xml, "reserved", 0)
    if not 0 <= frame_max <= 0xFFFFFF:
        raise ValueError("SDL frame_max must fit in 24 bits")
    if floor_frame not in (0, 1):
        raise ValueError("SDL floor_frame must be 0 or 1")
    if not 0 <= reserved <= 0x7F:
        raise ValueError("SDL reserved must fit in 7 bits")

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
            collect_entries(child, len(track_elements) - 1)

    collect_entries(tracks_xml)
    if not track_elements or track_elements[0][0].tag != "TYPE_ROOT":
        raise ValueError("SDL XML tracks must start with a TYPE_ROOT track")

    indexed = [element.get("index") is not None for element, _ in track_elements]
    if any(indexed) and not all(indexed):
        raise ValueError("SDL track index must be specified for every track or none")
    if all(indexed):
        track_elements.sort(key=lambda pair: _xml_int(pair[0], "index"))
        if [_xml_int(element, "index") for element, _ in track_elements] != list(
            range(len(track_elements))
        ):
            raise ValueError("SDL track indices must be unique and contiguous from zero")

    track_count = len(track_elements)
    for element, _ in track_elements:
        name = element.get("name", "")
        encoded_name = name.encode("utf-8")
        if b"\0" in encoded_name:
            raise ValueError("SDL track names cannot contain NUL bytes")

    tracks = []
    track_data = []
    for track_index, (element, structural_parent) in enumerate(track_elements):
        track_type = TRACK_TYPE[element.tag]
        data_entry = []
        data_xml = element.find("data")
        if data_xml is not None:
            data_entry = list(data_xml)

        prop_type_attr = element.get("prop_type")
        if prop_type_attr is None:
            prop_type = next(
                (value for value, name in RV_MTPROPERTY_RE5.items()
                 if data_entry and name == data_entry[0].tag),
                0,
            )
        else:
            prop_type = int(prop_type_attr, 0)
        if data_entry and any(item.tag != RV_MTPROPERTY_RE5.get(prop_type) for item in data_entry):
            raise ValueError(f"Inconsistent property type on SDL track {element.get('name', '')!r}")

        if len(data_entry) > 0xFFFF:
            raise ValueError("SDL tracks cannot contain more than 65535 frames")
        parent_value = element.get("parent")
        if parent_value is not None:
            parent = int(parent_value, 0)
        elif track_type in (TRACK_TYPE["TYPE_ROOT"], TRACK_TYPE["TYPE_UNIT"], TRACK_TYPE["TYPE_SCHEDULER"]):
            parent = 0
        else:
            parent = (structural_parent if structural_parent is not None else 0)
        dti_ref = _sdl_dti_value(element.get("dti_ref", "0"))

        tracks.append({
            "type": track_type,
            "prop_type": prop_type,
            "count": len(data_entry),
            "parent": parent,
            "name": element.get("name", ""),
            "dti_ref": dti_ref,
        })
        track_data.append(data_entry)

    header_size = 20
    tracks_size = track_count * 24
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
        # padding for data blocks
        if has_serialized_data:
            r = cur_track_data % 16
            cur_track_data += (16 - r) % 16
        track["data_offset"] = cur_track_data if has_serialized_data else 0
        if track["data_offset"]:
            # special bool list case
            if track["prop_type"] == 3:
                r = len(data_entry) % 4
                if r == 0:
                    cur_track_data += len(data_entry)
                else:
                    cur_track_data += len(data_entry) + (4 - r)
            else:
                cur_track_data += len(data_entry) * data_struct_size
    while cur_track_data % 4:
        cur_track_data += 1

    cur_names = 0
    name_offsets = {}
    for track in tracks:
        name = track["name"]
        if "\0" in name:
            raise ValueError("SDL track names cannot contain NUL characters")
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

    final_size = cur_track_data + cur_names
    stream = KaitaiStream(io.BytesIO(bytearray(final_size)))
    sdl = Sdl156(stream)
    header = Sdl156.BaseHeader(stream, sdl, sdl)
    header.magic = b"SDL\0"
    header.version = version
    header.num_tracks = track_count
    header.frame_max = frame_max
    header.floor_frame = bool(floor_frame)
    header.reserved = reserved
    header.ofs_dti_table = 0
    header.ofs_names = cur_track_data
    sdl.header = header

    generated_tracks = []
    cur_names = custom_data_offset
    for track, data_entry in zip(tracks, track_data):
        dst_track = Sdl156.Track(stream, sdl, sdl)
        dst_track.track_type = track["type"]
        dst_track.prop_type = track["prop_type"]
        dst_track.num_frames = track["count"]
        dst_track.parent = track["parent"]
        dst_track.ofs_name = name_offsets[track["name"]]
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
                value_offset = (
                    track["data_offset"]
                    + item_index * data_struct_size
                )
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
