

class BlenderRegistry:
    def __init__(self):
        self.import_registry = {}
        self.archive_loader_registry = {}
        self.archive_accessor_registry = {}

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
