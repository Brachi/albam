from .fs import LfsFS
from ...registry import blender_registry


@blender_registry.register_fs_root_loader(app_id="re4uhd", extension="lfs")
def lfs_fs_root_loader(absolute_path):
    return LfsFS(absolute_path)
