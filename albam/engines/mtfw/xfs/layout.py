"""Blender placeholders for object placements stored in MTFW XFS .lot files."""

import copy
import json
import math
import xml.etree.ElementTree as ET

import bpy
from mathutils import Euler, Matrix, Quaternion

from ....lib.stage_placer.re5_item_ids import (
    enum_items,
    get_item_class,
    get_item_name,
    get_item_type,
    get_item_types,
)
from ....registry import blender_registry


_MARKER_TAG = "_albam_xfs_lot_marker"
_MARKER_PATH = "_albam_xfs_path"
_MARKER_UNIT_CLASS_PATH = "_albam_xfs_unit_class_path"
_MARKER_UNIT_CLASS = "_albam_xfs_unit_class"
_MARKER_ITEM_ID_PATH = "_albam_xfs_item_id_path"
_MARKER_ITEM_ID = "_albam_xfs_item_id"
_MARKER_BASELINE = "_albam_xfs_baseline_transform"
_MARKER_MESH_TAG = "_albam_xfs_lot_marker_mesh"
def _item_type_identifier(item_type):
    if not item_type:
        return "UNCATEGORIZED"
    normalized = "".join(
        char if char.isalnum() else "_" for char in item_type.upper()
    ).strip("_")
    return f"TYPE_{normalized}"


_ITEM_TYPE_BY_IDENTIFIER = {
    _item_type_identifier(item_type): item_type
    for item_type in get_item_types()
}
_ITEM_TYPE_ENUM_ITEMS = tuple(
    (
        identifier,
        item_type.title() if item_type else "Uncategorized",
        f"Show {item_type or 'uncategorized'} Item IDs",
    )
    for identifier, item_type in _ITEM_TYPE_BY_IDENTIFIER.items()
)
_ITEM_ENUM_ITEMS_BY_TYPE = {
    item_type: tuple(enum_items(item_type=item_type))
    for item_type in _ITEM_TYPE_BY_IDENTIFIER.values()
}
_ITEM_ENUM_ITEMS_BY_TYPE[None] = tuple(enum_items())
_PRESERVED_ITEM_ENUM_ITEMS = {}


def _item_type_enum_items(_properties, _context):
    return _ITEM_TYPE_ENUM_ITEMS


def _item_id_enum_items(properties, _context):
    bl_object = properties.id_data
    item_type = _ITEM_TYPE_BY_IDENTIFIER.get(properties.item_type)
    enum_items_for_type = _ITEM_ENUM_ITEMS_BY_TYPE.get(
        item_type, _ITEM_ENUM_ITEMS_BY_TYPE[None]
    )
    items = list(enum_items_for_type)
    listed_ids = {item[0] for item in items}
    current_id = str(bl_object.get(_MARKER_ITEM_ID, ""))
    if current_id and current_id not in listed_ids:
        # Keep dynamically-created strings alive for Blender's EnumProperty.
        item = _PRESERVED_ITEM_ENUM_ITEMS.get(current_id)
        if item is None:
            try:
                numeric_id = int(current_id)
            except (TypeError, ValueError):
                numeric_id = None
            unit_class = (
                get_item_class(numeric_id) if numeric_id is not None else None
            )
            readable_name = get_item_name(numeric_id) if numeric_id is not None else ""
            if unit_class is not None:
                label = f"{current_id} — {unit_class}"
                if readable_name:
                    label += f" ({readable_name})"
                label += " (outside selected category)"
                description = "Current Item ID; changing it replaces this value"
            elif readable_name:
                label = f"{current_id} — {readable_name} (no class mapping)"
                description = "No class mapping is known; the original ID is preserved on export"
            else:
                label = f"{current_id} — unknown (preserve)"
                description = "Unknown ID; the original value is preserved on export"
            item = (
                current_id,
                label,
                description,
            )
            _PRESERVED_ITEM_ENUM_ITEMS[current_id] = item
        items.append(item)
    return items


def _item_id_updated(properties, context):
    bl_object = properties.id_data
    item_id_text = properties.item_id
    bl_object[_MARKER_ITEM_ID] = item_id_text
    try:
        unit_class = get_item_class(int(item_id_text))
    except (TypeError, ValueError):
        unit_class = None
    if unit_class is None:
        return

    bl_object[_MARKER_UNIT_CLASS] = unit_class
    if bl_object.type == "MESH" and context is not None:
        bl_object.data = _marker_mesh(unit_class, context)


@blender_registry.register_custom_properties_object(
    "lot_placement", ("re5",), asset_type="CONFIG"
)
@blender_registry.register_blender_prop
class XFSLotPlacementProperties(bpy.types.PropertyGroup):
    item_type: bpy.props.EnumProperty(
        name="Item Type",
        description="Filter the available RE5 Item IDs",
        items=_item_type_enum_items,
    )
    item_id: bpy.props.EnumProperty(
        name="Item ID",
        description="RE5 item spawned by this LOT placement",
        items=_item_id_enum_items,
        update=_item_id_updated,
    )


def _iter_xml_elements_with_paths(element, path=()):
    yield element, path
    for index, child in enumerate(element):
        yield from _iter_xml_elements_with_paths(child, path + (index,))


def _xml_node_at_path(root, path):
    node = root
    for index in path:
        children = list(node)
        if index >= len(children):
            raise ValueError(f"XFS XML node path {path!r} no longer exists")
        node = children[index]
    return node


def _named_property(class_xml, name):
    name = name.casefold()
    return next(
        (
            child for child in class_xml
            if child.attrib.get("name", "").casefold() == name
        ),
        None,
    )


def _position_property(class_xml):
    position = _named_property(class_xml, "mPosition")
    if position is None:
        position = _named_property(class_xml, "Position")
    return position


def _xml_vector(node):
    if node is None:
        return None
    component_names = ("x", "y", "z")
    if not all(name in node.attrib for name in component_names):
        return None
    try:
        return tuple(float(node.attrib[name]) for name in component_names)
    except ValueError:
        return None


def _set_xml_vector(node, values):
    if node is None or not all(name in node.attrib for name in ("x", "y", "z")):
        return False
    for name, value in zip(("x", "y", "z"), values):
        node.set(name, repr(float(value)))
    return True


def _lot_record_locations(root):
    elements = list(_iter_xml_elements_with_paths(root))
    paths_by_element = {id(element): path for element, path in elements}
    elements_by_path = {path: element for element, path in elements}
    inline_objects = {
        element.attrib["id"]: (element, path)
        for element, path in elements
        if element.tag == "classref" and "id" in element.attrib and len(element)
    }
    records = {}

    def resolve_reference(element, path):
        if not len(element) and "ref" in element.attrib:
            target = inline_objects.get(element.attrib["ref"])
            if target is None:
                return None, None
            return target
        return element, path

    def has_item_transform(element):
        return (
            _xml_vector(_named_property(element, "Pos")) is not None and
            _xml_vector(_named_property(element, "Ang")) is not None
        )

    def item_entries(
        element, path, visited=None, container_path=None, entry_path=None
    ):
        if element.tag == "array":
            for child in element:
                child_path = paths_by_element[id(child)]
                yield from item_entries(
                    child, child_path, visited,
                    container_path=path, entry_path=child_path,
                )
            return

        element, path = resolve_reference(element, path)
        if element is None:
            return
        visited = set() if visited is None else visited
        if path in visited:
            return
        visited.add(path)
        if element.tag == "classref" and has_item_transform(element):
            yield path, element, container_path, entry_path
            return
        for child in element:
            child_path = paths_by_element[id(child)]
            if child.tag in ("classref", "array"):
                yield from item_entries(
                    child, child_path, visited, container_path, entry_path
                )

    def add_record(element, path, set_info_container=None):
        if element.tag != "classref":
            return
        set_info_entry = element
        set_info_entry_path = path
        set_info_parent = elements_by_path.get(path[:-1])
        element, path = resolve_reference(element, path)
        if element is None:
            return
        set_info = element
        set_info_path = path
        unit_class_xml = _named_property(element, "mUnitClass")
        unit_class = (
            unit_class_xml.attrib.get("value", unit_class_xml.text or "")
            if unit_class_xml is not None else ""
        )
        unit_class_path = (
            paths_by_element[id(unit_class_xml)] if unit_class_xml is not None else None
        )
        info = _named_property(element, "mpInfo")
        if info is None or info.tag != "classref":
            return
        info_path = paths_by_element[id(info)]
        info, info_path = resolve_reference(info, info_path)
        if info is None:
            return
        item_set = _named_property(info, "mItemSet")
        if item_set is None:
            return
        item_set_path = paths_by_element[id(item_set)]
        for (
            item_path, item_record, item_container_path, item_entry_path
        ) in item_entries(item_set, item_set_path):
            item_id_xml = _named_property(item_record, "ItemId")
            try:
                item_id = int(item_id_xml.attrib.get("value"))
            except (AttributeError, TypeError, ValueError):
                item_id = None
            item_id_path = (
                paths_by_element[id(item_id_xml)] if item_id_xml is not None else None
            )
            records[item_path] = {
                "values": (
                    item_record, unit_class, info, info_path, unit_class_path,
                    item_id, item_id_path,
                ),
                "set_info": set_info,
                "set_info_path": set_info_path,
                "set_info_entry": set_info_entry,
                "set_info_entry_path": set_info_entry_path,
                "set_info_container": set_info_container,
                "set_info_parent": set_info_parent,
                "item_container_path": item_container_path,
                "item_entry_path": item_entry_path,
                "item_container": elements_by_path.get(item_container_path),
                "item_entry": elements_by_path.get(item_entry_path),
            }

    for element, path in elements:
        is_mset_infos = (
            element.tag == "array" and element.attrib.get("name", "").casefold() == "msetinfos"
        )
        if is_mset_infos:
            for child in element:
                add_record(child, paths_by_element[id(child)], element)
        elif (
            element.tag == "classref" and element.attrib.get("name", "").casefold() == "msetinfos"
        ):
            add_record(element, path)

    return records


def _lot_records(root):
    """Return the original marker data without the XML insertion locations."""
    return {
        path: location["values"]
        for path, location in _lot_record_locations(root).items()
    }


def _marker_material(tag, name, color):
    for material in bpy.data.materials:
        if material.get(tag):
            return material

    material = bpy.data.materials.new(name)
    material[tag] = True
    material.diffuse_color = color
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = 0.38
    return material


def _font_geometry(text, context):
    curve = bpy.data.curves.new("ALBAM XFS lot marker label", type="FONT")
    curve.body = text
    curve.size = 0.16
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    temporary_object = bpy.data.objects.new("ALBAM XFS lot marker label", curve)
    context.collection.objects.link(temporary_object)
    try:
        depsgraph = context.evaluated_depsgraph_get()
        evaluated_object = temporary_object.evaluated_get(depsgraph)
        text_mesh = bpy.data.meshes.new_from_object(
            evaluated_object, depsgraph=depsgraph
        )
        vertices = [
            (-vertex.co.x, -vertex.co.y, vertex.co.z + 0.62)
            for vertex in text_mesh.vertices
        ]
        faces = [tuple(polygon.vertices) for polygon in text_mesh.polygons]
        bpy.data.meshes.remove(text_mesh)
        return vertices, faces
    finally:
        bpy.data.objects.remove(temporary_object, do_unlink=True)
        bpy.data.curves.remove(curve)


def _marker_mesh(unit_class, context):
    for mesh in bpy.data.meshes:
        if mesh.get(_MARKER_MESH_TAG) == unit_class:
            return mesh

    vertices = []
    faces = []
    material_indices = []

    def add_box_beam(start_point, end_point, width):
        half = width / 2.0
        minimum = [min(a, b) for a, b in zip(start_point, end_point)]
        maximum = [max(a, b) for a, b in zip(start_point, end_point)]
        axis = next(i for i in range(3) if minimum[i] != maximum[i])
        for i in range(3):
            if i != axis:
                minimum[i] -= half
                maximum[i] += half

        x0, y0, z0 = minimum
        x1, y1, z1 = maximum
        offset = len(vertices)
        vertices.extend((
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
        ))
        faces.extend(tuple(offset + i for i in face) for face in (
            (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
            (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        ))
        material_indices.extend([0] * 6)

    corners = (
        (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5),
        (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5),
        (0.5, -0.5, -0.5), (0.5, -0.5, 0.5),
        (0.5, 0.5, -0.5), (0.5, 0.5, 0.5),
    )
    box_edges = (
        (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
        (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7),
    )
    for start_index, end_index in box_edges:
        add_box_beam(corners[start_index], corners[end_index], 0.012)

    arrow_face_start = len(faces)
    segments = 10

    def add_cylinder_y(y_start, y_end, radius):
        start = len(vertices)
        for y in (y_start, y_end):
            for index in range(segments):
                angle = (2.0 * math.pi * index) / segments
                vertices.append((radius * math.cos(angle), y,
                                 radius * math.sin(angle)))
        for index in range(segments):
            next_index = (index + 1) % segments
            if y_end >= y_start:
                faces.append((start + index, start + segments + index,
                              start + segments + next_index, start + next_index))
            else:
                faces.append((start + index, start + next_index,
                              start + segments + next_index, start + segments + index))
        if y_end >= y_start:
            faces.append(tuple(start + index for index in range(segments)))
            faces.append(tuple(start + segments + index for index in reversed(range(segments))))
        else:
            faces.append(tuple(start + index for index in reversed(range(segments))))
            faces.append(tuple(start + segments + index for index in range(segments)))

    def add_cone_y(y_base, y_tip, radius):
        start = len(vertices)
        for index in range(segments):
            angle = (2.0 * math.pi * index) / segments
            vertices.append((radius * math.cos(angle), y_base,
                             radius * math.sin(angle)))
        tip = len(vertices)
        vertices.append((0.0, y_tip, 0.0))
        for index in range(segments):
            next_index = (index + 1) % segments
            if y_tip >= y_base:
                faces.append((start + index, tip, start + next_index))
            else:
                faces.append((start + index, start + next_index, tip))
        faces.append(tuple(start + index for index in range(segments)))

    # The arrow starts at the placement origin and points along Blender's local Y+.
    add_cylinder_y(0.0, 0.40, 0.055)
    add_cone_y(0.38, 0.88, 0.17)
    material_indices.extend([1] * (len(faces) - arrow_face_start))

    if unit_class:
        text_vertices, text_faces = _font_geometry(unit_class, context)
        text_offset = len(vertices)
        vertices.extend(text_vertices)
        faces.extend(
            tuple(text_offset + vertex_index for vertex_index in face)
            for face in text_faces
        )
        material_indices.extend([2] * len(text_faces))

    mesh = bpy.data.meshes.new("ALBAM XFS lot placement marker")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(_marker_material(
        "_albam_xfs_lot_box_material", "ALBAM XFS lot box", (1.0, 0.22, 0.025, 1.0)
    ))
    mesh.materials.append(_marker_material(
        "_albam_xfs_lot_arrow_material", "ALBAM XFS lot arrow", (0.04, 0.85, 0.12, 1.0)
    ))
    mesh.materials.append(_marker_material(
        "_albam_xfs_lot_text_material", "ALBAM XFS lot label", (1.0, 1.0, 1.0, 1.0)
    ))
    for polygon, material_index in zip(mesh.polygons, material_indices):
        polygon.material_index = material_index
    mesh.update()
    mesh[_MARKER_MESH_TAG] = unit_class
    return mesh


def _game_angle_to_blender(angles):
    basis = Matrix.Rotation(math.pi / 2.0, 4, "X")
    game_rotation = Euler(angles, "XYZ").to_matrix().to_4x4()
    return (basis @ game_rotation @ basis.inverted()).to_euler("XYZ")


def _blender_angle_to_game(blender_rotation):
    basis = Matrix.Rotation(math.pi / 2.0, 4, "X")
    blender_matrix = blender_rotation.to_matrix().to_4x4()
    return (basis.inverted() @ blender_matrix @ basis).to_euler("XYZ")


def _store_baseline(bl_object):
    bl_object[_MARKER_BASELINE] = json.dumps({
        "location": list(bl_object.location),
        "rotation": list(bl_object.rotation_quaternion),
        "scale": list(bl_object.scale),
    })


def _transform_changes(bl_object):
    baseline_text = bl_object.get(_MARKER_BASELINE)
    if not baseline_text:
        return {"location", "rotation", "scale"}
    baseline = json.loads(baseline_text)
    location, rotation, scale = bl_object.matrix_basis.decompose()
    baseline_rotation = Quaternion(baseline["rotation"])
    rotation.normalize()
    baseline_rotation.normalize()
    changes = set()
    if any(
        not math.isclose(
            float(value), float(original), rel_tol=1e-7, abs_tol=1e-7
        )
        for value, original in zip(location, baseline["location"])
    ):
        changes.add("location")
    if any(
        not math.isclose(
            float(value), float(original), rel_tol=1e-7, abs_tol=1e-7
        )
        for value, original in zip(scale, baseline["scale"])
    ):
        changes.add("scale")
    if 1.0 - abs(rotation.dot(baseline_rotation)) > 1e-8:
        changes.add("rotation")
    return changes


def build_xfs_lot_markers(bl_object, xml, context):
    """Create viewport markers for child ``mItemSet`` placements in ``mSetInfos``."""
    records = _lot_record_locations(xml.getroot())
    if not records:
        return
    for marker_index, (
        path, location,
    ) in enumerate(records.items()):
        (
            record, xml_unit_class, info, info_path, unit_class_path,
            item_id, item_id_path,
        ) = location["values"]
        unit_class = get_item_class(item_id, default=xml_unit_class)
        position = _xml_vector(_named_property(record, "Pos"))
        angles = _xml_vector(_named_property(record, "Ang"))
        parent_scale = _xml_vector(_named_property(info, "mScale")) or (1, 1, 1)
        marker_mesh = _marker_mesh(unit_class, context)

        marker = bpy.data.objects.new(
            f"{bl_object.name}_SetInfo_{marker_index:03d}",
            marker_mesh,
        )
        marker.parent = bl_object
        marker.location = (
            position[0] / 100.0,
            -position[2] / 100.0,
            position[1] / 100.0,
        )
        marker.rotation_mode = "XYZ"
        marker.rotation_euler = _game_angle_to_blender(angles)
        marker.scale = (parent_scale[0], parent_scale[2], parent_scale[1])
        marker.display_type = "SOLID"
        marker.show_in_front = True
        marker.hide_render = True
        marker[_MARKER_TAG] = True
        marker[_MARKER_PATH] = json.dumps(path)
        if unit_class_path is not None:
            marker[_MARKER_UNIT_CLASS_PATH] = json.dumps(unit_class_path)
        marker[_MARKER_UNIT_CLASS] = unit_class
        if item_id_path is not None:
            marker[_MARKER_ITEM_ID_PATH] = json.dumps(item_id_path)
        if item_id is not None:
            marker[_MARKER_ITEM_ID] = str(item_id)
            marker_properties = marker.albam_custom_properties.re5__lot_placement
            marker_properties.item_id = str(item_id)
            item_type = get_item_type(item_id)
            item_type_identifier = _item_type_identifier(item_type)
            if item_type_identifier in _ITEM_TYPE_BY_IDENTIFIER:
                marker_properties.item_type = item_type_identifier
        _store_baseline(marker)


def _write_marker_values(record, parent, unit_class_node, marker):
    changes = _transform_changes(marker)
    item_id_path_json = marker.get(_MARKER_ITEM_ID_PATH)
    item_id_text = str(marker.get(_MARKER_ITEM_ID, ""))
    if item_id_path_json and item_id_text:
        item_id_node = _named_property(record, "ItemId")
        if item_id_node is None:
            raise ValueError(f"Missing ItemId for XFS lot marker {marker.name!r}")
        try:
            item_id = int(item_id_text)
        except ValueError:
            raise ValueError(
                f"Invalid ItemId {item_id_text!r} on XFS lot marker {marker.name!r}"
            ) from None
        if "value" in item_id_node.attrib:
            item_id_node.set("value", str(item_id))
        else:
            item_id_node.text = str(item_id)

        mapped_unit_class = get_item_class(item_id)
        if mapped_unit_class is not None and unit_class_node is not None:
            if "value" in unit_class_node.attrib:
                unit_class_node.set("value", mapped_unit_class)
            else:
                unit_class_node.text = mapped_unit_class

    if unit_class_node is not None and "mUnitClass" in marker and not item_id_path_json:
        unit_class = str(marker["mUnitClass"])
        if "value" in unit_class_node.attrib:
            unit_class_node.set("value", unit_class)
        else:
            unit_class_node.text = unit_class

    # cSetInfoItem repeats its child cItemSetInfo transform.
    if "location" in changes:
        location = marker.location
        position = (location.x * 100.0, location.z * 100.0, -location.y * 100.0)
        child_written = _set_xml_vector(_named_property(record, "Pos"), position)
        parent_written = _set_xml_vector(_position_property(parent), position)
        if not child_written or not parent_written:
            raise ValueError(f"Cannot synchronize Pos and mPosition for {marker.name!r}")
    if "rotation" in changes:
        rotation = marker.matrix_basis.decompose()[1]
        angles = _blender_angle_to_game(rotation)
        child_written = _set_xml_vector(_named_property(record, "Ang"), angles)
        parent_written = _set_xml_vector(_named_property(parent, "mAngle"), angles)
        if not child_written or not parent_written:
            raise ValueError(f"Cannot synchronize Ang and mAngle for {marker.name!r}")
    if "scale" in changes:
        scale = marker.scale
        if not _set_xml_vector(
            _named_property(parent, "mScale"), (scale.x, scale.z, scale.y)
        ):
            raise ValueError(f"Cannot write mScale for XFS lot marker {marker.name!r}")


def _ensure_set_info_array(location, xml_root):
    container = location["set_info_container"]
    if container is not None:
        return container

    entry = location["set_info_entry"]
    parent = location["set_info_parent"]
    if parent is None or entry not in list(parent):
        raise ValueError("Cannot find the mSetInfos array for this marker")

    attributes = {
        key: value for key, value in entry.attrib.items()
        if key in {"name", "flags", "size", "reserved"}
    }
    property_type = None
    class_index = parent.attrib.get("class_index")
    property_name = entry.attrib.get("name", "mSetInfos")
    metadata = xml_root.find("_xfs_metadata")
    if metadata is not None and class_index is not None and property_name:
        for class_def in metadata.findall("class_def"):
            if class_def.attrib.get("index") != class_index:
                continue
            property_def = next(
                (
                    prop for prop in class_def.findall("property")
                    if prop.attrib.get("name") == property_name
                ),
                None,
            )
            if property_def is not None:
                property_type = property_def.attrib.get("type_id")
            break
    attributes["name"] = property_name
    attributes["type"] = property_type or "classref"
    array = ET.Element("array", attrib=attributes)
    children = list(parent)
    index = children.index(entry)
    parent.remove(entry)
    array.append(entry)
    parent.insert(index, array)
    location["set_info_container"] = array
    location["set_info_entry"] = entry
    return array


def _clone_inline_record(record, xml_root):
    duplicate = copy.deepcopy(record)
    next_id = max(
        (int(element.attrib["id"]) for element in xml_root.iter()
         if element.tag == "classref" and "id" in element.attrib),
        default=0,
    ) + 1
    id_map = {}
    for element in duplicate.iter():
        old_id = element.attrib.get("id")
        if old_id is not None:
            id_map[old_id] = str(next_id)
            next_id += 1
    for element in duplicate.iter():
        if element.attrib.get("id") in id_map:
            element.set("id", id_map[element.attrib["id"]])
        if element.attrib.get("ref") in id_map:
            element.set("ref", id_map[element.attrib["ref"]])
    return duplicate


def _path_relative_to(path, root_path, label):
    if path is None or path[:len(root_path)] != root_path:
        raise ValueError(
            f"Cannot safely duplicate this XFS lot placement: {label} is outside mSetInfos"
        )
    return path[len(root_path):]


def _remove_item_entry(location):
    container = location["item_container"]
    entry = location["item_entry"]
    if container is None or entry is None or entry not in list(container):
        raise ValueError("Cannot remove this mItemSet entry safely")
    container.remove(entry)


def _duplicate_set_info(
    location, record_path, marker, xml_root, prune_to_item_entry=False
):
    clone = _clone_inline_record(location["set_info"], xml_root)
    set_info_path = location["set_info_path"]
    values = location["values"]
    info_path, unit_class_path = values[3], values[4]
    record_relative_path = _path_relative_to(record_path, set_info_path, "mItemSet")
    if prune_to_item_entry:
        container_path = location["item_container_path"]
        entry_path = location["item_entry_path"]
        if container_path is None or entry_path is None:
            raise ValueError("Cannot isolate this mItemSet entry for duplication")
        cloned_container = _xml_node_at_path(
            clone,
            _path_relative_to(container_path, set_info_path, "mItemSet array"),
        )
        cloned_entry = _xml_node_at_path(
            clone,
            _path_relative_to(entry_path, set_info_path, "mItemSet entry"),
        )
        if cloned_entry not in list(cloned_container):
            raise ValueError("Cannot isolate this mItemSet entry for duplication")
        for child in list(cloned_container):
            if child is not cloned_entry:
                cloned_container.remove(child)
    cloned_record = _xml_node_at_path(
        clone,
        record_relative_path,
    )
    cloned_info = _xml_node_at_path(
        clone,
        _path_relative_to(info_path, set_info_path, "mpInfo"),
    )
    cloned_unit_class = None
    if unit_class_path is not None:
        cloned_unit_class = _xml_node_at_path(
            clone,
            _path_relative_to(unit_class_path, set_info_path, "mUnitClass"),
        )
    _write_marker_values(cloned_record, cloned_info, cloned_unit_class, marker)
    return clone


def write_xfs_lot_marker_changes(xml_root, bl_object):
    """Apply marker edits, additions, and deletions to the source XFS XML."""
    records = _lot_record_locations(xml_root)
    markers_by_path = {}
    for marker in bl_object.children_recursive:
        if marker.get(_MARKER_TAG):
            path = tuple(json.loads(marker.get(_MARKER_PATH, "[]")))
            markers_by_path.setdefault(path, []).append(marker)

    unknown_paths = set(markers_by_path).difference(records)
    if unknown_paths:
        raise ValueError(f"XFS lot marker source paths no longer exist: {sorted(unknown_paths)}")

    paths_by_set_info = {}
    for path, location in records.items():
        paths_by_set_info.setdefault(location["set_info_entry_path"], []).append(path)

    # Update each source record from one surviving marker. Further markers with
    # the same source path are Blender duplicates and become new XML entries.
    for path, markers in markers_by_path.items():
        (
            record, _unit_class, parent, _parent_path, unit_class_path, *_
        ) = records[path]["values"]
        unit_class_node = (
            _xml_node_at_path(xml_root, tuple(unit_class_path))
            if unit_class_path is not None else None
        )
        _write_marker_values(record, parent, unit_class_node, markers[0])

    # Each additional marker represents a new placement. Copy the complete
    # mSetInfos entry so its class, info object, item set, and transforms stay
    # independent from the source placement.
    for path, markers in markers_by_path.items():
        location = records[path]
        if len(markers) < 2:
            continue
        container = _ensure_set_info_array(location, xml_root)
        prune_to_item_entry = len(
            paths_by_set_info[location["set_info_entry_path"]]
        ) > 1
        for marker in markers[1:]:
            container.append(
                _duplicate_set_info(
                    location, path, marker, xml_root,
                    prune_to_item_entry=prune_to_item_entry,
                )
            )

    # Remove one mItemSet entry when its mSetInfos row contains other markers;
    # remove the whole row when this was its only placement. Do this after
    # cloning so the source child paths still have their original indexes.
    for source_paths in paths_by_set_info.values():
        location = records[source_paths[0]]
        active_paths = [path for path in source_paths if path in markers_by_path]
        if len(active_paths) == len(source_paths):
            continue
        if active_paths:
            for path in source_paths:
                if path not in markers_by_path:
                    _remove_item_entry(records[path])
            continue

        entry = location["set_info_entry"]
        container = _ensure_set_info_array(location, xml_root)
        if entry not in list(container):
            raise ValueError("Cannot remove the deleted mSetInfos entry")
        container.remove(entry)
