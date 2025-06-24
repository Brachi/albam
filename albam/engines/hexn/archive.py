import zlib

from .structs.hexane_ssg import HexaneSsg
from albam.registry import blender_registry


@blender_registry.register_archive_loader(app_id="reorc", extension="ssg")
def ssg_loader(vfile, context=None):
    ssg = SSGWrapper(file_path=vfile.absolute_path)
    for file_path, _ in ssg.get_file_entries():
        yield file_path


@blender_registry.register_archive_accessor(app_id="reorc", extension="ssg")
def ssg_accessor(vfile, context):
    ssg = SSGWrapper(file_path=vfile.root_vfile.absolute_path)
    file_bytes = ssg.get_file(vfile.relative_path)
    return file_bytes


class SSGWrapper:

    def __init__(self, file_path):
        self.file_path = file_path
        self.parsed = HexaneSsg.from_file(file_path)
        self._file_entries = []

    def get_file_entries(self):
        if self._file_entries:
            return self._file_entries
        counter = 0
        uncompressed_buffer = bytearray()
        for chunk_size in self.parsed.chunk_sizes:
            if not chunk_size:
                continue
            uncompressed = zlib.decompress(self.parsed.buffer_chunks[counter:counter + chunk_size])
            uncompressed_buffer.extend(uncompressed)
            counter += chunk_size

        pos = 0
        for file_info in self.parsed.files_info:
            file_bytes = uncompressed_buffer[pos: pos + file_info.size]
            pos += file_info.size + (-file_info.size % self.parsed.size_padding)
            self._file_entries.append((file_info.name, file_bytes))

        return self._file_entries

    def get_file(self, file_path):
        # breakpoint()
        file_ = None
        for file_entry_path, file_bytes in self.get_file_entries():
            if file_path == file_entry_path:
                file_ = file_bytes
        return file_
