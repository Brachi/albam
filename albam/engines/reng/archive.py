import bpy

from ...registry import blender_registry
from .pak_fs import PakFS, ReenFS


def _get_path_list_file():
    # Set via the App Settings popup (RE Engine apps only), persisted in
    # apps-userdata.ini the same way app_dir is - see
    # albam/blender_ui/import_panel.py's path_list_file property. A .pak's
    # file entries carry only hashes, not paths, so this is required to
    # resolve anything at all (see pak_fs.py's module docstring).
    path_list_file = bpy.context.scene.albam.apps.path_list_file
    if not path_list_file:
        app_id = bpy.context.scene.albam.apps.app_selected
        raise RuntimeError(
            f'App "{app_id}" has no path list file configured - set it via the '
            "App Settings popup next to the app selector"
        )
    return path_list_file


@blender_registry.register_fs_root_loader(app_id="re2", extension="pak")
@blender_registry.register_fs_root_loader(app_id="re2_non_rt", extension="pak")
@blender_registry.register_fs_root_loader(app_id="re3", extension="pak")
@blender_registry.register_fs_root_loader(app_id="re3_non_rt", extension="pak")
@blender_registry.register_fs_root_loader(app_id="re8", extension="pak")
def pak_fs_root_loader(absolute_path):
    return PakFS(absolute_path, _get_path_list_file())


@blender_registry.register_fs_root_loader(app_id="re2", extension=None)
@blender_registry.register_fs_root_loader(app_id="re2_non_rt", extension=None)
@blender_registry.register_fs_root_loader(app_id="re3", extension=None)
@blender_registry.register_fs_root_loader(app_id="re3_non_rt", extension=None)
@blender_registry.register_fs_root_loader(app_id="re8", extension=None)
def reen_fs_root_loader(absolute_path):
    return ReenFS(absolute_path, _get_path_list_file())
