import os

import bpy

from albam.registry import blender_registry


class ALBAM_PT_ImportExportPanel2(bpy.types.Panel):
    """UI Albam subpanel in 3D view"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_UI_Panel2"
    bl_label = "Albam (Beta)"

    def draw(self, context):  # pragma: no cover
        self.layout.operator("albam_import.item", text="Import")


class AlbamImportOperator2(bpy.types.Operator):
    """Import button operator"""

    DIRECTORY = bpy.props.StringProperty(subtype="DIR_PATH")
    FILES = bpy.props.CollectionProperty(name="adf", type=bpy.types.OperatorFileListElement)
    FILTER_GLOB = bpy.props.StringProperty(default="*.arc", options={"HIDDEN"})

    bl_idname = "albam_import.item"
    bl_label = "import item"
    directory: DIRECTORY
    files: FILES
    filter_glob: FILTER_GLOB

    def invoke(self, context, event):  # pragma: no cover
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):  # pragma: no cover
        to_import = [
            os.path.join(self.directory, f.name) for f in self.files
        ]  # combine path to file and file name list to a new list
        for file_path in to_import:
            self._import_file(file_path=file_path)

        return {"FINISHED"}

    @staticmethod
    def _import_file(file_path):  # pragma: no cover
        with open(file_path, "rb") as f:
            data = f.read()
        id_magic = data[:4]

        func = blender_registry.import_registry.get(id_magic)  # find header in dictionary
        if not func:
            raise TypeError(f"File not supported for import. Id magic: {id_magic}")

        # TODO: proper logging/raising and rollback if failure
        bl_container = func(file_path)

        bpy.context.collection.objects.link(bl_container)
        for child in bl_container.children_recursive:
            try:
                # already linked
                bpy.context.collection.objects.link(child)
            except RuntimeError:
                pass


classes_to_register = (
    ALBAM_PT_ImportExportPanel2,
    AlbamImportOperator2,
)
