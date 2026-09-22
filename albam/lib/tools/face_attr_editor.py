import bpy
import bmesh
import blf

TARGET_TOOL = "albam.face_prop_edit"
_handler = None


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
    # Registered once for the addon's lifetime and only runs when Blender
    # actually redraws the viewport - custom WorkSpaceTool.setup()/teardown()
    # staticmethods are never called by Blender's tool system (register_tool()
    # only ever reads idname/label/description/icon/cursor/options/widget/
    # widget_properties/keymap/data_block/operator/draw_settings/draw_cursor
    # off the class), so there's no lifecycle hook to toggle this on/off with.
    workspace = getattr(bpy.context, "workspace", None)
    if workspace is None:
        return
    tool = workspace.tools.from_space_view3d_mode(bpy.context.mode, create=False)
    if not tool or tool.idname != TARGET_TOOL:
        return

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
            f"Behavior attribute: {fbehavior}"
        )

        y = 100

        for line in text.splitlines():
            blf.position(font_id, 80, y, 0)
            blf.size(font_id, 14)
            blf.draw(font_id, line)
            y -= 18


def register_overlay():
    global _handler

    if _handler is None:
        _handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback,
            (),
            'WINDOW',
            'POST_PIXEL',
        )


def unregister_overlay():
    global _handler

    if _handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(
            _handler,
            'WINDOW',
        )
        _handler = None
