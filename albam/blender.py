import os

try:
    import bpy
except ImportError:
    pass

from albam.mtframework.blender_import import import_arc
from albam.mtframework.blender_export import export_arc


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
                raise
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
