from albam.mtframework.blender_import import import_arc

import bpy
from bpy.props import StringProperty as StrProp

bl_info = {
    "name": "Albam",
    "author": "Sebastian Brachi",
    "version": (0, 0, 1),
    "blender": (2, 76, 0),
    "location": "File > bla",
    "description": "Import-Export multiple video-bame formats",
    "wiki_url": "https://github.com/Brachi/albam",
    "tracker_url": "https://github.com/Brachi/albam/issues",
    "category": "Import-Export"}


scn = bpy.types.Scene
scn.albam_import_filepath = StrProp(name="Arc file*", description="Arc file to import", subtype="FILE_PATH")


class AlbamUIPanel(bpy.types.Panel):
    bl_label = "Albam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        layout.prop(scn, 'albam_import_filepath')
        layout.operator("import.model", text='Import Model')


class AlbamImportOperator(bpy.types.Operator):
    bl_idname = "import.model"
    bl_label = "imort model"

    @classmethod
    def poll(self, context):
        if not bpy.context.scene.albam_import_file_path:
            return False
        return True

    # To do: find how to always get absolute path to pass to the function
    def execute(self, context):
        import_arc(bpy.context.scene.albam_import_filepath)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AlbamUIPanel)
    bpy.utils.register_class(AlbamImportOperator)


def unregister():
    bpy.utils.unregister_class(AlbamUIPanel)
    bpy.utils.unregister_class(AlbamImportOperator)

if __name__ == "__main__":
    register()
