import bpy


class ALBAM_UL_ExportableObjects(bpy.types.UIList):
    def filter_items(self, context, data, property_):
        flt_flags = [
            self.bitflag_filter_item if obj.get("albam.exportable") else 0 for obj in data.objects
        ]
        flt_neworder = []

        return flt_flags, flt_neworder


class ALBAM_PT_Export(bpy.types.Panel):
    bl_category = "Albam [Beta]"
    bl_idname = "ALBAM_PT_Export"
    bl_label = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        row = self.layout.row()
        row.template_list(
            "ALBAM_UL_ExportableObjects",
            "",
            context.scene,
            "objects",
            context.scene.albam.file_explorer,
            "file_list_selected_index",
            sort_lock=True,
        )
        row = self.layout.row()
        self.layout.operator("albam_import.item", text="Export")
