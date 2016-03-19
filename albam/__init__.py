import os

from albam.mtframework.blender_import import import_arc
from albam.mtframework.blender_export import export_arc

try:
    import bpy
except ImportError:
    from unittest.mock import Mock
    bpy = Mock()


bl_info = {
    "name": "Albam",
    "author": "Sebastian Brachi",
    "version": (0, 0, 1),
    "blender": (2, 76, 0),
    "location": "Properties Panel",
    "description": "Import-Export multiple video-bame formats",
    "wiki_url": "https://github.com/Brachi/albam",
    "tracker_url": "https://github.com/Brachi/albam/issues",
    "category": "Import-Export"}


class AlbamImportedItemName(bpy.types.PropertyGroup):
    '''All imported object names are saved here to then show them in the
    export list'''
    name = bpy.props.StringProperty(name="Imported Item", default="Unknown")


class AlbamImportedItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(options={'HIDDEN'})
    source_path = bpy.props.StringProperty(options={'HIDDEN'})
    source_path_is_absolute = bpy.props.BoolProperty(options={'HIDDEN'})
    data = bpy.props.StringProperty(options={'HIDDEN'}, subtype='BYTE_STRING')
    file_type = bpy.props.StringProperty(options={'HIDDEN'})


class AlbamImportExportPanel(bpy.types.Panel):
    bl_label = "Albam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        layout.operator('import.item', text='Import')
        layout.prop_search(scn, 'albam_item_to_export', scn, 'albam_items_imported', 'select')
        layout.operator('export.item', text='Export')


class AlbamImportOperator(bpy.types.Operator):
    bl_idname = "import.item"
    bl_label = "import item"
    directory = bpy.props.StringProperty(subtype='DIR_PATH')
    files = bpy.props.CollectionProperty(name='adf', type=bpy.types.OperatorFileListElement)
    filter_glob = bpy.props.StringProperty(default="*.arc", options={'HIDDEN'})

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        to_import = [os.path.join(self.directory, f.name) for f in self.files]
        for item in to_import:
            try:
                import_arc(item, None, context.scene)
            except Exception as err:
                # TODO: proper logging
                print('Error importing {}: {}'.format(item, err))
        return {'FINISHED'}


class AlbamExportOperator(bpy.types.Operator):
    bl_idname = "export.item"
    bl_label = "export item"
    filepath = bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        if not bpy.context.scene.albam_item_to_export:
            return False
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        object_name = context.scene.albam_item_to_export
        obj = bpy.data.objects[object_name]
        arc = export_arc(obj)
        with open(self.filepath, 'wb') as w:
            w.write(arc)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AlbamImportExportPanel)
    bpy.utils.register_class(AlbamImportOperator)
    bpy.utils.register_class(AlbamExportOperator)
    bpy.utils.register_class(AlbamImportedItemName)
    bpy.utils.register_class(AlbamImportedItem)

    bpy.types.Scene.albam_item_to_export = bpy.props.StringProperty()
    bpy.types.Scene.albam_items_imported = bpy.props.CollectionProperty(type=AlbamImportedItemName)

    bpy.types.Object.albam_imported_item = bpy.props.PointerProperty(type=AlbamImportedItem)

    # Not using PointerProperty/PropertyGroup since they are not editable from the UI
    # TODO: look if that can be added into blender
    bpy.types.Texture.albam_imported_texture_type = bpy.props.StringProperty()
    bpy.types.Texture.albam_imported_texture_value_1 = bpy.props.FloatProperty()
    bpy.types.Texture.albam_imported_texture_value_2 = bpy.props.FloatProperty()
    bpy.types.Texture.albam_imported_texture_value_3 = bpy.props.FloatProperty()
    bpy.types.Texture.albam_imported_texture_value_4 = bpy.props.FloatProperty()


def unregister():
    bpy.utils.unregister_class(AlbamImportExportPanel)
    bpy.utils.unregister_class(AlbamImportOperator)
    bpy.utils.unregister_class(AlbamExportOperator)


if __name__ == "__main__":
    register()
