import contextlib
import os

import bpy
import pytest

from tests.skip_policy import skip_missing


R2_PROTOCOL_PREFIX = "r2://"

# app_id -> the MTFW_FS instance already mounted as a VFS root this session -
# add_fs_root() must only run once per app_id (it always creates a new root;
# node ids are app_id::relative_path only, not scoped per-root, so adding
# the same game folder twice would create ambiguous duplicate entries).
_GAME_FS_INSTANCES = {}


def _game_dirs(pytestconfig):
    # Already validated (well-formed "<app-id>::<value>[::<extra>]", once, at
    # startup) by tests/conftest.py's pytest_configure - see there. <value>
    # is either a local directory path, or an explicit
    # "r2://<bucket>/<prefix>" value (see tests.mtfw.r2_config.resolve_r2_source)
    # selecting the R2 backend - never inferred from whether a local path
    # happens to exist. A third segment is reng-only (its own path-list -
    # see tests/reng/conftest.py) and simply ignored here.
    parsed = {}
    for app_id_and_dir in pytestconfig.getoption("game_dir") or []:
        app_id, value, *_reng_only = app_id_and_dir.split("::")
        parsed[app_id] = value
    return parsed


def _build_game_fs(pytestconfig, local_app_id):
    """The MTFW_FS --game-dir's value for local_app_id describes, freshly
    built (a brand new S3/R2 key listing for the r2:// case) - the mounting
    half of game_fs_root(), factored out so resolve_hashes_with_remount()
    can get a second, independent instance without touching
    _GAME_FS_INSTANCES' cache. Skips (raising via skip_missing) exactly as
    game_fs_root does for a bad/missing --game-dir.
    """
    from albam.engines.mtfw.arc_fs import MTFW_FS
    from tests.mtfw.r2_config import resolve_r2_source

    value = _game_dirs(pytestconfig).get(local_app_id)
    if not value:
        skip_missing(f"No --game-dir supplied for app_id={local_app_id!r}")
    elif value.startswith(R2_PROTOCOL_PREFIX):
        r2_kwargs = resolve_r2_source(value)
        if r2_kwargs is None:
            skip_missing(
                f"--game-dir={local_app_id}::{value} requested but R2 isn't configured "
                f"(empty bucket, missing s3 extras, or missing credentials - see "
                f".env.example)"
            )
        return MTFW_FS.from_s3(**r2_kwargs)
    elif not os.path.isdir(value):
        skip_missing(f"--game-dir={local_app_id}::{value} does not exist")
    return MTFW_FS(value)


@pytest.fixture(scope="session")
def game_fs_root(pytestconfig, local_app_id):
    """
    Mounts a VFS root for local_app_id via MTFW_FS (once per session, cached
    in _GAME_FS_INSTANCES) - the same mechanism "Add Folder" uses in the UI
    for a whole game install. Returns the MTFW_FS instance itself, so
    callers can resolve_hashes() against the exact same tree that got
    mounted into the VFS.

    Source is explicit in --game-dir's value, never inferred: a local path,
    or an explicit "r2://<bucket>/<prefix>" (see
    tests.mtfw.r2_config.resolve_r2_source for the R2/CI details). No
    --game-dir for this app_id skips outright.

    Scanning + flattening a full local game install's tree can take a while
    (a real RE5 install has ~1200 archives) - that cost is paid once per
    app_id per session, not per test.
    """
    if local_app_id not in _GAME_FS_INSTANCES:
        game_fs = _build_game_fs(pytestconfig, local_app_id)
        bpy.context.scene.albam.apps.app_selected = local_app_id
        vfs = bpy.context.scene.albam.vfs
        vfs.add_fs_root(local_app_id, game_fs, display_name=f"{local_app_id}-local")
        _GAME_FS_INSTANCES[local_app_id] = game_fs

    return _GAME_FS_INSTANCES[local_app_id]


def resolve_hashes_with_remount(pytestconfig, local_app_id, game_fs, target_hashes, attempts=2):
    """resolve_hashes(game_fs, target_hashes), retrying up to `attempts`
    more times against a brand new S3/R2 key listing (each mounted as its
    own extra VFS root, alongside game_fs_root's own) before giving up.

    A fresh listing of the exact same R2 bucket/prefix has been observed to
    come back without an archive a sibling pytest-xdist worker's listing of
    that same prefix found in the very same CI run (confirmed via
    MTFW_FS.failed_arcs being empty - the archive isn't failing to load,
    it's simply absent from this particular listing) - a second,
    independent listing has a chance not to repeat that, where retrying the
    same already-built game_fs cannot.
    """
    from tests.mtfw.scripts.catalog_paths import resolve_hashes

    fs = game_fs
    for _ in range(attempts):
        try:
            return resolve_hashes(fs, target_hashes)
        except KeyError:
            fs = _build_game_fs(pytestconfig, local_app_id)
            vfs = bpy.context.scene.albam.vfs
            vfs.add_fs_root(local_app_id, fs, display_name=f"{local_app_id}-retry")
    return resolve_hashes(fs, target_hashes)


def import_export(local_app_id, local_path):
    """Select local_path (already resolved from a committed hash, and
    already mounted into the VFS via game_fs_root) and run it through the
    real Blender import_vfile()/export() operators - the shared
    "select, import, export" step every *_local round-trip fixture needs.
    Returns the source vfile; callers fetch whatever exported vfile(s) they
    need afterward from bpy.context.scene.albam.exported, since what comes
    out varies (a straight copy for a standalone file, but also an
    accompanying .mrl alongside a mod).
    """
    vfs = bpy.context.scene.albam.vfs
    try:
        vfile = vfs.select_vfile(local_app_id, local_path)
    except KeyError:
        skip_missing(f"{local_path!r} not found under --game-dir for app_id={local_app_id!r}")

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    latest_exported = len(bpy.context.scene.albam.exportable.file_list) - 1
    bpy.context.scene.albam.exportable.file_list_selected_index = latest_exported
    result = bpy.ops.albam.export()  # FIXME: won't capture failures
    assert result == {"FINISHED"}
    return vfile


def import_vfile(local_app_id, local_path):
    """Select local_path (already resolved from a committed hash, and
    already mounted into the VFS via game_fs_root) and run it through the
    real Blender import_vfile() operator.

    The import-only half of import_export() above, for the tests that only
    care about what a file turns into in Blender - most notably apps albam
    can import but not yet export.
    """
    vfs = bpy.context.scene.albam.vfs
    try:
        vfile = vfs.select_vfile(local_app_id, local_path)
    except KeyError:
        skip_missing(f"{local_path!r} not found under --game-dir for app_id={local_app_id!r}")

    result = bpy.ops.albam.import_vfile()
    assert result == {"FINISHED"}
    return vfile


def clear_scene():
    """Drops everything a previous import left behind.

    Imports accumulate in bpy.data otherwise, so a per-model assertion like
    "this model built some materials" would really be reading the sum of
    every model imported before it - and a whole game's worth of models in
    one session would exhaust memory. Deleting objects only unlinks the
    meshes/images they used; orphans_purge is what actually frees them.
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for _ in range(3):
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)


def action_fcurves(action):
    """Every fcurve an action holds, whichever Blender version made it.

    The flat Action.fcurves shortcut is gone from 5.0 on - the same removal
    the LMT import tests exist to catch - so reading it directly here would
    break the tests exactly where it broke the code.
    """
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    return [
        fcurve
        for layer in action.layers
        for strip in layer.strips
        for channelbag in strip.channelbags
        for fcurve in channelbag.fcurves
    ]


@contextlib.contextmanager
def _pose_restored(armature):
    """Put the armature's pose back exactly as it was found.

    Assigning an action makes Blender write the evaluated values into the pose
    bones themselves, and taking the action away again does not undo that - the
    armature keeps the last frame it was on. Root motion moves a character
    metres from the origin, so a test that animates one and walks away leaves
    every later test measuring that pose instead of the rest one.
    """
    from mathutils import Matrix

    animation_data = armature.animation_data
    previous_action = animation_data and animation_data.action
    previous_pose = {pb.name: pb.matrix_basis.copy() for pb in armature.pose.bones}
    previous_frame = bpy.context.scene.frame_current
    try:
        yield
    finally:
        if armature.animation_data is not None:
            armature.animation_data.action = previous_action
        for pose_bone in armature.pose.bones:
            pose_bone.matrix_basis = previous_pose.get(pose_bone.name, Matrix.Identity(4))
        bpy.context.scene.frame_set(previous_frame)


@pytest.fixture
def mount_vfs_root():
    """Mount VFS roots and take them back out again afterwards.

    The VFS lives in Blender's scene data, which is process-global and outlives
    any one test, while the filesystems behind its roots do not. Node ids are
    `app_id::relative_path` with no scoping per root, so a root left mounted is
    one a later test can resolve a path to and then fail to read - and the
    failure surfaces in that later test, nowhere near the cause.

    Teardown runs whether the test passed or not, which matters most when it
    failed: leaving the roots behind turns one real failure into a cascade of
    unrelated ones. Roots come out in reverse order, and only the ones actually
    mounted, so nothing has to be kept in sync by hand.

    Returns the root_id *string*, not the VirtualFile: a reference taken
    before further file_list.add() calls (any later mount) goes stale and
    silently reads back as "" (see _expand_archive's comment in albam/vfs.py
    and add_fs_root's own re-fetch), which a test would then pass root_id=""
    around without noticing.
    """
    mounted = []

    def mount(app_id, fs_instance, display_name, **kwargs):
        root_vfile = bpy.context.scene.albam.vfs.add_fs_root(
            app_id, fs_instance, display_name=display_name, **kwargs)
        # Not f"{app_id}::{display_name}": _unique_root_name() suffixes that
        # same key with "#1", "#2", ... when a same-named root is already
        # mounted (see its own docstring), and reconstructing the unsuffixed
        # form here would then miss the real root at teardown, leaking it.
        # root_vfile.name is whatever key actually got used.
        root_id = root_vfile.name
        mounted.append(root_id)
        return root_id

    yield mount

    vfs = bpy.context.scene.albam.vfs
    for root_id in reversed(mounted):
        index = vfs.file_list.find(root_id)
        if index == -1:
            continue  # the test removed it itself
        vfs.file_list_selected_index = index
        bpy.ops.albam.remove_imported()


@pytest.fixture
def new_bl_material(request):
    """Factory for materials with one image node linked to Base Color, so
    the export machinery picks the image up. Each call adds a material and
    its image, both named after the test; all are removed afterwards.
    """
    created = []

    def make(app_id, relative_path=""):
        name = f"{request.node.name}_{len(created)}"
        bl_mat = bpy.data.materials.new(name)
        if not bl_mat.node_tree:  # created on demand before Blender 5
            bl_mat.use_nodes = True
        im_node = bl_mat.node_tree.nodes.new("ShaderNodeTexImage")
        bl_im = bpy.data.images.new(name, 4, 4)
        bl_im.albam_asset.app_id = app_id
        bl_im.albam_asset.relative_path = relative_path
        im_node.image = bl_im
        bsdf = bl_mat.node_tree.nodes["Principled BSDF"]
        bl_mat.node_tree.links.new(im_node.outputs["Color"], bsdf.inputs["Base Color"])
        created.append((bl_mat, bl_im))
        return bl_mat, bl_im

    yield make

    for bl_mat, bl_im in created:
        bpy.data.materials.remove(bl_mat)
        bpy.data.images.remove(bl_im)
