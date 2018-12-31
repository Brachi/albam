try:
    import bpy
except ImportError:
    pass

import albam.engines.mtframework.blender_import  # noqa
import albam.engines.mtframework.blender_import  # noqa
from albam.registry import blender_registry

import os

try:
    import bpy
except ImportError:
    from unittest.mock import Mock
    bpy = Mock()

from albam.registry import blender_registry


class AlbamImportedItemName(bpy.types.PropertyGroup):
    '''All imported object names are saved here to then show them in the
    export list'''
    name : bpy.props.StringProperty(name="Imported Item", default="Unknown")


class AlbamImportedItem(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(options={'HIDDEN'})
    source_path : bpy.props.StringProperty(options={'HIDDEN'})
    folder : bpy.props.StringProperty(options={'HIDDEN'})  # Always in posix format
    data : bpy.props.StringProperty(options={'HIDDEN'}, subtype='BYTE_STRING')
    file_type : bpy.props.StringProperty(options={'HIDDEN'})


class AlbamImportExportPanel(bpy.types.Panel):
    bl_label = "Albam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):  # pragma: no cover
        scn = context.scene
        layout = self.layout
        layout.operator('albam_import.item', text='Import (debug)')
        layout.prop_search(scn, 'albam_item_to_export', scn, 'albam_items_imported', text='select')
        layout.operator('albam_export.item', text='Export')


class AlbamImportOperator(bpy.types.Operator):
    bl_idname = "albam_import.item"
    bl_label = "import item"

    directory : bpy.props.StringProperty(subtype='DIR_PATH')
    files : bpy.props.CollectionProperty(name='adf', type=bpy.types.OperatorFileListElement)
    unpack_dir : bpy.props.StringProperty(options={'HIDDEN'})

    # temporary disabling
    # def invoke(self, context, event):  # pragma: no cover
    #     wm = context.window_manager
    #     wm.fileselect_add(self)
    #     return {'RUNNING_MODAL'}

    def execute(self, context):
        """
        Temporary always importing the same model for upgrade to 2.8
        """
        # to_import = [os.path.join(self.directory, f.name) for f in self.files]
        # for file_path in to_import:
        #     self._import_file(file_path=file_path, context=context)

        file_path = '/home/brachi/repos/albam/tests/samples/re5/arc/uPl00ChrisNormal.arc'
        self._import_file(file_path=file_path, context=context)
        return {'FINISHED'}

    def _import_file(self, **kwargs):
        parent = kwargs.get('parent')
        file_path = kwargs.get('file_path')
        context = kwargs['context']
        kwargs['unpack_dir'] = self.unpack_dir

        with open(file_path, 'rb') as f:
            data = f.read()
        id_magic = data[:4]

        func = blender_registry.import_registry.get(id_magic)
        if not func:
            raise TypeError('File not supported for import. Id magic: {}'.format(id_magic))

        name = os.path.basename(file_path)
        obj_data = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, obj_data)
        obj.parent = parent
        obj.albam_imported_item['data'] = data
        obj.albam_imported_item.source_path = file_path

        # TODO: proper logging/raising and rollback if failure
        results_dict = func(blender_object=obj, **kwargs)
        obj.display_type = 'WIRE'
        bpy.context.scene.collection.objects.link(obj)

        is_exportable = bool(blender_registry.export_registry.get(id_magic))
        if is_exportable:
            new_albam_imported_item = context.scene.albam_items_imported.add()
            new_albam_imported_item.name = name
        # TODO: re-think this. Is it necessary? Too implicit
        if results_dict:
            files = results_dict.get('files', [])
            kwargs = results_dict.get('kwargs', {})
            for f in files:
                self._import_file(file_path=f, context=context, **kwargs)


class AlbamExportOperator(bpy.types.Operator):
    bl_label = "export item"
    bl_idname = "albam_export.item"

    filepath : bpy.props.StringProperty()

    @classmethod
    def poll(self, context):  # pragma: no cover
        if not bpy.context.scene.albam_item_to_export:
            return False
        return True

    def invoke(self, context, event):  # pragma: no cover
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
        bpy.ops.object.mode_set(mode='OBJECT')
        func(obj, self.filepath)
        return {'FINISHED'}


bl_info = {
    "name": "Albam",
    "author": "Sebastian Brachi",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),
    "location": "Properties Panel",
    "description": "Import-Export multiple video-bame formats",
    "wiki_url": "https://github.com/Brachi/albam",
    "tracker_url": "https://github.com/Brachi/albam/issues",
    "category": "Import-Export"}


def register():
    bpy.utils.register_class(AlbamImportedItem)
    bpy.utils.register_class(AlbamImportedItemName)
    bpy.utils.register_class(AlbamImportExportPanel)
    bpy.utils.register_class(AlbamExportOperator)
    bpy.utils.register_class(AlbamImportOperator)

    bpy.types.Scene.albam_item_to_export = bpy.props.StringProperty()
    bpy.types.Scene.albam_items_imported = bpy.props.CollectionProperty(type=AlbamImportedItemName)
    bpy.types.Object.albam_imported_item = bpy.props.PointerProperty(type=AlbamImportedItem)


def unregister():
    bpy.utils.unregister_module(__name__)
