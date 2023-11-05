import json
import os


_shaders_file = "shader-objects.json"
_shader_objects = None


def get_shader_objects():
    global _shader_objects
    if not _shader_objects:
        this_dir = os.path.dirname(__file__)
        path = os.path.join(this_dir, _shaders_file)
        with open(path) as f:
            _shader_objects = json.load(f)
    return _shader_objects
