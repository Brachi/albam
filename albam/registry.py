import ctypes
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
                field_type = field[1]
                if not field_name.startswith(prefix):
                    continue
                name_to_register = field_name  # TODO: name clash between clasess, e.g unk_value_...
                bpy_prop_cls_name = self._decide_bpyprop_cls(field_type)
                value = (name_to_register, bpy_prop_cls_name)
                self.bpy_props[identifier].append(value)
            return cls
        return decorator

    @staticmethod
    def _decide_bpyprop_cls(field_type):
        # TODO: add grouping in a different lib, like the 'DynamicStructure' one
        if field_type == ctypes.c_float:
            return 'FloatProperty'
        elif field_type in (ctypes.c_short, ctypes.c_ushort, ctypes.c_uint, ctypes.c_uint16):
            return 'IntProperty'
        else:
            raise TypeError('{} is not supported for registering with a bpy prop'.format(field_type))


blender_registry = BlenderRegistry()
