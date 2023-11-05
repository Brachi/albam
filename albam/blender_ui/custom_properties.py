import bpy

from albam.registry import blender_registry


@blender_registry.register_blender_type
class ALBAM_PT_CustomPropertiesMaterial(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CustomPropertiesMaterial"
    bl_label = "Custom Properties (Albam)"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):  # pragma: no cover
        return context.material and bool(cls.albam_asset_uses_mat(context.material))

    def draw(self, context):
        mat = context.material
        albam_asset = self.albam_asset_uses_mat(mat)  # already called in poll, can we save this?
        app_id = albam_asset.app_id
        custom_props = mat.albam_custom_properties.get_appid_custom_properties(app_id)
        for k in custom_props.__annotations__:
            self.layout.prop(custom_props, k)

    @staticmethod
    def albam_asset_uses_mat(mat):
        # XXX case where same material used in different
        # albam assets with different app_ids not supported yet
        albam_asset = None
        for obj in bpy.data.objects:
            if not obj.albam_asset.relative_path:
                continue
            children = [c.data for c in obj.children_recursive if c.type == "MESH"]
            is_mat_used = any(mesh.user_of_id(mat) for mesh in children)
            if is_mat_used:
                albam_asset = obj.albam_asset
        return albam_asset


@blender_registry.register_blender_type
class ALBAM_PT_CustomPropertiesMesh(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CustomPropertiesMesh"
    bl_label = "Custom Properties (Albam)"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):  # pragma: no cover
        return context.mesh and bool(cls.albam_asset_uses_mesh(context.mesh))

    def draw(self, context):
        albam_asset = self.albam_asset_uses_mesh(context.mesh)  # already called in poll, can we save this?
        app_id = albam_asset.app_id
        custom_props = context.mesh.albam_custom_properties.get_appid_custom_properties(app_id)
        for k in custom_props.__annotations__:
            self.layout.prop(custom_props, k)

    @staticmethod
    def albam_asset_uses_mesh(mesh):
        # XXX case where same material used in different
        # albam assets with different app_ids not supported yet
        albam_asset = None
        for obj in bpy.data.objects:
            if not obj.albam_asset.relative_path:
                continue
            children = {c.data for c in obj.children_recursive if c.type == "MESH"}
            if mesh in children:
                albam_asset = obj.albam_asset
                break
        return albam_asset
