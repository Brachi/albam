import os

try:
    import bpy
except ImportError:
    from unittest.mock import Mock
    bpy = Mock()

from albam.registry import blender_registry


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
        for file_path in to_import:
            with open(file_path, 'rb') as f:
                data = f.read()
            id_magic = data[:4]

            func = blender_registry.import_registry.get(id_magic)
            if not func:
                raise TypeError('File not supported for import. Id magic: {}'.format(id_magic))

            name = os.path.basename(file_path)
            obj = bpy.data.objects.new(name, None)

            # TODO: proper logging/raising and rollback if failure
            func(obj, file_path)

            obj.albam_imported_item['data'] = data
            obj.albam_imported_item.name = name
            obj.albam_imported_item.source_path = file_path
            bpy.context.scene.objects.link(obj)
            new_albam_imported_item = context.scene.albam_items_imported.add()
            new_albam_imported_item.name = name

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
        id_magic = obj.albam_imported_item['data'][:4]
        func = blender_registry.export_registry.get(id_magic)
        if not func:
            raise TypeError('File not supported for export. Id magic: {}'.format(id_magic))
        func(obj, self.filepath)
        return {'FINISHED'}
