from ...registry import blender_registry

import bpy
from kaitaistruct import KaitaiStream
from .structs.lfs import Lfs
from .structs.udas import Udas
from ...albam_vendor import xcompress


@blender_registry.register_archive_loader(app_id="re4hd", extension="lfs")
def lfs_loader(vfile):
    lfs = LfsWrapper(file_path=vfile.absolute_path)
    for file_entry in lfs.get_file_entries():
        yield file_entry.file_path_with_ext


@blender_registry.register_archive_accessor(app_id="rehd", extension="lfs")
def arc_accessor(vfile, context):
    lfs = LfsWrapper(vfile.root_vfile.absolute_path)


class LfsWrapper:
    PATH_SEPARATOR = "\\"

    def __init__(self, file_path):
        self.file_path = file_path
        self.compressed = Lfs.from_file(file_path)
        self.compressed._read()

    def get_file_entries(self):
        file_entries = []
        return file_entries