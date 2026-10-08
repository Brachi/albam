from .fs import HexnFS, SsgFS
from ...registry import blender_registry


@blender_registry.register_fs_root_loader(app_id="reorc", extension="ssg")
def ssg_fs_root_loader(absolute_path):
    return SsgFS(absolute_path)


@blender_registry.register_fs_root_loader(app_id="reorc", extension=None)
def game_fs_root_loader(absolute_path):
    return HexnFS(absolute_path)
