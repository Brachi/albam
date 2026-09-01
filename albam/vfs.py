import copy
import os
from pathlib import PureWindowsPath, Path

import bpy
from bpy.app.handlers import persistent
from fs.memoryfs import MemoryFS
from fs.path import dirname

from .apps import APPS
from .lib import fs_registry
from .registry import blender_registry


def _extension_from_name(name):
    """
    Allow up to 2 dots as an extension when the naive (single-dot) extension
    is purely numeric - e.g. "texname.tex.34" -> "tex.34", "pl0000.mesh.2109108288"
    -> "mesh.2109108288" (RE Engine's own versioned-format naming, where the
    trailing number alone doesn't identify the format on its own). Otherwise
    just the naive extension - e.g. "re_chunk_000.pak.patch_999.pak" -> "pak",
    not "patch_999.pak": a real RE Engine patch pak's ".patch_NNN" segment is
    the patch number, not a versioned extension, and misreading it as one
    broke fs_root_loader/archive_loader dispatch for "Add Files" on any real
    patch pak, not just an oddly-named one.

    Single source of truth for VirtualFile.extension/VirtualFileData.extension
    too (both just delegate here) - used standalone here since add_real_file's
    FS-root dispatch needs this before a VirtualFile exists yet.
    """
    SEP = "."
    stem, _, extension = name.rpartition(SEP)
    if SEP in stem:
        _, __, extension0 = stem.rpartition(SEP)
        if extension.isdigit():
            extension = SEP.join((extension0, extension))
    return extension


@blender_registry.register_blender_prop
class TreeNode(bpy.types.PropertyGroup):
    node_id: bpy.props.StringProperty()
    root_id: bpy.props.StringProperty()
    depth: bpy.props.IntProperty(default=0)


@blender_registry.register_blender_prop
class VirtualFile(bpy.types.PropertyGroup):
    display_name: bpy.props.StringProperty()
    absolute_path: bpy.props.StringProperty()
    relative_path: bpy.props.StringProperty()  # posix style
    is_archive: bpy.props.BoolProperty(default=False)
    is_root: bpy.props.BoolProperty(default=False)
    is_expandable: bpy.props.BoolProperty(default=False)
    is_expanded: bpy.props.BoolProperty(default=False)
    albam_asset_type: bpy.props.StringProperty()  # TODO: enum albam.asset.AlbamAssetType
    tree_node: bpy.props.PointerProperty(type=TreeNode)  # consider adding the attributes here directly
    # FIXME: consider strings, seems pretty inefficient
    tree_node_ancestors: bpy.props.CollectionProperty(type=TreeNode)

    app_id: bpy.props.EnumProperty(name="", description="", items=APPS)
    vfs_id: bpy.props.StringProperty()

    data_bytes: bpy.props.StringProperty(subtype="BYTE_STRING")  # noqa: F821
    # Set on root nodes created via add_fs_root(): key into fs_registry for
    # the live fs.base.FS instance backing this root (bpy.types.PropertyGroup
    # can't hold that object directly). Empty for roots/nodes still going
    # through the legacy archive_loader/archive_accessor registries.
    fs_key: bpy.props.StringProperty()

    @property
    def relative_path_windows(self):
        return self._get_relative_path_windows()

    @property
    def relative_path_windows_no_ext(self):
        return self._get_relative_path_windows(include_extension=False)

    @property
    def root_vfile(self):
        vfs = self.get_vfs()
        try:
            return vfs.file_list[self.tree_node.root_id]
        except KeyError:
            return None

    @property
    def extension(self):
        """See _extension_from_name()."""
        return _extension_from_name(self.display_name)

    @property
    def fs_path(self):
        return "/" + str(self.relative_path).replace("\\", "/")

    def get_bytes(self):
        root = self.root_vfile
        if root and root.fs_key:
            return root_fs(root).readbytes(self.fs_path)
        accessor = self.get_accessor()
        return accessor(self, bpy.context)

    def get_accessor(self):
        if self.absolute_path:
            return self.real_file_accessor
        if self.data_bytes:
            return lambda vfile, context: self.data_bytes
        vfs = self.get_vfs()
        root = vfs.file_list[self.tree_node.root_id]
        accessor_func = blender_registry.archive_accessor_registry.get(
            (self.app_id, root.extension)
        )
        if not accessor_func:
            raise RuntimeError("Archive item doesn't have an accessor")

        return accessor_func

    @staticmethod
    def real_file_accessor(file_item, context):
        with open(file_item.absolute_path, 'rb') as f:
            return f.read()

    def get_vfs(self):
        """The vfs collection this file actually belongs to - resolved
        through the scene owning it (`id_data`), not through
        bpy.context.scene: a file lives in one specific scene's albam data,
        and looking it up in whichever scene happens to be active resolves
        roots (and therefore bytes) from the wrong file list entirely.
        """
        scene = self.id_data
        return getattr(scene.albam, self.vfs_id)

    def _get_relative_path_windows(self, include_extension=True):
        p = PureWindowsPath(self.relative_path)
        if not include_extension:
            return PureWindowsPath(*p.parts[:-1] + (p.stem,))
        return p


class VirtualFileSystemBase:
    file_list: bpy.props.CollectionProperty(type=VirtualFile)
    file_list_selected_index: bpy.props.IntProperty()

    SEPARATOR = "::"
    VFS_ID = "vfs"

    def get_vfile(self, app_id, relative_path):
        path = PureWindowsPath(relative_path)
        file_id = self.SEPARATOR.join((app_id,) + path.parts)
        return self.file_list[file_id]

    def select_vfile(self, app_id, relative_path):
        path = PureWindowsPath(relative_path)
        file_id = self.SEPARATOR.join((app_id,) + path.parts)
        self.file_list_selected_index = self.file_list.find(file_id)
        return self.file_list[file_id]

    def add_real_file(self, app_id, absolute_path):
        path = PureWindowsPath(absolute_path)
        extension = _extension_from_name(path.name)

        # A single archived file (e.g. one .arc) has its own loader keyed by
        # extension; a folder has none (no meaningful extension), so it falls
        # through to the whole-folder loader keyed by (app_id, None), if any.
        fs_loader = (blender_registry.fs_root_loader_registry.get((app_id, extension)) or
                     blender_registry.fs_root_loader_registry.get((app_id, None)))
        if fs_loader:
            self.add_fs_root(
                app_id, fs_loader(absolute_path), display_name=path.name,
                is_archive=bool(extension), absolute_path=absolute_path,
            )
            return

        vf = self.file_list.add()
        vf.is_root = True
        vf.name = f"{app_id}::{path.name}"
        vf.vfs_id = self.VFS_ID
        vf.app_id = app_id
        vf.display_name = path.name
        vf.absolute_path = absolute_path

        archive_loader_func = blender_registry.archive_loader_registry.get(
            (vf.app_id, vf.extension)
        )
        if archive_loader_func:
            vf.is_expandable = True
            vf.is_archive = True
            self._expand_archive(archive_loader_func, vf, app_id)
        else:
            vf.is_expandable = True
            vf.is_archive = False
            self._expand_directory(absolute_path, vf, app_id)

    def add_fs_root(self, app_id, fs_instance, display_name, is_archive=False, absolute_path=""):
        """
        Register `fs_instance` (any fs.base.FS) as a new root, sourcing its
        whole file tree via one fs_instance.walk() pass instead of an
        engine-specific archive_loader/archive_accessor. Bytes for every node
        under this root are read on demand straight from `fs_instance`
        (see VirtualFile.get_bytes()), never duplicated into a bpy property.
        """
        fs_key = fs_registry.register(fs_instance)

        root_id = f"{app_id}::{display_name}"
        vf = self.file_list.add()
        vf.is_root = True
        vf.name = root_id
        vf.vfs_id = self.VFS_ID
        vf.app_id = app_id
        vf.display_name = display_name
        vf.absolute_path = absolute_path
        vf.fs_key = fs_key
        vf.is_expandable = True
        vf.is_archive = is_archive

        tree = Tree(root_id=root_id, app_id=app_id)
        for file_path in fs_instance.walk.files():
            tree.add_node_from_path(file_path.lstrip("/"))
        for node in tree.flatten():
            self._add_vf_from_treenode(app_id, root_id, node)

        # Re-fetch: further file_list.add() calls above can invalidate the
        # `vf` reference taken before the loop (same Blender CollectionProperty
        # quirk _expand_archive's comment warns about) - look it up fresh by
        # the plain-string root_id instead of trusting the stale object.
        return self.file_list[root_id]

    def add_export_root(self, app_id, display_name, vfiles_data):
        """
        Stage freshly-exported bytes (VirtualFileData, as returned by an
        engine's export function) in a writable in-memory FS and register it
        as a new root via add_fs_root() - the export-side counterpart of its
        read-only archive/game-folder roots, sharing the same tree-building
        and get_bytes() machinery instead of duplicating bytes into
        data_bytes.

        A child file's node id is `app_id::<relative path parts>` (see
        select_vfile()/get_vfile()) and isn't scoped by which root added it -
        each root here gets its own unique display_name (see
        ALBAM_OT_Export._execute()), but re-exporting the same
        (app_id, relative_path) still produces a second file_list entry with
        an identical id. Blender's CollectionProperty name lookup
        (file_list[id]/file_list.find(id)) returns the *first* match, so
        without this, select_vfile() on that identity would keep returning
        the previous export's bytes forever after, silently - purge every
        earlier entry for each identity this export is about to add, so the
        new one (added below via add_fs_root()) is the one found. Scoped to
        the export root only - add_fs_root()'s read-only archive/game-folder
        mount path has its own separate "mounting the same folder twice"
        sharp edge (see game_fs_root()'s docstring), left alone here.
        """
        mem_fs = MemoryFS()
        for vfile_data in vfiles_data:
            path = "/" + str(vfile_data.relative_path).replace("\\", "/")
            mem_fs.makedirs(dirname(path), recreate=True)
            mem_fs.writebytes(path, vfile_data.data_bytes or b"")

            file_id = self.SEPARATOR.join(
                (app_id,) + PureWindowsPath(vfile_data.relative_path).parts)
            stale_index = self.file_list.find(file_id)
            while stale_index != -1:
                self.file_list.remove(stale_index)
                stale_index = self.file_list.find(file_id)

        return self.add_fs_root(app_id, mem_fs, display_name=display_name)

    def _expand_archive(self, archive_loader_func, vf, app_id):
        # Beware of chaning this, it was observed the reference
        # is lost in the middle of the loop below if using vf.name directly,
        # we get an empty string instead! Don't know why
        root_id = vf.name
        tree = Tree(root_id=vf.name, app_id=app_id)
        # TODO: popup if calling failed. Known exceptions + unexpected
        for rel_path in archive_loader_func(vf):
            tree.add_node_from_path(rel_path)
        for node in tree.flatten():
            self._add_vf_from_treenode(app_id, root_id, node)

    def _abs_to_rel_path(self, path_to_file, root_path):
        abs_path = Path(path_to_file)
        root_path = Path(root_path)
        return abs_path.relative_to(root_path)

    def _expand_directory(self, root_folder, vf, app_id):
        root_id = vf.name
        tree = Tree(root_id=vf.name, app_id=app_id)

        max_files = 60000
        file_count = 0
        for files_folder, dirs, files in os.walk(root_folder):
            for file in files:
                if file_count >= max_files:
                    print(f"Reached the max file limit of {max_files}, change if needed")
                    break
                file_count += 1
                rel_path = os.path.join(self._abs_to_rel_path(files_folder, root_folder), file)
                abs_path = os.path.join(files_folder, file)
                tree.add_node_from_path(rel_path, absolute_path=abs_path)
        for node in tree.flatten():
            self._add_vf_from_treenode(app_id, root_id, node)

    def _add_vf_from_treenode(self, app_id, root_id, node):
        child_vf = self.file_list.add()
        child_vf.vfs_id = self.VFS_ID
        child_vf.app_id = app_id
        child_vf.name = node["node_id"]
        child_vf.relative_path = node["relative_path"]
        child_vf.absolute_path = node["full_path"]
        child_vf.display_name = node["name"]
        child_vf.is_expandable = bool(node["children"])
        child_vf.albam_asset_type = blender_registry.albam_asset_types.get((app_id, child_vf.extension), "")
        child_vf.tree_node.depth = node["depth"] + 1
        child_vf.tree_node.root_id = root_id
        for ancestor_id in node["ancestors_ids"]:
            ancestor_node = child_vf.tree_node_ancestors.add()
            ancestor_node.node_id = ancestor_id

    @property
    def selected_vfile(self):
        if len(self.file_list) == 0:
            return None
        index = self.file_list_selected_index
        try:
            vfile = self.file_list[index]
        except IndexError:
            # list might have been cleared
            return
        if not vfile.is_root and vfile.is_expandable:
            return None
        return vfile


def _fs_root_loader(vf):
    """The registered fs_root_loader able to rebuild root `vf`'s FS: keyed by
    the root's own extension for an archive root ("Add Files"), falling back
    to the whole-folder loader ("Add Folder"), same as add_real_file().
    """
    return (blender_registry.fs_root_loader_registry.get((vf.app_id, vf.extension)) or
            blender_registry.fs_root_loader_registry.get((vf.app_id, None)))


def reconnect_fs_root(vf):
    """
    Rebuild the fs_registry entry backing root `vf` - under the `fs_key` it
    already carries, not a fresh one - and return the live FS instance.

    fs_registry is plain in-process state (see its module docstring): it
    isn't part of the .blend file, and it's also dropped mid-session
    whenever the add-on is re-registered (Reload Scripts, an extension
    update, a disable/enable cycle - unregister() calls fs_registry.clear()).
    A root's `fs_key`/`absolute_path` are real bpy.props that outlive both,
    so the entry can be recreated the same way add_real_file() created it
    the first time.
    """
    if not vf.absolute_path:
        raise RuntimeError(
            f"VFS root {vf.display_name!r} has no path on disk to mount again - it only "
            f"ever existed in memory (e.g. an export root), so it's gone for this session"
        )
    fs_loader = _fs_root_loader(vf)
    if not fs_loader:
        raise RuntimeError(
            f"VFS root {vf.display_name!r} has no fs_root_loader registered for "
            f"app_id={vf.app_id!r} to mount it again with"
        )
    fs_instance = fs_loader(vf.absolute_path)
    fs_registry.reconnect(vf.fs_key, fs_instance)
    return fs_instance


def root_fs(root_vf):
    """
    The live FS instance backing root `root_vf`, mounting it again on demand
    if this process's fs_registry doesn't have it (any more) - see
    reconnect_fs_root(). Going through here instead of straight to
    fs_registry.get() keeps a root readable in every case the load_post
    handler below can't cover: the add-on being re-registered mid-session,
    roots living in a scene that wasn't the active one when the file loaded,
    or a file loaded before the add-on was enabled at all. Otherwise the
    first read of such a root raises a bare KeyError on a uuid, from
    wherever an importer happened to ask for bytes.
    """
    try:
        return fs_registry.get(root_vf.fs_key)
    except KeyError:
        print(f"albam: mounting VFS root {root_vf.display_name!r} again "
              f"from {root_vf.absolute_path!r}")
        return reconnect_fs_root(root_vf)


@persistent
def reconnect_fs_roots(dummy):
    """
    Mount every FS-backed root in the freshly-loaded file again, so the
    `fs_key` values restored from it keep pointing at something live (see
    reconnect_fs_root() for what drops them). Doing it up front here keeps
    the first read of a root predictable - a whole game folder can take a
    while to mount - while get_bytes() still falls back to mounting lazily
    for any root this misses. Roots with no `absolute_path`
    (add_export_root()'s in-memory FS) can't be recreated this way and are
    left as-is - they're transient, run-only state to begin with.
    """
    for scene in bpy.data.scenes:
        albam_data = getattr(scene, "albam", None)
        if albam_data is None:
            continue
        for vfs_id in ("vfs", "exported"):
            vfs = getattr(albam_data, vfs_id, None)
            if vfs is None:
                continue
            for vf in vfs.file_list:
                if not (vf.is_root and vf.fs_key and vf.absolute_path):
                    continue
                try:
                    reconnect_fs_root(vf)
                except Exception as err:
                    print(f"albam: could not reconnect VFS root {vf.display_name!r}: {err}")


@blender_registry.register_blender_prop_albam(name="vfs")
class VirtualFileSystem(VirtualFileSystemBase, bpy.types.PropertyGroup):
    pass


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemAddFiles(bpy.types.Operator):
    """Add files to the virtual file system"""
    bl_idname = "albam.add_files"
    bl_label = "Add Files"
    directory: bpy.props.StringProperty(subtype="DIR_PATH")  # NOQA
    files: bpy.props.CollectionProperty(name="added_files", type=bpy.types.OperatorFileListElement)  # NOQA
    # FIXME: use registry, un-hardcode
    filter_glob: bpy.props.StringProperty(default="*.arc;*.pak;*.lfs", options={"HIDDEN"})  # NOQA

    def invoke(self, context, event):  # pragma: no cover
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):  # pragma: no cover
        self._execute(context, self.directory, self.files)
        context.scene.albam.vfs.file_list.update()
        return {"FINISHED"}

    @staticmethod
    def _execute(context, directory, files):
        app_id = context.scene.albam.apps.app_selected
        vfs = context.scene.albam.vfs
        for f in files:
            absolute_path = os.path.join(directory, f.name)
            vfs.add_real_file(app_id, absolute_path)


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemAddFolder(bpy.types.Operator):
    """Add folder to the virtual file system"""
    bl_idname = "albam.add_folder"
    bl_label = "Add Folder"
    directory: bpy.props.StringProperty(subtype='DIR_PATH')  # NOQA
    files: bpy.props.CollectionProperty(name="added_files", type=bpy.types.OperatorFileListElement)  # NOQA

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):  # pragma: no cover
        self.report({'INFO'}, f"Selected directory: {self.directory}")
        self._execute(context, self.directory, self.files)
        return {"FINISHED"}

    @staticmethod
    def _execute(context, directory, files):
        app_id = context.scene.albam.apps.app_selected
        vfs = context.scene.albam.vfs
        vfs.add_real_file(app_id, directory)


class ALBAM_OT_VirtualFileSystemSaveFileBase:
    CHECK_EXISTING = bpy.props.BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )
    FILEPATH = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    bl_idname = "albam.save_file"
    bl_label = "Save files"
    bl_description = "Save selected item as a new file"
    check_existing: CHECK_EXISTING
    filepath: FILEPATH

    VFS_ID = "vfs"

    def invoke(self, context, event):  # pragma: no cover
        vfs = self.get_vfs(self, context)
        vfile = vfs.selected_vfile
        self.filepath = vfile.display_name
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):  # pragma: no cover
        vfile = self.get_vfs(self, context).selected_vfile
        with open(self.filepath, 'wb') as w:
            w.write(vfile.get_bytes())
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        selected = cls.get_vfs(cls, context).selected_vfile
        is_root = False
        if selected:
            is_root = getattr(selected, "is_root")
        return selected and not is_root

    @staticmethod
    def get_vfs(cls_or_self, context):
        return getattr(context.scene.albam, cls_or_self.VFS_ID)


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemSaveFile(
        ALBAM_OT_VirtualFileSystemSaveFileBase, bpy.types.Operator):
    VFS_ID = "vfs"


class ALBAM_OT_VirtualFileSystemCollapseToggleBase:

    button_index: bpy.props.IntProperty(default=0)
    VFS_ID = None
    NODES_CACHE = None

    def execute(self, context):
        item_index = self.button_index
        vfs = getattr(context.scene.albam, self.VFS_ID)
        item_list = vfs.file_list
        item = item_list[item_index]
        item.is_expanded = not item.is_expanded
        if item.is_root:
            cache_key = item.name
        else:
            cache_key = item.tree_node.root_id
        if cache_key not in self.NODES_CACHE.keys():
            self.NODES_CACHE[cache_key] = {}
        self.NODES_CACHE[cache_key][item.name] = item.is_expanded

        vfs.file_list_selected_index = self.button_index
        item_list.update()
        return {"FINISHED"}


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemCollapseToggle(
        ALBAM_OT_VirtualFileSystemCollapseToggleBase, bpy.types.Operator):

    bl_idname = "albam.file_item_collapse_toggle"
    bl_label = "ALBAM_OT_VirtualFileSystemCollapseToggle"
    VFS_ID = "vfs"
    NODES_CACHE = {}


class ALBAM_OT_VirtualFileSystemRemoveRootVFileBase:
    bl_idname = "albam.remove_imported"
    bl_label = "Remove imported files"
    bl_description = "Remove files from the virtual file system"
    VFS_ID = ""

    def execute(self, context):
        vfs = getattr(context.scene.albam, self.VFS_ID)
        vfiles_to_remove = []
        root_node_index = vfs.file_list_selected_index
        archive_node = vfs.file_list[root_node_index]
        archive_node_name = archive_node.name
        archive_node_fs_key = archive_node.fs_key
        for i in range(len(vfs.file_list)):
            parent = vfs.file_list[i].tree_node.root_id
            if parent == archive_node_name:
                vfiles_to_remove.append(i)

        vfiles_to_remove.reverse()
        for i in range(len(vfiles_to_remove)):
            vfs.file_list.remove(vfiles_to_remove[i])
        vfs.file_list.remove(root_node_index)

        if archive_node_fs_key:
            fs_registry.unregister(archive_node_fs_key)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        vfs = getattr(context.scene.albam, cls.VFS_ID)
        current_item = vfs.selected_vfile
        return current_item and current_item.is_root


@blender_registry.register_blender_type
class ALBAM_OT_VirtualFileSystemRemoveRootVFile(
        ALBAM_OT_VirtualFileSystemRemoveRootVFileBase, bpy.types.Operator):
    """Remove files from vitual files system"""
    bl_idname = "albam.remove_imported"
    bl_label = "Remove imported files"
    VFS_ID = "vfs"


class VirtualFileData:
    # FIXME: normalize to posix path!

    def __init__(self, app_id, relative_path, data_bytes=None):
        self.app_id = app_id
        self.relative_path = relative_path
        self.name = os.path.basename(relative_path)  # TODO: posix only
        self.data_bytes = data_bytes

    @property
    def extension(self):
        """See _extension_from_name()."""
        return _extension_from_name(self.relative_path)


class Tree:
    PATH_SEPARATOR = "::"
    OS_PATH_SEPARATOR = "/"

    def __init__(self, root_id=None, app_id=None):  # FIXME: make app_id mandatory
        self.root = []
        self.root_id = root_id
        self.nodes = {}
        self.app_id = app_id

    def _find_node_in_level(self, node_name, node_level):
        node_found = None
        for node in node_level:
            if node["name"] == node_name:
                node_found = node
                break
        return node_found

    def add_node_from_path(self, full_path, absolute_path=""):
        p = PureWindowsPath(full_path)
        path_parts = p.parts
        # FIXME: adding a single root node doesn't work
        # E.g. when importing a single file mod, it doesn't have
        # albam_asset.relative_path properly set, and when exporting
        # the file will be nameless
        leaf_name = path_parts[-1] if path_parts else p.name

        current_level = 0
        current_dir = self.root
        ancestors_ids = [] if not self.root_id else [self.root_id]
        for i in range(len(path_parts) - 1):
            path_part = path_parts[i]
            existing_node = self._find_node_in_level(node_name=path_part, node_level=current_dir)
            if existing_node:
                new_node = existing_node
            else:
                new_node = {
                    "name": path_part,
                    "children": [],
                    "depth": current_level,
                    "node_id": self.generate_node_id(path_parts[0 : i + 1], use_prefix=True),
                    "relative_path": self.generate_node_id(path_parts[0 : i + 1], use_prefix=False),
                    "full_path": absolute_path,
                    "ancestors_ids": copy.copy(ancestors_ids),

                }
                current_dir.append(new_node)
                self.nodes[new_node["node_id"]] = new_node

            ancestors_ids.append(new_node["node_id"])
            current_level += 1
            current_dir = new_node["children"]

        node_id = self.generate_node_id(path_parts, use_prefix=True)
        leaf_node = {
            "name": leaf_name,
            "children": [],
            "depth": current_level,
            "node_id": node_id,
            "relative_path": self.generate_node_id(path_parts, use_prefix=False),
            "full_path": absolute_path,
            "ancestors_ids": ancestors_ids,
        }
        current_dir.append(leaf_node)
        self.nodes[node_id] = leaf_node

    def generate_node_id(self, parts, use_prefix=True):
        prefix = (self.app_id or "") + self.PATH_SEPARATOR
        sep = self.PATH_SEPARATOR if use_prefix else self.OS_PATH_SEPARATOR
        body = sep.join(parts)
        if use_prefix:
            return prefix + body
        return body

    @staticmethod
    def sort_node(node):
        """
        Sort expandable items first
        """
        return node['name'] if node['children'] else "zzz" + node['name']

    def flatten(self, flat_tree=None, current_level=None):
        flat_tree = flat_tree or []
        current_level = current_level or self.root

        for node in sorted(current_level, key=self.sort_node):
            flat_tree.append(node)
            if node['children']:
                self.flatten(flat_tree, node['children'])
        return flat_tree
