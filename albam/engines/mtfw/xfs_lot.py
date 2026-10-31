"""Blender placeholders for object placements stored in MTFW XFS .lot files."""

import json
import math

import bpy
from mathutils import Euler, Matrix, Quaternion


_MARKER_TAG = "_albam_xfs_lot_marker"
_MARKER_PATH = "_albam_xfs_path"
_MARKER_PARENT_PATH = "_albam_xfs_parent_path"
_MARKER_BASELINE = "_albam_xfs_baseline_transform"
_MARKER_MESH_TAG = "_albam_xfs_lot_marker_mesh"


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


def _lot_records(root):
    elements = list(_iter_xml_elements_with_paths(root))
    paths_by_element = {id(element): path for element, path in elements}
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

    def item_entries(element, path, visited=None):
        element, path = resolve_reference(element, path)
        if element is None:
            return
        visited = set() if visited is None else visited
        if path in visited:
            return
        visited.add(path)
        if element.tag == "classref" and has_item_transform(element):
            yield path, element
            return
        for child in element:
            child_path = paths_by_element[id(child)]
            if child.tag in ("classref", "array"):
                yield from item_entries(child, child_path, visited)

    def add_record(element, path):
        if element.tag != "classref":
            return
        element, path = resolve_reference(element, path)
        if element is None:
            return
        unit_class_xml = _named_property(element, "mUnitClass")
        unit_class = (
            unit_class_xml.attrib.get("value", unit_class_xml.text or "")
            if unit_class_xml is not None else ""
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
        for item_path, item_record in item_entries(item_set, item_set_path):
            records[item_path] = (item_record, unit_class, info, info_path)

    for element, path in elements:
        is_mset_infos = (
            element.tag == "array" and element.attrib.get("name", "").casefold() == "msetinfos"
        )
        if is_mset_infos:
            for child in element:
                add_record(child, paths_by_element[id(child)])
        elif (
            element.tag == "classref" and element.attrib.get("name", "").casefold() == "msetinfos"
        ):
            add_record(element, path)

    return records


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
    records = _lot_records(xml.getroot())
    if not records:
        return
    for marker_index, (path, (record, unit_class, info, info_path)) in enumerate(
        records.items()
    ):
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
        marker[_MARKER_PARENT_PATH] = json.dumps(info_path)
        marker["_albam_xfs_unit_class"] = unit_class
        _store_baseline(marker)


def write_xfs_lot_marker_changes(xml_root, bl_object):
    """Copy edited child ``Pos``/``Ang`` values into their source XML nodes."""
    seen_paths = set()
    for marker in bl_object.children_recursive:
        if not marker.get(_MARKER_TAG):
            continue
        path = tuple(json.loads(marker.get(_MARKER_PATH, "[]")))
        if path in seen_paths:
            raise ValueError(f"Duplicate XFS lot placement marker path on {marker.name!r}")
        seen_paths.add(path)
        record = _xml_node_at_path(xml_root, path)
        parent_path = tuple(json.loads(marker.get(_MARKER_PARENT_PATH, "[]")))
        parent = _xml_node_at_path(xml_root, parent_path)
        changes = _transform_changes(marker)

        # cSetInfoItem repeats its child cItemSetInfo transform.
        if "location" in changes:
            location = marker.location
            position = (location.x * 100.0, location.z * 100.0, -location.y * 100.0)
            child_written = _set_xml_vector(
                _named_property(record, "Pos"),
                position,
            )
            parent_written = _set_xml_vector(_position_property(parent), position)
            if not child_written or not parent_written:
                raise ValueError(
                    f"Cannot synchronize Pos and mPosition for {marker.name!r}"
                )
        if "rotation" in changes:
            rotation = marker.matrix_basis.decompose()[1]
            angles = _blender_angle_to_game(rotation)
            child_written = _set_xml_vector(
                _named_property(record, "Ang"),
                angles,
            )
            parent_written = _set_xml_vector(_named_property(parent, "mAngle"), angles)
            if not child_written or not parent_written:
                raise ValueError(
                    f"Cannot synchronize Ang and mAngle for {marker.name!r}"
                )
        if "scale" in changes:
            scale = marker.scale
            if not _set_xml_vector(
                _named_property(parent, "mScale"),
                (scale.x, scale.z, scale.y),
            ):
                raise ValueError(f"Cannot write mScale for XFS lot marker {marker.name!r}")
