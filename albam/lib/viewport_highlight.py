"""Shared viewport highlighting for generated preview objects."""

HIGHLIGHT_COLOR = (0.025, 0.12, 0.62, 1.0)
_BASE_COLOR = "_albam_viewport_highlight_base_color"
_BASE_SHOW_WIRE = "_albam_viewport_highlight_base_show_wire"
_BASE_SHOW_ALL_EDGES = "_albam_viewport_highlight_base_show_all_edges"
_BASE_SHOW_IN_FRONT = "_albam_viewport_highlight_base_show_in_front"


def set_active_preview_highlight(
        preview_objects, active_object=None, *, active_objects=None):
    """Highlight selected generated previews and restore the rest to base state."""
    preview_objects = tuple(obj for obj in preview_objects if obj is not None)
    selected_objects = active_objects
    if selected_objects is None:
        selected_objects = (active_object,) if active_object is not None else ()
    selected_ids = {obj.as_pointer() for obj in selected_objects if obj is not None}
    for preview_object in preview_objects:
        _store_base_state(preview_object)
        highlighted = preview_object.as_pointer() in selected_ids

        values = (
            ("show_wire", highlighted or preview_object[_BASE_SHOW_WIRE]),
            ("show_all_edges", highlighted or preview_object[_BASE_SHOW_ALL_EDGES]),
            ("show_in_front", highlighted or preview_object[_BASE_SHOW_IN_FRONT]),
            ("color", HIGHLIGHT_COLOR if highlighted else tuple(preview_object[_BASE_COLOR])),
        )
        for property_name, value in values:
            current_value = getattr(preview_object, property_name)
            changed = (tuple(current_value) != tuple(value)
                       if property_name == "color" else current_value != value)
            if changed:
                setattr(preview_object, property_name, value)


def _store_base_state(preview_object):
    if _BASE_COLOR in preview_object:
        return
    preview_object[_BASE_COLOR] = list(preview_object.color)
    if preview_object.get("_albam_ccl_preview", False):
        base_show_wire, base_show_all_edges, base_show_in_front = False, False, False
    else:
        base_show_wire = preview_object.show_wire
        base_show_all_edges = preview_object.show_all_edges
        base_show_in_front = preview_object.show_in_front
    preview_object[_BASE_SHOW_WIRE] = base_show_wire
    preview_object[_BASE_SHOW_ALL_EDGES] = base_show_all_edges
    preview_object[_BASE_SHOW_IN_FRONT] = base_show_in_front
