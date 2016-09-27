from collections import defaultdict


class BlenderRegistry:

    def __init__(self):
        self.import_registry = {}
        self.export_registry = {}
        self.bpy_props = defaultdict(list)  # identifier: [(prop_name, prop_type)]

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

    def register_bpy_prop(self, identifier, prefix):
        def decorator(cls):
            for field in cls._fields_:
                field_name = field[0]
                if not field_name.startswith(prefix):
                    continue
                name_to_register = '{}_{}'.format(cls.__name__, field_name)
                value = (name_to_register, 'FloatProperty')
                self.bpy_props[identifier].append(value)
            return cls
        return decorator


blender_registry = BlenderRegistry()
