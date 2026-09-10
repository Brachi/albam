import bpy
import io
import xml.etree.ElementTree as ET
from ...registry import blender_registry
from ...vfs import VirtualFileData, VirtualFile

from ...lib.xml_parser import from_sdl, to_sdl, from_xfs, to_xfs
from ...lib.mt_classes import RV_DTI_HASHES, RV_MtPropertyTypeRE5
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


def _append_sdl_value_xml(parent_xml, value):
    for field_name, field_value in vars(value).items():
        if field_name.startswith("_") or field_value is None:
            continue

        field_xml = ET.SubElement(parent_xml, field_name)
        if isinstance(field_value, (str, int, float, bool)):
            field_xml.text = str(field_value)
        else:
            _append_sdl_value_xml(field_xml, field_value)


@blender_registry.register_import_function(app_id="re5", extension="sdl", albam_asset_type="CONFIG")
def build_sheduler_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
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
    ET.SubElement(header_xml, "frames").text = str(sdl.header.frames)
    ET.SubElement(header_xml, "floor_frame").text = "0"

    tracks_xml = ET.SubElement(root_xml, "tracks")

    elements = []
    for track_id, track in enumerate(sdl.tracks):
        track_el = ET.Element(
            RV_TRACK_TYPE.get(track.track_type, "TYPE_UNKNOWN"),
            {"name": track.name},
        )
        if track.num_frames > 0:
            data_xml = ET.SubElement(track_el, "data")
            data = track.data or []
            timing_frames = track.timing_frames or []
            for frame_id in range(track.num_frames):
                timing_frame = timing_frames[frame_id]
                item_xml = ET.SubElement(
                    data_xml,
                    RV_MtPropertyTypeRE5.get(track.prop_type, "TYPE_UNKNOWN"),
                    {
                        "frame": str(timing_frame.frame),
                        "type": str(timing_frame.type),
                    },
                )
                if frame_id >= len(data):
                    continue

                value = data[frame_id]
                if track.track_type in (
                    TRACK_TYPE["TYPE_INT"],
                    TRACK_TYPE["TYPE_FLOAT"],
                    TRACK_TYPE["TYPE_BOOL"],
                ):
                    item_xml.set("value", str(value.val))
                elif track.track_type == TRACK_TYPE["TYPE_VECTOR"]:
                    _append_sdl_value_xml(item_xml, value)
                elif track.track_type == TRACK_TYPE["TYPE_RESOURCE"] and value.ref_ofs:
                    item_xml.set("ref_path", value.ref_path)
                    item_xml.set(
                        "ref_dti",
                        RV_DTI_HASHES.get(value.ref_dti, str(value.ref_dti)),
                    )
        elements.append(track_el)

    for track_id, track in enumerate(sdl.tracks):
        parent_id = None if track.track_type == TRACK_TYPE["TYPE_ROOT"] else track.parent - 1
        if parent_id is not None and 0 <= parent_id < len(elements) and parent_id != track_id:
            elements[parent_id].append(elements[track_id])
        else:
            tracks_xml.append(elements[track_id])

    tree = ET.ElementTree(root_xml)
    return tree



@blender_registry.register_export_function(app_id="re5", extension="sdl")
def export_sdl(bl_object):
    vfiles = []
    sdl_name = bl_object.get('sdl', None)
    if sdl_name:
        xml = bpy.data.texts[sdl_name]
        xml_string = xml.as_string()
        tree = ET.fromstring(xml_string)
        out_data = to_sdl(tree)
        vfiles.append(out_data)

    return vfiles



@blender_registry.register_import_function(app_id="re5", extension="lot", albam_asset_type="CONFIG")
def build_xfs_object(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    app_id = vfile.app_id
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
