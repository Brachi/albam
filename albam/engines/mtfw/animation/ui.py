"""What the import panel shows for a .lmt.

A .lmt carries no skeleton of its own - it is keyed on bone ids that mean
nothing without one - so the panel has to ask which armature to apply it to
before the operator can run at all.
"""
import bpy

from ....registry import blender_registry


def filter_armatures(self, obj):
    # TODO: filter by custom properties that indicate is
    # a RE5 compatible armature
    return obj.type == 'ARMATURE'


@blender_registry.register_blender_prop_albam(name='import_options_lmt')
class ImportOptionsLMT(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(type=bpy.types.Object, poll=filter_armatures)


@blender_registry.register_import_options_custom_draw_func(extension='lmt')
def draw_lmt_options(panel_instance, context):
    panel_instance.bl_label = "LMT Options"
    panel_instance.layout.prop(context.scene.albam.import_options_lmt, 'armature')


@blender_registry.register_import_options_custom_poll_func(extension='lmt')
def poll_lmt_options(panel_instance, context):
    return True


@blender_registry.register_import_operator_poll_func(extension='lmt')
def poll_import_operator_for_lmt(panel_class, context):
    return bool(context.scene.albam.import_options_lmt.armature)
