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
    pass


class SSGWrapper:

    def __init__(self, file_path):
        self.file_path = file_path
        self.parsed = HexaneSsg.from_file(file_path)

    def get_file_entries(self):
        counter = 0
        uncompressed_buffer = bytearray()
        for chunk_size in self.parsed.chunk_sizes:
            if not chunk_size:
                continue
            uncompressed = zlib.decompress(self.parsed.buffer_chunks[counter:counter + chunk_size])
            uncompressed_buffer.extend(uncompressed)
            counter += chunk_size

        files = []
        pos = 0
        for file_info in self.parsed.files_info:
            file_bytes = uncompressed_buffer[pos: pos + file_info.size]
            pos += file_info.size + (-file_info.size % self.parsed.size_padding)
            files.append((file_info.name, file_bytes))

        return files
