

class BlenderRegistry:
    def __init__(self):
        self.import_registry = {}
        self.archive_loader_registry = {}
        self.archive_accessor_registry = {}
        self.props = []  # order is meaningful for dependencies
        self.types = []  # order is meaningufl for dependencies
        self.import_options_custom_draw_funcs = {}
        self.import_options_custom_poll_funcs = {}
        self.import_operator_poll_funcs = {}

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

    def register_import_function(self, extension):
        def decorator(f):
            self.import_registry[extension] = f
            return f
        return decorator

    def register_archive_loader(self, extension):
        def decorator(f):
            self.archive_loader_registry[extension] = f
            return f
        return decorator

    def register_archive_accessor(self, extension):
        def decorator(f):
            self.archive_accessor_registry[extension] = f
            return f

        return decorator

    @property
    def importable_extensions(self):
        return list(self.import_registry.keys())


blender_registry = BlenderRegistry()
