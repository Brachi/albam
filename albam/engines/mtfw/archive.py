import io
import os
import zlib

import bpy
from kaitaistruct import KaitaiStream

from albam.registry import blender_registry
from . import EXTENSION_TO_FILE_ID
from .mesh import build_blender_model
from .structs.arc import Arc


@blender_registry.register_function("import", identifier=b"ARC\x00")
def import_arc(file_path):
    bl_arc_container = bpy.data.objects.new(os.path.basename(file_path), None)
    arc = ArcWrapper(file_path)
    mod_type = EXTENSION_TO_FILE_ID["mod"]
    mod_file_entries = arc.get_file_entries_by_type(mod_type)

    for mod_file_entry in mod_file_entries:
        try:
            bl_mod_container = build_blender_model(arc, mod_file_entry)
            bl_mod_container.parent = bl_arc_container
        except Exception as err:
            print("failed to build model", mod_file_entry.file_path, err)

    return bl_arc_container


class ArcWrapper:
    def __init__(self, file_path):
        with open(file_path, "rb") as f:
            self.parsed = Arc(KaitaiStream(io.BytesIO(f.read())))

    def get_file_entries_by_type(self, file_type):
        filtered = []
        for fe in self.parsed.file_entries:
            if fe.file_type == file_type:
                filtered.append(fe)
        return filtered

    def get_file(self, file_path, file_type):
        file_ = None

        for fe in self.parsed.file_entries:
            if fe.file_path == file_path and fe.file_type == file_type:
                try:
                    file_ = zlib.decompress(fe.raw_data)
                    break
                except EOFError:
                    print(f"Requested to read out of bounds. Offset: {fe.offset}")
                    raise
        return file_
