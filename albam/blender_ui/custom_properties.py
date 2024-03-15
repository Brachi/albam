import bpy

from albam.registry import blender_registry


def AlbamCustomPropertiesFactory(kind: str):
    """
    Generate subclasses of bpy.props.PropertyGroup
    based on kind, which can be "mesh", "image", or "material".

    These subclassess will use the blender registry to include
    custom properties for each app_id.

    E.g. to add custom properties for materials for app_id `app_test`
    use the register_custom

    ```
    @blender_registry.register_custom_properties_material("app_test_properties", ("app_test",))
    @blender_registry.register_blender_prop
    class AppTestMaterialCustomProperties(bpy.types.PropertyGroup):
        custom_property_1: bpy.props.IntVectorProperty(size=4, default=(0, 0, 128, 140))
        custom_property_2: bpy.props.StringProperty(default="spam")
        ...
    ```

    This later can be access from a material like this:

    ```
    >>> bpy.data.materials[0].albam_custom_properties.app_test_properties
    bpy.data.materials[0].albam_custom_properties.app_test_properties
    >>> type(bpy.data.materials[0].albam_custom_properties.app_test_properties)
    <class "AppTestMaterialCustomProperties">
    >>> bpy.data.materials[0].albam_custom_properties.app_test_properties.custom_property_2
    spam
    ```

    Knowing the name of the custom properties is not necessary, since they can also be
    obtained with the app_id:

    >>> bpy.data.materials[0].albam_custom_properties.get_appid_custom_properties("app_test")
    bpy.data.materials[0].albam_custom_properties.app_test_properties
    >>> type(bpy.data.materials[0].albam_custom_properties.get_appid_custom_properties("app_test"))
    <class "AppTestMaterialCustomProperties">

    """

    def create_data_custom_properties(registry_name):
        data = {}
        appid_map = {}
        registry = getattr(blender_registry, registry_name)
        for name, (cls, app_ids) in registry.items():
            data[name] = bpy.props.PointerProperty(type=cls)
            appid_map.update({app_id: name for app_id in app_ids})
        return data, appid_map

    def get_appid_custom_properties(self, app_id):
        """
        class method to return the custom_properties
        associated with the app_id
        """
        # TODO: error handling
        property_name = self.APPID_MAP[app_id]
        return getattr(self, property_name)

    def _get_parent_albam_asset_mesh(mesh):
        albam_asset = None
        for obj in bpy.data.objects:
            if not obj.albam_asset.relative_path:
                continue
            children = {c.data for c in obj.children_recursive if c.type == "MESH"}
            if mesh in children:
                albam_asset = obj.albam_asset
                break
        return albam_asset

    def _get_parent_albam_asset_material(mat):
        albam_asset = None
        for obj in bpy.data.objects:
            if not obj.albam_asset.relative_path:
                continue
            children = [c.data for c in obj.children_recursive if c.type == "MESH"]
            is_mat_used = any(mesh.user_of_id(mat) for mesh in children)
            if is_mat_used:
                albam_asset = obj.albam_asset
                break
        return albam_asset

    def get_parent_albam_asset(self):
        custom_prop_context = self.id_data
        albam_asset = None

        if isinstance(custom_prop_context, bpy.types.Mesh):
            albam_asset = _get_parent_albam_asset_mesh(custom_prop_context)
        elif isinstance(custom_prop_context, bpy.types.Material):
            albam_asset = _get_parent_albam_asset_material(custom_prop_context)

        return albam_asset

    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    assert kind in ("mesh", "material", "image")
    data, appid_map = create_data_custom_properties(f"custom_properties_{kind}")

    return type(
        f'AlbamCustomProperty{kind.title()}',
        (bpy.types.PropertyGroup, ),
        {
            '__annotations__' : data,
            'APPID_MAP': appid_map,
            get_appid_custom_properties.__name__: get_appid_custom_properties,
            get_parent_albam_asset.__name__: get_parent_albam_asset,
        }
    )


@blender_registry.register_blender_type
class ALBAM_PT_CustomPropertiesMaterial(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CustomPropertiesMaterial"
    bl_label = "Custom Properties (Albam)"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):  # pragma: no cover
        return context.material and context.material.albam_custom_properties.get_parent_albam_asset()

    def draw(self, context):
        albam_asset = context.material.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        custom_props = context.material.albam_custom_properties.get_appid_custom_properties(app_id)
        props_name = context.material.albam_custom_properties.APPID_MAP[app_id]
        self.layout.label(text=f"App: {app_id}")
        self.layout.label(text=f"Props: {props_name}")
        self.layout.separator()
        for k in custom_props.__annotations__:
            self.layout.prop(custom_props, k)


@blender_registry.register_blender_type
class ALBAM_PT_CustomPropertiesMesh(bpy.types.Panel):
    bl_idname = "ALBAM_PT_CustomPropertiesMesh"
    bl_label = "Custom Properties (Albam)"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):  # pragma: no cover
        return context.mesh and context.mesh.albam_custom_properties.get_parent_albam_asset()

    def draw(self, context):
        albam_asset = context.mesh.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        custom_props = context.mesh.albam_custom_properties.get_appid_custom_properties(app_id)
        props_name = context.mesh.albam_custom_properties.APPID_MAP[app_id]
        self.layout.label(text=f"App: {app_id}")
        self.layout.label(text=f"Props: {props_name}")
        self.layout.separator()
        for k in custom_props.__annotations__:
            self.layout.prop(custom_props, k)
