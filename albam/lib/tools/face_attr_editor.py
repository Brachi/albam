import bpy
import bmesh
import gpu
import blf
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from ..misc import number_to_color

TARGET_TOOL = "albam.face_prop_edit"
_handler = None
# shader = gpu.shader.from_builtin("UNIFORM_COLOR")
shader = None


def get_selected_face_attributes():
    attrs = ('type', 'surface_attr', 'special_attr')
    obj = bpy.context.object
    mode = bpy.context.mode
    if mode != 'EDIT_MESH':
        return {}
    if obj is None or obj.type != 'MESH':
        return {}
    bm = bmesh.from_edit_mesh(obj.data)
    for attr in attrs:
        if not any(layer.name == attr for layer in bm.faces.layers.int):
            bm.faces.layers.int.new(attr)
    face = next((f for f in bm.faces if f.select), None)
    if face is None:
        return {}

    return {layer.name: face[layer] for layer in bm.faces.layers.int}


def draw_callback():
    font_id = 0

    obj = bpy.context.active_object
    face_attrs = get_selected_face_attributes()
    ftype = face_attrs.get('type', 'N/A')
    fsurface = face_attrs.get('surface_attr', 'N/A')
    fbehavior = face_attrs.get('special_attr', 'N/A')
    if obj and obj.type == 'MESH':

        text = (
            f"Type: {ftype}\n"
            f"Surface attribute: {fsurface}\n"
            f"Behavior attribute: {fbehavior }"
        )

        y = 100

        for line in text.splitlines():
            blf.position(font_id, 80, y, 0)
            blf.size(font_id, 14)
            blf.draw(font_id, line)
            y -= 18


def show():
    global _handler

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback,
            (),
            'WINDOW',
            'POST_PIXEL',
        )

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def hide():
    global _handler

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            _handler,
            'WINDOW',
        )
        _handler = None

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def check_active_tool():
    if not getattr(bpy.context, "workspace", None):
        return 0.1
    current_mode = bpy.context.mode
    tool = bpy.context.workspace.tools.from_space_view3d_mode(current_mode, create=False)
    tool_id = tool.idname if tool else None

    if tool_id == TARGET_TOOL:
        show()
    else:
        hide()

    return 0.1


def build_batches(bl_obj):
    if bl_obj is None or bl_obj.type != 'MESH':
        return {}

    mesh = bl_obj.data
    mesh.calc_loop_triangles()

    groups = {}

    for tri in mesh.loop_triangles:
        poly = mesh.polygons[tri.polygon_index]
        material_index = poly.material_index

        vertices = groups.setdefault(material_index, [])

        for vertex_index in tri.vertices:
            co = bl_obj.matrix_world @ mesh.vertices[vertex_index].co
            vertices.append(tuple(co))

    batches = {}

    for material_index, vertices in groups.items():
        batches[material_index] = batch_for_shader(
            shader,
            "TRIS",
            {"pos": vertices},
        )
    wire_vertices = []

    for tri in mesh.loop_triangles:
        a, b, c = tri.vertices

        va = tuple(bl_obj.matrix_world @ mesh.vertices[a].co)
        vb = tuple(bl_obj.matrix_world @ mesh.vertices[b].co)
        vc = tuple(bl_obj.matrix_world @ mesh.vertices[c].co)

        wire_vertices.extend([
            va, vb,
            vb, vc,
            vc, va,
        ])

    wire_batch = batch_for_shader(
        shader,
        "LINES",
        {"pos": wire_vertices},
    )

    return batches, wire_batch


def draw(bfaces, bwires):
    shader.bind()
    gpu.state.blend_set("ALPHA")
    gpu.state.depth_test_set("NONE")

    # faces
    for material_index, batch in bfaces.items():
        shader.uniform_float(
            "color",
            number_to_color(material_index),
        )

        batch.draw(shader)
    # wireframe
    shader.uniform_float("color", (0.0, 0.0, 0.0, 1.0))
    bwires.draw(shader)

    gpu.state.blend_set("NONE")


def draw_text(bl_ob, region, rv3d):
    if bl_ob is None or bl_ob.type != 'MESH':
        return
    font_id = 0
    for poly in bl_ob.data.polygons:
        co = poly.center
        # to world coord
        world_co = bl_ob.matrix_world @ co
        # 3D -> 2D viewport
        screen_co = location_3d_to_region_2d(
            region,
            rv3d,
            world_co,
        )
        if screen_co is None:
            continue
        x, y = screen_co
        # draw the text
        blf.position(font_id, x, y, 0)
        blf.size(font_id, 20)

        blf.draw(
            font_id,
            str(poly.material_index),
        )


_draw_face_handle = None
_draw_text_handle = None


def overlay_enable(bl_object, region, rv3d):
    global _draw_face_handle
    global _draw_text_handle

    if _draw_face_handle is not None and _draw_text_handle is not None:
        return

    faces, wires = build_batches(bl_object)
    _draw_face_handle = bpy.types.SpaceView3D.draw_handler_add(
        draw,
        (faces, wires),
        "WINDOW",
        "POST_VIEW",
    )

    _draw_text_handle = bpy.types.SpaceView3D.draw_handler_add(
        draw_text,
        (bl_object, region, rv3d),
        "WINDOW",
        "POST_PIXEL",
    )
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def overlay_disable():
    global _draw_face_handle
    global _draw_text_handle

    if _draw_face_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            _draw_face_handle,
            "WINDOW",
        )
        _draw_face_handle = None

    if _draw_text_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            _draw_text_handle,
            "WINDOW",
        )
        _draw_text_handle = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
