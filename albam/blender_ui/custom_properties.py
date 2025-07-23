import json

import bpy

from albam.apps import APPS
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

    ```
    # Assuming the material is associated with a mesh that is part of an Albam asset
    >>> bpy.data.materials[0].albam_custom_properties.get_custom_properties_for_appid("app_test")
    bpy.data.materials[0].albam_custom_properties.app_test_properties
    >>> type(bpy.data.materials[0].albam_custom_properties.get_custom_properties_for_appid("app_test"))
    <class "AppTestMaterialCustomProperties">
    ```

    Even easier, with the shortcut that will get the app_id for us:

    ```
    # Assuming the material is associated with a mesh that is part of an Albam asset
    >>> bpy.data.materials[0].albam_custom_properties.get_custom_properties()
    bpy.data.materials[0].albam_custom_properties.app_test_properties
    >>> type(bpy.data.materials[0].albam_custom_properties.get_custom_properties())
    <class "AppTestMaterialCustomProperties">
    ```
    """

    def create_data_custom_properties(registry_name):
        data = {}
        appid_map = {}
        appid_map_secondary = {}
        subpanel_type = SUBPANEL_BASE.get(registry_name, None)
        registry = getattr(blender_registry, registry_name)
        for app_id, props_dict in registry.items():
            for name, (cls, is_secondary, display_name) in props_dict.items():
                data[f"{app_id}__{name}"] = bpy.props.PointerProperty(type=cls)
                if not is_secondary:
                    appid_map[app_id] = name
                else:
                    _create_custom_properties_secondary_subpanel(app_id, display_name, name, subpanel_type)
                    prop_names = appid_map_secondary.setdefault(app_id, [])
                    prop_names.append(name)

        return data, appid_map, appid_map_secondary

    def _create_custom_properties_secondary_subpanel(app_id, label, custom_props_id, subpanel_type):

        bl_idname = (f"ALBAM_PT_CustomProperties{kind.title()}Secondary"
                     f"{custom_props_id.title()}{app_id.title()}")

        SubPanel = type(
            bl_idname,
            (subpanel_type, ),
            {
                "bl_label": label,
                "bl_idname": bl_idname,
                "APP_ID": app_id,
                "custom_props_to_draw": custom_props_id,
                "bl_options": {"DEFAULT_CLOSED"},
            }
        )
        # Since these factories are created at the end, we need to register manually
        # the window where they are registered in albam/__init__.py was lost
        bpy.utils.register_class(SubPanel)
        # Adding to the registry now anyways so auto-unregistering works
        blender_registry.types.append(SubPanel)

    def get_custom_properties(self):
        """
        Shortcut to get the custom properties based on the app_id
        of the parent albam asset
        """
        albam_asset = self.get_parent_albam_asset()
        app_id = albam_asset.app_id
        return self.get_custom_properties_for_appid(app_id)

    def get_custom_properties_for_appid(self, app_id):
        """
        class method to return the custom_properties
        associated with the app_id
        """
        # TODO: error handling
        property_name = self.APPID_MAP[app_id]
        return getattr(self, f"{app_id}__{property_name}")

    def get_custom_properties_secondary_for_appid(self, app_id):
        # TODO: error handling
        try:
            property_names = self.APPID_MAP_SECONDARY[app_id]
        except KeyError:
            return {}

        return {pn: getattr(self, f"{app_id}__{pn}") for pn in property_names}

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

    def _get_parent_albam_asset_object(bl_obj):
        albam_asset = None
        for obj in bpy.data.objects:
            if not obj.albam_asset.relative_path:
                continue
            children = {c for c in obj.children_recursive if c.type == "EMPTY" or c.type == "MESH"}
            if bl_obj in children:
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
        elif isinstance(custom_prop_context, bpy.types.Object):
            albam_asset = _get_parent_albam_asset_object(custom_prop_context)

        return albam_asset

    def get_custom_properties_as_dict(self):
        context_item = self.id_data
        albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        props_name = context_item.albam_custom_properties.APPID_MAP[app_id]
        props = context_item.albam_custom_properties.get_custom_properties_for_appid(app_id)

        props_secondary = (
            context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
        )

        final = {
            app_id: {
                props_name: {},

            }
        }
        current = final[app_id][props_name]

        for prop_item_name in props.__annotations__:
            value = getattr(props, prop_item_name)
            try:
                value = value[:]
            except TypeError:
                pass
            current[prop_item_name] = value

        for prop_sec_name, props_sec in props_secondary.items():
            for prop_sec_item_name in props_sec.__annotations__:
                value = getattr(props_sec, prop_sec_item_name)
                try:
                    value = value[:]
                except TypeError:
                    pass
                final[app_id].setdefault(
                    prop_sec_name, {})[prop_sec_item_name] = value

        return final

    # missing bl_label and bl_idname in cls dict?
    # https://projects.blender.org/blender/blender/issues/86719#issuecomment-232525
    assert kind in ("mesh", "material", "image", "collision")
    data, appid_map, appid_map_secondary = create_data_custom_properties(f"custom_properties_{kind}")

    return type(
        f'AlbamCustomProperty{kind.title()}',
        (bpy.types.PropertyGroup, ),
        {
            '__annotations__': data,
            'APPID_MAP': appid_map,
            'APPID_MAP_SECONDARY': appid_map_secondary,
            get_custom_properties.__name__: get_custom_properties,
            get_custom_properties_as_dict.__name__: get_custom_properties_as_dict,
            get_custom_properties_for_appid.__name__: get_custom_properties_for_appid,
            get_custom_properties_secondary_for_appid.__name__: get_custom_properties_secondary_for_appid,
            get_parent_albam_asset.__name__: get_parent_albam_asset,
        }
    )


class ALBAM_PT_CustomPropertiesBase(bpy.types.Panel):
    bl_label = "Custom Properties (Albam)"
    CONTEXT_ITEM_NAME = ""

    @classmethod
    def poll(cls, context):  # pragma: no cover
        """
        Only show custom properties panel if the contex_item (mesh or material)
        are associated with an albam asset (e.g. a 3d model)
        """
        context_item = getattr(context, cls.CONTEXT_ITEM_NAME)
        return context_item and context_item.albam_custom_properties.get_parent_albam_asset()

    def draw(self, context):
        """
        Draw the custom properties for the context_item (mesh or material)
        """
        context_item = getattr(context, self.CONTEXT_ITEM_NAME)
        albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        app_name = [app[1] for app in APPS if app[0] == app_id][0]
        custom_props = context_item.albam_custom_properties.get_custom_properties_for_appid(app_id)
        props_name = context_item.albam_custom_properties.APPID_MAP[app_id]

        layout = self.layout
        layout.use_property_split = True

        row = layout.row(align=True)
        row.label(text=f"{props_name} ({app_name})", icon="PROPERTIES")
        row.operator("albam.custom_props_copy", icon="COPYDOWN", text="")
        row.operator("albam.custom_props_paste", icon="PASTEDOWN", text="")
        row.operator("albam.custom_props_export", icon="EXPORT", text="")
        row.operator("albam.custom_props_import", icon="IMPORT", text="")

        self.layout.separator(factor=3.0)
        # for cases when the main custom properties class is empty
        if getattr(custom_props, "__annotations__", None):
            for k in custom_props.__annotations__:
                self.layout.prop(custom_props, k)


@blender_registry.register_blender_type
class ALBAM_PT_CustomPropertiesMaterial(ALBAM_PT_CustomPropertiesBase):
    bl_idname = "ALBAM_PT_CustomPropertiesMaterial"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    CONTEXT_ITEM_NAME = "material"


class ALBAM_PT_CustomPropertiesMaterialSubPanelBase(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_parent_id = "ALBAM_PT_CustomPropertiesMaterial"

    APP_ID = None
    custom_props_to_draw = None
    CONTEXT_ITEM_NAME = "material"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        context_item = getattr(context, self.CONTEXT_ITEM_NAME)
        albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        custom_props_sec = (
            context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id))
        if not custom_props_sec:
            return
        custom_props = custom_props_sec.get(self.custom_props_to_draw)
        if not custom_props:
            return
        for k in custom_props.__annotations__:
            # TODO: don't draw if marked as "HIDDEN"
            layout.prop(custom_props, k)

    @classmethod
    def poll(cls, context):
        context_item = getattr(context, cls.CONTEXT_ITEM_NAME)
        albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        if cls.APP_ID != app_id:
            return False
        custom_props_sec = (
            context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id))
        if not custom_props_sec:
            return False
        custom_props = custom_props_sec.get(cls.custom_props_to_draw)
        if not custom_props:
            return False
        return True


class ALBAM_PT_CustomPropertiesCollisionSubPanelBase(ALBAM_PT_CustomPropertiesMaterialSubPanelBase):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_parent_id = "ALBAM_PT_CustomPropertiesCollision"

    APP_ID = None
    custom_props_to_draw = None
    CONTEXT_ITEM_NAME = "object"

    def draw(self, context):
        super().draw(context)

        layout = self.layout
        context_item = getattr(context, self.CONTEXT_ITEM_NAME)
        albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id

        custom_props_sec = (
            context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
        )
        custom_props = custom_props_sec.get(self.custom_props_to_draw)
        for k in custom_props.__annotations__:
            collection = getattr(custom_props, k)
            if not collection:
                return
            # display collection item
            if isinstance(collection, bpy.types.bpy_prop_collection):
                active_index = getattr(custom_props, "item_index", 0)
                if 0 <= active_index < len(collection):
                    active_item = collection[active_index]
                    name = k.capitalize()
                    layout.label(text=f"{name}: {active_index}")
                    # display child collection item
                    for child_k in active_item.__annotations__:
                        child_value = getattr(active_item, child_k)
                        if isinstance(child_value, bpy.types.bpy_prop_collection):
                            child_active_index = getattr(active_item, "item_index", 0)
                            if 0 <= child_active_index < len(child_value):
                                child_active_item = child_value[child_active_index]
                                child_name = child_k.capitalize()
                                layout.label(text=f"{child_name}: {child_active_index}")
                                for prop in child_active_item.__annotations__:
                                    layout.prop(child_active_item, prop)
                            else:
                                layout.label(text=f"{child_k}: (empty)")
                        else:
                            layout.prop(active_item, child_k)


@blender_registry.register_blender_type
class ALBAM_PT_CustomPropertiesMesh(ALBAM_PT_CustomPropertiesBase):
    bl_idname = "ALBAM_PT_CustomPropertiesMesh"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    CONTEXT_ITEM_NAME = "mesh"


@blender_registry.register_blender_prop_albam(name="clipboard")
class ClipboardData(bpy.types.PropertyGroup):
    buff: bpy.props.StringProperty(default="{}")

    def get_buffer(self):
        return json.loads(self.buff)

    def update_buffer(self, data: dict):
        current = self.get_buffer()
        current.update(data)
        self.buff = json.dumps(current)


@blender_registry.register_blender_type
class ALBAM_PT_CustomPropertiesCollision(ALBAM_PT_CustomPropertiesBase):
    bl_idname = "ALBAM_PT_CustomPropertiesCollision"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    CONTEXT_ITEM_NAME = "object"


SUBPANEL_BASE = {
    "custom_properties_material": ALBAM_PT_CustomPropertiesMaterialSubPanelBase,
    "custom_properties_collision": ALBAM_PT_CustomPropertiesCollisionSubPanelBase,
}


@blender_registry.register_blender_type
class ALBAM_OT_CustomPropertiesCopy(bpy.types.Operator):
    """
    Store properties in context.scene.albam.clipboard
    """
    bl_idname = "albam.custom_props_copy"
    bl_label = "Copy Albam Custom Properties"

    def execute(self, context):
        context_item = context.mesh or context.material
        props_dict = context_item.albam_custom_properties.get_custom_properties_as_dict()
        context.scene.albam.clipboard.update_buffer(props_dict)
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_CustomPropertiesPaste(bpy.types.Operator):
    """
    Paste properties stored in context.scene.albam.clipboard
    """
    bl_idname = "albam.custom_props_paste"
    bl_label = "Paste Albam Custom Properties"

    def execute(self, context):
        context_item = context.mesh or context.material
        albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        custom_props = context_item.albam_custom_properties.get_custom_properties_for_appid(app_id)
        custom_props_sec = (
            context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
        )
        props_name = context_item.albam_custom_properties.APPID_MAP[app_id]
        buff = context.scene.albam.clipboard.get_buffer()

        to_paste = buff.get(app_id, {}).get(props_name, {})
        for k, v in to_paste.items():
            setattr(custom_props, k, v)

        for sec_prop_name, sec_prop in custom_props_sec.items():
            to_paste = buff.get(app_id, {}).get(sec_prop_name, {})
            for k, v in to_paste.items():
                setattr(sec_prop, k, v)

        # TODO: report items pasted
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_CustomPropertiesExport(bpy.types.Operator):
    """
    Export properties stored context.scene.albam.clipboard
    to a json file
    """
    bl_idname = "albam.custom_props_export"
    bl_label = "Export props"

    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    CHECK_EXISTING = bpy.props.BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )
    check_existing: CHECK_EXISTING
    filepath: FILEPATH
    filename = bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        self.filepath = context.active_object.active_material.name + ".json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        context_item = context.mesh or context.material
        to_export = context_item.albam_custom_properties.get_custom_properties_as_dict()
        with open(self.filepath, "w") as w:
            json.dump(to_export, w, indent=4)
        return {'FINISHED'}


@blender_registry.register_blender_type
class ALBAM_OT_CustomPropertiesImport(bpy.types.Operator):
    """
    Import custom properties from a json file
    """
    bl_idname = "albam.custom_props_import"
    bl_label = "Import props"

    EXTENSION_FILTER = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
    )
    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    filepath: FILEPATH
    filename = bpy.props.StringProperty(default="")
    filter_glob: EXTENSION_FILTER

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        data = {}
        with open(self.filepath) as f:
            try:
                data = json.load(f)
            except UnicodeDecodeError:
                self.report({"ERROR"}, "Failed opening the file in text mode. Is it a valid json?")
                return {'FINISHED'}
            except json.JSONDecodeError:
                self.report({"ERROR"}, "Failed decoding json. Is it valid?"
                            " Tip: validate it in https://jsonformatter.org")
                return {'FINISHED'}
            except Exception as err:
                self.report({"ERROR"}, "An unexpted error happened, please check the console")
                print(err)
                return {'FINISHED'}

        context_item = context.mesh or context.material
        albam_asset = context_item.albam_custom_properties.get_parent_albam_asset()
        app_id = albam_asset.app_id
        current_props = context_item.albam_custom_properties.get_custom_properties()
        current_props_sec = (
            context_item.albam_custom_properties.get_custom_properties_secondary_for_appid(app_id)
        )
        props_name_main = context_item.albam_custom_properties.APPID_MAP[app_id]
        props_main = {}
        props_sec = {}
        missing = []

        try:
            props_main = data[app_id][props_name_main]
        except KeyError:
            missing.append(props_name_main)

        for prop_name in current_props_sec:
            try:
                props_sec[prop_name] = data[app_id][prop_name]
            except KeyError:
                missing.append(prop_name)

        imported = 0
        for k, v in props_main.items():
            # TODO: validate keys exist and emit a warning (e.g. for name changing)
            setattr(current_props, k, v)
            imported += 1

        for prop_sec_name, data in props_sec.items():
            for k, v in data.items():
                # TODO: validate keys exist and emit a warning (e.g. for name changing)
                target = current_props_sec[prop_sec_name]
                setattr(target, k, v)
                imported += 1

        if missing and not imported:
            self.report(
                {"WARNING"}, f"Expected to find the keys {missing} under '{app_id}'. Nothing imported")

        elif missing and imported:
            self.report(
                {"WARNING"},
                f"Expected to find the keys {missing} under '{app_id}'. Imported {imported} properties")
        else:
            self.report({"INFO"}, f"Imported {imported} properties")

        context.area.tag_redraw()
        return {'FINISHED'}
