import ctypes
from collections import defaultdict


class BlenderRegistry:

    _VALID_BPY_PROP_IDENTIFIERS = {'material', 'texture', 'mesh'}

    def __init__(self):
        self.import_registry = {}
        self.export_registry = {}
        self.bpy_props = defaultdict(list)  # identifier: [(prop_name, prop_type, default)]

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
        """
        Class decorator to use in ctypes.Structure or albam.lib.DynamicStructure.
        iterates over the _fields_ attribute of the class looking for all
        fields that start with `prefix` and and depending on `identifier`, register
        it for drawing eiter in the Mesh, Material, or Texture panel.
        This is a temporary design, since adding more games will complicate things.
        It's not meant for users, but for test the behavior of a game when certain
        settings are changed before exporting
        """
        if identifier not in self._VALID_BPY_PROP_IDENTIFIERS:
            raise TypeError('Identifier {} is not valid: {}'
                            .format(identifier, self._VALID_BPY_PROP_IDENTIFIERS))

        def decorator(cls):
            defaults_dict = getattr(cls, '_defaults_', {})
            for field in cls._fields_:
                field_name = field[0]
                field_type = field[1]
                if not field_name.startswith(prefix):
                    continue
                name_to_register = field_name  # TODO: name clash between clasess, e.g unk_value_...
                bpy_prop_cls_name = self._decide_bpyprop_cls(field_type)
                default = defaults_dict.get(field_name)
                value = (name_to_register, bpy_prop_cls_name, default)
                self.bpy_props[identifier].append(value)
            return cls
        return decorator

    @staticmethod
    def _decide_bpyprop_cls(field_type):
        # TODO: add grouping in a different lib, like the 'DynamicStructure' one
        if field_type == ctypes.c_float:
            return 'FloatProperty'
        elif field_type in (ctypes.c_short, ctypes.c_ushort, ctypes.c_uint, ctypes.c_byte, ctypes.c_ubyte):
            return 'IntProperty'
        elif field_type == ctypes.c_uint16:
            return 'BoolProperty'
        else:
            raise TypeError('{} is not supported for registering with a bpy prop'.format(field_type))


blender_registry = BlenderRegistry()
