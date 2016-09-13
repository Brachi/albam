

class BlenderRegistry:

    def __init__(self):
        self.import_registry = {}
        self.export_registry = {}

    def register_function(self, func_type, identifier):
        def decorator(f):
            if func_type == 'import':
                self.import_registry[identifier] = f
            elif func_type == 'export':
                self.export_registry[identifier] = f
            else:
                raise TypeError('func_type {} not valid.'.format(func_type))
            return f
        return decorator

    def register_export_function(self, id_magic):
        def decorator(f):
            self.export_registry[id_magic] = f
            return f
        return decorator


blender_registry = BlenderRegistry()
