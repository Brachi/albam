"""Importing a room: the geometry the level itself is made of.

A room archive holds the props standing in a room as separate mesh .bin
entries, and the room around them as one or two scenario .smd entries. An
.smd is a placement table plus the models it places, each of them a mesh
.bin embedded in the file (see structs/re4-uhd-smd.ksy), so importing one is
mostly a matter of handing every embedded model to the .bin importer with
the transform its entry carries.

That reuse is what this module is: mesh.build_blender_model reads a
VirtualFile and resolves the model's textures through the VFS, and neither
an embedded model nor an embedded .tpl is a file the VFS knows about. Both
are presented to it as objects that answer the handful of questions it
asks - see _EmbeddedFile and _ScenarioContext - rather than by adding
entries to the user's file list, which would reallocate the collection the
import operator is holding a reference into.

Rooms too big for one file are split across several archives, one holding
the models the others share. An entry for a shared model says so and
indexes that file's table instead of its own, which is why importing one
file reaches for a sibling archive (see _SharedScenario).
"""
import math
import os

import bpy
from mathutils import Euler, Matrix, Vector

from ...registry import blender_registry
from ...vfs import VirtualFile
from .mesh import AUTO_TPL, GLOBAL_SCALE, build_blender_model
from .structs.re4_uhd_smd import Re4UhdSmd

# The magic values a scenario ships with. Anything else is not one. 0x0000
# is a stub that places nothing (see structs/re4-uhd-smd.ksy).
SCENARIO_MAGICS = (0x0000, 0x0010, 0x0020, 0x0031, 0x0040, 0x0140)

# What the shared file of a split room is called, relative to one of the
# files sharing it: the extra files are named "<room>_NN" and the shared one
# "<room>", both in the same folder.
SHARED_ARCHIVE_EXTENSION = ".udas.lfs"


@blender_registry.register_import_function(
    app_id="re4uhd", extension="smd", albam_asset_type="MODEL")
def build_blender_scenario(vfile: VirtualFile, context: bpy.types.Context) -> bpy.types.Object:
    scenario_bytes = vfile.get_bytes()
    name = vfile.display_name
    smd = Re4UhdSmd.from_bytes(scenario_bytes)
    smd._read()

    bl_scenario = bpy.data.objects.new(name, None)
    context.collection.objects.link(bl_scenario)

    shared = _SharedScenario(vfile)
    # One model can be placed many times - a room can place 64 models out of
    # 27 - so each is built once and every later placement is an object over
    # the same mesh, the way the game itself instances them.
    built = {}
    placed = 0
    missing = 0
    try:
        for index, entry in enumerate(smd.entries):
            if not entry.is_placed:
                continue
            source = shared.scenario() if entry.is_shared else smd
            source_bytes = shared.data() if entry.is_shared else scenario_bytes
            if source is None:
                missing += 1
                continue
            # A shared model's textures come from the shared file's first
            # .tpl: the entry's own tpl index addresses the table of the file
            # the entry is in, which is not the file the model is in.
            key = (entry.is_shared, entry.model_id, 0 if entry.is_shared else entry.tpl_id)
            bl_mesh = built.get(key)
            if bl_mesh is None:
                bl_mesh = _build_model(
                    source, source_bytes, key[1], key[2],
                    f"{_stem(name)}_{index:03}", vfile, context)
                if bl_mesh is None:
                    missing += 1
                    continue
                built[key] = bl_mesh
            _place(f"{_stem(name)}_{index:03}", bl_mesh, entry, bl_scenario, context)
            placed += 1
    finally:
        shared.close()
    print(f"[re4uhd] scenario {name}: {placed} placed, {len(built)} models, {missing} unresolved")
    return bl_scenario


def _stem(display_name):
    return display_name.rsplit(".", 1)[0]


def _build_model(smd, scenario_bytes, model_id, tpl_id, name, vfile, context):
    """The mesh of one embedded model, built by the .bin importer, or None if
    the scenario has no model under that index.

    Everything the importer needs beyond the bytes - a name, the archive the
    model came from, the .tpl its materials address - comes off the .smd's
    own VirtualFile, so a model imported this way resolves its textures
    through the same archive a prop in the same room does.
    """
    model_offset = _table_offset(smd.offsets_models, smd.header.offset_model_table, model_id)
    if model_offset is None or model_offset >= len(scenario_bytes):
        return None
    model_vfile = _EmbeddedFile(f"{name}.bin", scenario_bytes[model_offset:], vfile)

    tpl_offset = _table_offset(smd.offsets_tpls, smd.header.offset_tpl_table, tpl_id)
    tpl_vfile = None
    if tpl_offset is not None and tpl_offset < len(scenario_bytes):
        tpl_vfile = _EmbeddedFile(f"{name}.tpl", scenario_bytes[tpl_offset:], vfile)

    bl_object = build_blender_model(model_vfile, _ScenarioContext(context, tpl_vfile))
    # The importer returns whatever it parents the mesh to - an empty, or an
    # armature for a model carrying bones. A placed model needs neither: the
    # placement is what parents it, and a room model's bones are one bone at
    # the origin. So the mesh is taken off the object it came under and both
    # that object and its data are dropped.
    bl_mesh = None
    for child in list(bl_object.children):
        bl_mesh = child.data
        bpy.data.objects.remove(child, do_unlink=True)
    _remove_object(bl_object)
    return bl_mesh


def _remove_object(bl_object):
    data = bl_object.data
    bpy.data.objects.remove(bl_object, do_unlink=True)
    if isinstance(data, bpy.types.Armature):
        bpy.data.armatures.remove(data)


def _table_offset(table, table_offset, index):
    """Where one entry of an offset table points, absolute, or None.

    Table entries are relative to the table's own position, and the table is
    zero terminated - so its last entry is the terminator, and an index
    landing on it names no file.
    """
    if index >= len(table) or table[index] == 0:
        return None
    return table_offset + table[index]


def _place(name, bl_mesh, entry, bl_scenario, context):
    """Put one model in the room, under the scenario's own object.

    A placement is a translation, a scale and a rotation, applied in that
    order (see _entry_matrices) - and that order is the one a Blender object
    cannot express: an object scales before it rotates. A uniform scale is
    the same either way, and so is any scale with no rotation to reorder it
    against, and those are placed as one object. The rest are placed as two,
    an empty carrying the position and scale with the model rotated
    underneath it, which is exact rather than the nearest object transform to
    a matrix that isn't one.
    """
    placement, rotation = _entry_matrices(entry)
    bl_object = bpy.data.objects.new(name if rotation is None else f"{name}.000", bl_mesh)
    context.collection.objects.link(bl_object)
    if rotation is None:
        bl_object.parent = bl_scenario
        # matrix_basis, not matrix_local: the two are the same for an object
        # parented without a parent inverse, and this one writes straight
        # into the object's own location, rotation and scale instead of
        # through a matrix the depsgraph caches.
        bl_object.matrix_basis = placement
        return bl_object

    bl_placement = bpy.data.objects.new(name, None)
    context.collection.objects.link(bl_placement)
    bl_placement.parent = bl_scenario
    bl_placement.matrix_basis = placement
    bl_object.parent = bl_placement
    bl_object.matrix_basis = rotation
    return bl_placement


def _entry_matrices(entry):
    """A placement as (position and scale, rotation), in Blender's axes.

    The game rotates a model's raw position by the entry's three angles, X
    then Y then Z, scales the result per axis and adds the entry's position,
    all in its own Y-up millimetre space. The mesh the .bin importer built is
    already in Blender's Z-up metres (see mesh._yz_flip), so the same
    transform is expressed in Blender's axes: a change of basis by 90 degrees
    about X either side of it, which is exactly what that conversion is, and
    a translation converted the same way.

    The rotation comes back separately when it has to be applied after the
    scale and cannot be folded in, and as None when the whole placement is
    one object transform.
    """
    to_blender = Matrix.Rotation(math.radians(90), 4, "X")
    rotation = Euler((entry.angles.x, entry.angles.y, entry.angles.z), "XYZ").to_matrix().to_4x4()
    scale = Matrix.Diagonal(Vector((entry.scale.x, entry.scale.y, entry.scale.z, 1.0)))
    translation = Matrix.Translation(
        to_blender @ Vector((entry.position.x, entry.position.y, entry.position.z)) * GLOBAL_SCALE)
    in_blender = to_blender @ scale @ to_blender.inverted()
    rotation = to_blender @ rotation @ to_blender.inverted()
    if entry.scale.x == entry.scale.y == entry.scale.z or rotation == Matrix.Identity(4):
        return translation @ in_blender @ rotation, None
    return translation @ in_blender, rotation


class _EmbeddedFile:
    """A file inside a scenario, presented the way the .bin importer expects.

    Only the handful of attributes that importer and the texture layer read
    off a VirtualFile: the bytes, a name to build objects and materials
    under, and the archive the scenario itself came from - which is what
    finds the texture packs the model's .tpl names.
    """

    def __init__(self, display_name, data, scenario_vfile):
        self.display_name = display_name
        self.name = display_name
        self._data = data
        self.root_vfile = scenario_vfile.root_vfile
        self.tree_node = scenario_vfile.tree_node

    def get_bytes(self):
        return self._data


class _ScenarioContext:
    """The import context, with one .tpl in place of the whole VFS.

    A scenario says outright which of its own .tpl files each model uses, so
    the search mesh.choose_tpl does over an archive has nothing to work out
    here - but the .bin importer always runs it. Giving it a file list
    holding exactly the right .tpl is what makes it come back with that one,
    without touching the user's real VFS.
    """

    def __init__(self, context, tpl_vfile):
        self._context = context
        self.scene = _ScenarioScene(context.scene, tpl_vfile)

    def __getattr__(self, name):
        return getattr(self._context, name)


class _ScenarioScene:
    def __init__(self, scene, tpl_vfile):
        self._scene = scene
        self.albam = _ScenarioAlbamData(tpl_vfile)

    def __getattr__(self, name):
        return getattr(self._scene, name)


class _ScenarioAlbamData:
    def __init__(self, tpl_vfile):
        self.vfs = _ScenarioVfs(tpl_vfile)
        self.import_options_bin = _ScenarioImportOptions()


class _ScenarioVfs:
    def __init__(self, tpl_vfile):
        self.file_list = [tpl_vfile] if tpl_vfile is not None else []


class _ScenarioImportOptions:
    tpl_file_id = AUTO_TPL
    shared_armature = None


class _SharedScenario:
    """The scenario holding the models a split room's files share.

    An entry can place a model that is not in its own file: a room split
    into several archives keeps the models they have in common in one of
    them, and the others index that file's table. The file is found the only
    way it can be - next to the archive being imported, under the room's own
    name - and is mounted on first use, since reading it means decompressing
    a whole archive and most scenarios never ask for one.
    """

    def __init__(self, scenario_vfile):
        root = scenario_vfile.root_vfile
        self._archive_path = root.absolute_path if root else ""
        self._fs = None
        self._scenario = None
        self._data = None
        self._resolved = False

    def scenario(self):
        self._resolve()
        return self._scenario

    def data(self):
        self._resolve()
        return self._data

    def close(self):
        if self._fs is not None:
            self._fs.close()
            self._fs = None

    def _resolve(self):
        if self._resolved:
            return
        self._resolved = True
        path = _shared_archive_path(self._archive_path)
        if path is None:
            return
        from .fs import LfsFS

        print(f"[re4uhd] scenario: reading shared models from {os.path.basename(path)}")
        try:
            self._fs = LfsFS(path)
        except Exception as err:  # a sibling that isn't readable is not fatal
            print(f"[re4uhd] scenario: {os.path.basename(path)} not readable: {err}")
            return
        # The archive can hold more than one scenario, and the shared models
        # are in whichever of them carries the most - the others place a
        # handful of their own.
        best = None
        for entry_path in self._fs.walk.files():
            if not entry_path.lower().endswith(".smd"):
                continue
            data = self._fs.readbytes(entry_path)
            try:
                smd = Re4UhdSmd.from_bytes(data)
                smd._read()
            except Exception:
                continue
            if smd.header.magic not in SCENARIO_MAGICS:
                continue
            if best is None or len(smd.offsets_models) > len(best[0].offsets_models):
                best = (smd, data)
        if best is not None:
            self._scenario, self._data = best


def _shared_archive_path(archive_path):
    """The archive holding a split room's shared models, or None.

    The files of a split room are named after the room with a number
    appended, and the archive they share is the one with no number, in the
    same folder. A file that is not part of a split room finds nothing here,
    which is the answer: its models are all its own.
    """
    if not archive_path:
        return None
    directory, file_name = os.path.split(archive_path)
    stem = file_name.split(".")[0]
    base, separator, suffix = stem.rpartition("_")
    if not separator or not suffix.isdigit():
        return None
    wanted = (base + SHARED_ARCHIVE_EXTENSION).lower()
    try:
        names = os.listdir(directory)
    except OSError:
        return None
    for name in names:
        if name.lower() == wanted:
            return os.path.join(directory, name)
    return None
