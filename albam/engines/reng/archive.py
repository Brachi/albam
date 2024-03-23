import io
import struct

import bpy
from kaitaistruct import KaitaiStream
import pymmh3 as mmh3
import zlib
import zstd

from albam.registry import blender_registry
from .structs.pak import Pak


@blender_registry.register_archive_loader(app_id="re2", extension='pak')
@blender_registry.register_archive_loader(app_id="re3", extension='pak')
@blender_registry.register_archive_loader(app_id="re8", extension='pak')
@blender_registry.register_archive_loader(app_id="re2_non_rt", extension='pak')
@blender_registry.register_archive_loader(app_id="re3_non_rt", extension='pak')
def pak_loader(file_item):
    app_config_filepath = bpy.context.scene.albam.apps.app_config_filepath
    app_id = file_item.app_id  # blender bug, needs reference or might mutate
    if not app_config_filepath:
        # TODO: custom exception that will result in informative popup
        print("WARNING: no app_config_filepath")
        return
    pak = PakWrapper(app_id, file_item.absolute_path, app_config_filepath)
    for path in pak.paths:
        yield path.strip()


@blender_registry.register_archive_accessor(app_id="re2", extension="pak")
@blender_registry.register_archive_accessor(app_id="re2_non_rt", extension="pak")
@blender_registry.register_archive_accessor(app_id="re3", extension="pak")
@blender_registry.register_archive_accessor(app_id="re3_non_rt", extension="pak")
@blender_registry.register_archive_accessor(app_id="re8", extension="pak")
def pak_accessor(vfile, context):
    app_config_filepath = context.scene.albam.apps.get_app_config_filepath(vfile.app_id)
    if not app_config_filepath:
        # TODO: custom exception that will result in informative popup, with solution
        raise RuntimeError(f'App "{vfile.app_id}" doesn\'t have its file config loaded')
    pak = PakWrapper(vfile.app_id, vfile.root_vfile.absolute_path, app_config_filepath)
    return pak.get_file(vfile.relative_path)


class PakWrapper:
    PATH_SEPARATOR = "/"
    HEADER_SIZE = 16
    NUM_FILES_OFFSET = 8
    FILE_ENTRY_SIZE = 48
    SEED = 0xFFFFFFFF

    def __init__(self, app_id, file_path, file_list_path):
        self.app_id = app_id
        self.file_path = file_path
        self.file_list_path = file_list_path
        self._tree = None
        self.paths = set()
        with open(file_path, "rb") as f:
            f.seek(8)
            num_file_entries = struct.unpack("I", f.read(4))[0]
            f.seek(0)
            read_size = self.HEADER_SIZE + self.FILE_ENTRY_SIZE * num_file_entries
            self.parsed = Pak(KaitaiStream(io.BytesIO(f.read(read_size))))

        with open(self.file_list_path) as f:
            for path in f:
                self.paths.add(path)

    def get_file(self, file_path):
        file_entry = None
        file_bytes = None
        file_path_hash = mmh3.hash(file_path.encode('utf-16')[2:], self.SEED) & self.SEED

        for fe in self.parsed.file_entries:
            if fe.file_path_hash_case_insensitive == file_path_hash:
                file_entry = fe
                break
        else:
            print("[PakWrapper] WARNING:file path not found:", file_path, file_path_hash)

        # FIXME: proper exception when the path is not found or avoid it (warning in UI)
        with open(self.file_path, "rb") as f:
            f.seek(file_entry.offset)
            if file_entry.flags & 1:
                file_bytes = zlib.decompress(f.read(file_entry.zsize), -15)
            elif file_entry.flags & 2:
                file_bytes = zstd.decompress(f.read(file_entry.zsize))
            else:
                file_bytes = f.read(file_entry.zsize)
        return file_bytes
