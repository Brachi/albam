from ...registry import blender_registry

import os
from .structs.lfs import Lfs
from .structs.udas import Udas
from ...albam_vendor import xcompress


@blender_registry.register_archive_loader(app_id="re4uhd", extension="lfs")
def lfs_loader(vfile, context=None):
    print(vfile.absolute_path)
    lfs = LfsWrapper(file_path=vfile.absolute_path)
    for file_entry in lfs.get_file_entries():
        yield file_entry.file_path_with_ext


@blender_registry.register_archive_accessor(app_id="re4uhd", extension="lfs")
def arc_accessor(vfile, context):
    print("accsessor")
    lfs = LfsWrapper(vfile.root_vfile.absolute_path)


class LfsWrapper:
    PATH_SEPARATOR = "\\"

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_type = self._get_all_extensions(file_path)[0]
        self.compressed = Lfs.from_file(file_path)
        self.compressed._read()
        self.parsed = None

    def get_file_entries(self):
        file_entries = []
        if self.file_type == ".udas":
            decompressed = xcompress.xcompress_decompress_re4hd(self.compressed.file_entries)
            udas = Udas.from_bytes(decompressed)
            udas._read()
            self.parsed = udas
            fe_base_name = os.path.basename(self.file_path)
            fe_base_name = fe_base_name.split(".")[0] + "_"
            for i, fe in enumerate(udas.header.data_blocks.file_entries):
                ext = udas.header.data_blocks.file_extension[i].ext
                fe.file_path_with_ext = f"{fe_base_name}{str(i).zfill(3)}.{ext}"
                file_entries.append(fe)
        return file_entries

    def _get_all_extensions(self, filepath):
        exts = []
        base = filepath
        while True:
            base, ext = os.path.splitext(base)
            if ext:
                exts.insert(0, ext)
            else:
                break
        return exts
