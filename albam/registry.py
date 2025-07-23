
class BlenderRegistry:
    def __init__(self):
        self.import_registry = {}
        self.export_registry = {}
        self.archive_loader_registry = {}
        self.archive_accessor_registry = {}
        self.props = []  # order is meaningful for dependencies
        self.types = []  # order is meaningufl for dependencies
        self.import_options_custom_draw_funcs = {}
        self.import_options_custom_poll_funcs = {}
        self.import_operator_poll_funcs = {}
        self.custom_properties_material = {}
        self.custom_properties_mesh = {}
        self.custom_properties_image = {}
        self.custom_properties_animation = {}
        self.file_categories = {}

    def register_blender_prop_albam(self, name):
        """
        Classes decorated will be automatically registered
        for Blender and stored in bpy.context.scene.albam.<name>
        """
        def decorator(cls):
            self.props.append((name, cls))
            return cls
        return decorator

    def register_blender_prop(self, cls):
        self.props.append(("", cls))
        return cls

    def register_blender_type(self, cls):
        self.types.append(cls)
        return cls

    def register_import_options_custom_draw_func(self, extension):
        def decorator(f):
            self.import_options_custom_draw_funcs[extension] = f
            return f
        return decorator

    def register_import_options_custom_poll_func(self, extension):
        def decorator(f):
            self.import_options_custom_poll_funcs[extension] = f
            return f
        return decorator

    def register_import_operator_poll_func(self, extension):
        def decorator(f):
            self.import_operator_poll_funcs[extension] = f
            return f
        return decorator

    def register_import_function(self, app_id, extension, file_category=None):
        def decorator(f):
            self.import_registry[(app_id, extension)] = f
            self.file_categories[(app_id, extension)] = file_category
            return f
        return decorator

    def register_export_function(self, app_id, extension):
        def decorator(f):
            self.export_registry[(app_id, extension)] = f
            return f
        return decorator

    def register_archive_loader(self, app_id, extension):
        def decorator(f):
            self.archive_loader_registry[(app_id, extension)] = f
            return f
        return decorator

    def register_archive_accessor(self, app_id, extension):
        def decorator(f):
            self.archive_accessor_registry[(app_id, extension)] = f
            return f

        return decorator

    def register_custom_properties_material(self, name, app_ids, is_secondary=False, display_name=""):
        def decorator(cls):
            for app_id in app_ids:
                self.custom_properties_material.setdefault(
                    app_id, {})[name] = (cls, is_secondary, display_name)
            return cls
        return decorator

    def register_custom_properties_mesh(self, name, app_ids, is_secondary=False, display_name=""):
        def decorator(cls):
            for app_id in app_ids:
                self.custom_properties_mesh.setdefault(app_id, {})[name] = (cls, is_secondary, display_name)
            return cls
        return decorator

    def register_custom_properties_animation(self, name, app_ids, is_secondary=False, display_name=""):
        def decorator(cls):
            for app_id in app_ids:
                self.custom_properties_animation.setdefault(app_id, {})[name] = (cls, is_secondary, display_name)
            return cls
        return decorator

    def register_custom_properties_image(self, name, app_ids, is_secondary=False, display_name=""):
        def decorator(cls):
            for app_id in app_ids:
                self.custom_properties_image.setdefault(app_id, {})[name] = (cls, is_secondary, display_name)
            return cls
        return decorator

    @property
    def importable_extensions(self):
        return list(self.import_registry.keys())

    @property
    def exportable_extensions(self):
        return list(self.export_registry.keys())


blender_registry = BlenderRegistry()
