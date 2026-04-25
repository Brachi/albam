from ...registry import blender_registry

import os
from .structs.lfs import Lfs
from .structs.udas import Udas
from .structs.pack import Pack
from ...albam_vendor import xcompress


@blender_registry.register_archive_loader(app_id="re4uhd", extension="lfs")
def lfs_loader(vfile, context=None):
    print(vfile.absolute_path)
    lfs = LfsWrapper(file_path=vfile.absolute_path)
    for file_entry in lfs.get_file_entries():
        yield file_entry.file_path_with_ext


@blender_registry.register_archive_accessor(app_id="re4uhd", extension="lfs")
def arc_accessor(vfile, context):
    lfs = LfsWrapper(vfile.root_vfile.absolute_path)

    path = vfile.relative_path_windows
    path_no_ext = str(vfile.relative_path_windows_no_ext)
    ext = path.suffix.replace(".", "")
    file_type = ext
    file_bytes = lfs.get_file(path_no_ext, file_type)

    return file_bytes


class LfsWrapper:
    PATH_SEPARATOR = "\\"

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_type = self._get_all_extensions(file_path)[0]
        self.compressed = Lfs.from_file(file_path)
        self.compressed._read()
        self.parsed = self.decompress()

    def decompress(self):
        decompressed = xcompress.xcompress_decompress_re4hd(self.compressed.file_entries)
        if self.file_type == ".udas":
            udas = Udas.from_bytes(decompressed)
            udas._read()
            return udas
        elif self.file_type == ".pack":
            pack = Pack.from_bytes(decompressed)
            pack._read()
            return pack
        else:
            raise NotImplementedError(f"Unknown file type {self.file_type}")

    def get_file_entries(self):
        file_entries = []
        if self.file_type == ".udas":
            udas = self.parsed
            fe_base_name = os.path.basename(self.file_path)
            fe_base_name = fe_base_name.split(".")[0] + "_"
            for i, fe in enumerate(udas.header.data_blocks.file_entries):
                ext = udas.header.data_blocks.file_extension[i].ext
                if not ext:
                    ext = "NULL"
                fe.file_path_with_ext = f"{fe_base_name}{str(i).zfill(3)}.{ext}"
                file_entries.append(fe)
        elif self.file_type == ".pack":
            pack = self.parsed
            fe_base_name = os.path.basename(self.file_path)
            fe_base_name = fe_base_name.split(".")[0] + "_"
            for i, fe in enumerate(pack.file_entries):
                ext = ".dds" if fe.data.is_dds else ".tga"
                fe.file_path_with_ext = f"{fe_base_name}{str(i).zfill(3)}{ext}"
                file_entries.append(fe)
        return file_entries

    def get_file(self, file_path_no_ext, file_type):
        file_id = int(file_path_no_ext.split("_")[-1])
        if self.file_type == ".udas":
            for i,  fe in enumerate(self.parsed.header.data_blocks.file_entries):
                if i == file_id and self.parsed.header.data_blocks.file_extension[i].ext == file_type:
                    return fe.raw_data
        elif self.file_type == ".pack":
            for i, fe in enumerate(self.parsed.file_entries):
                ext = ".dds" if fe.data.is_dds else ".tga"
                if i == file_id and ext.replace(".", "") == file_type:
                    return fe.data.raw_data
        raise RuntimeError(f"File {file_path_no_ext} with type {file_type} not found in {self.file_path}")

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
