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
import hashlib
import math
import os
import struct

import bpy
from mathutils import Euler, Matrix, Vector

from ...exceptions import AlbamCheckFailure
from ...registry import blender_registry
from ...vfs import VirtualFile, VirtualFileData
from .mesh import (AUTO_TPL, GLOBAL_SCALE, VERTEX_COLOR_ATTRIBUTE, build_blender_model,
                   export_room_model)
from .structs.re4_uhd_smd import Re4UhdSmd

# The magic values a scenario ships with. Anything else is not one. 0x0000
# is a stub that places nothing (see structs/re4-uhd-smd.ksy).
SCENARIO_MAGICS = (0x0000, 0x0010, 0x0020, 0x0031, 0x0040, 0x0140)

# The custom property a placement's top-level object carries: the index of
# the .smd entry it was imported from, which is what export writes it back
# into (see export_smd).
ENTRY_PROPERTY = "albam_smd_entry"

# Where the entry table starts, and how big one entry is - for every magic
# but 0x140, whose header carries a variable list of counts first (see
# structs/re4-uhd-smd.ksy). An entry is three vec3f, four u1, seven u4 and
# a u4 status.
SMD_HEADER_SIZE = 16
SMD_ENTRY_SIZE = 72
# Within an entry: position, angles and scale, three f4 each.
ENTRY_TRANSFORM_FORMAT = "<9f"
# A placement is written back only if it moved by more than this, in
# Blender's units (metres and radians); anything less is float noise from
# the round trip through a matrix, and the entry keeps its shipped bytes.
TRANSFORM_TOLERANCE = 1e-5
# How far, relative to the placement's own size, the transform an entry can
# express may land from the one in Blender before export refuses it (see
# _matrix_to_entry).
EXPRESSIBLE_TOLERANCE = 1e-4
# The custom property on a room's object listing the entries import made an
# object for - the only ones export may treat as deleted when no object
# claims them (see export_smd).
IMPORTED_ENTRIES_PROPERTY = "albam_smd_imported_entries"

# The custom properties a room model's mesh carries: which entry of the
# .smd's model table it was built from, and a fingerprint of what export
# writes from it as it was imported (see _mesh_fingerprint), which is what
# tells an edited model from one left alone.
MODEL_PROPERTY = "albam_smd_model"
FINGERPRINT_PROPERTY = "albam_smd_fingerprint"
# Embedded models start on this boundary in shipped files.
SMD_MODEL_ALIGNMENT = 32

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
    imported = []
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
                if not entry.is_shared:
                    bl_mesh[MODEL_PROPERTY] = entry.model_id
                    bl_mesh[FINGERPRINT_PROPERTY] = _mesh_fingerprint(bl_mesh)
                built[key] = bl_mesh
            bl_placement = _place(f"{_stem(name)}_{index:03}", bl_mesh, entry, bl_scenario, context)
            bl_placement[ENTRY_PROPERTY] = index
            imported.append(index)
            placed += 1
    finally:
        shared.close()
    bl_scenario[IMPORTED_ENTRIES_PROPERTY] = imported
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

    try:
        bl_object = build_blender_model(model_vfile, _ScenarioContext(context, tpl_vfile))
    except AlbamCheckFailure:
        # A room places hundreds of models. One the .bin importer refuses -
        # an offset landing on something that is not a model - counts as
        # unresolved, like a model index the tables have no entry for, rather
        # than taking the whole room down with it.
        return None
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
    # The rotation-vs-identity comparison below is exact rather than
    # tolerant, which issue #271 lists as a latent defect worth checking.
    # Tried and not reproduced: zero angles, angles that are whole multiples
    # of 2*pi and very small angles all classify correctly through the change
    # of basis. Getting it wrong would only ever cost an extra placement
    # Empty, never wrong geometry, so the comparison is left as it is.
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


@blender_registry.register_export_function(app_id="re4uhd", extension="smd")
def export_smd(bl_obj):
    """The .smd a room was imported from, with its placements as they are in
    Blender now.

    Only the entry table is rewritten, and only the entries whose placement
    changed. A scenario holds far more than this module reads - between the
    entry table and the models sit megabytes nothing here models - so the
    shipped file is the starting point and everything else in it is kept
    byte for byte.

    A placement moved, rotated or scaled in Blender is written back to its
    entry. One deleted in Blender is zeroed, which is what the unused
    entries a few rooms ship with look like and is what the game skips -
    but only an entry import made an object for: one whose model could not
    be built (a split room's shared models when the shared archive is not
    beside it, a model the .bin importer refused) never had an object to
    delete, and is kept as it is. A room imported before that was recorded
    has nothing deleted.

    A model whose mesh was edited is written again (see _write_models);
    every other model keeps its shipped bytes.
    """
    asset = bl_obj.albam_asset
    data = bytearray(asset.original_bytes)
    smd = Re4UhdSmd.from_bytes(bytes(data))
    smd._read()
    if smd.header.magic == 0x140:
        raise AlbamCheckFailure(
            f"{bl_obj.name} is a room assembled from several files, which albam "
            f"can't write back yet",
            details="Its header carries a list of per-file entry counts that "
                    "export does not maintain. One room of the game is like this.",
        )

    placements = {}
    for child in bl_obj.children:
        index = child.get(ENTRY_PROPERTY)
        if index is None:
            continue
        if index in placements or not 0 <= index < len(smd.entries):
            raise AlbamCheckFailure(
                f"{child.name} claims entry {index} of {bl_obj.name}, which "
                f"{'another object also claims' if index in placements else 'has no such entry'}",
                details="Each object placed in a room stands for one entry of its "
                        ".smd, recorded on import. A duplicate made in Blender "
                        "copies that record but has no entry of its own: adding "
                        "placements isn't supported yet.",
                solution="Delete the duplicate, or move the original instead",
            )
        placements[index] = child

    imported = bl_obj.get(IMPORTED_ENTRIES_PROPERTY)
    imported = set(imported) if imported is not None else set(placements)

    changed = 0
    for index, entry in enumerate(smd.entries):
        if not entry.is_placed or index not in imported:
            continue
        offset = SMD_HEADER_SIZE + index * SMD_ENTRY_SIZE
        # The entry is patched where it sits rather than written out from the
        # parsed fields, so the offset is checked against what the parser
        # read there before anything is written to it.
        position = (entry.position.x, entry.position.y, entry.position.z)
        if struct.unpack_from("<3f", data, offset) != position:
            raise RuntimeError(f"entry {index} of {bl_obj.name} is not at offset {offset}")
        bl_placement = placements.get(index)
        if bl_placement is None or not _has_mesh(bl_placement):
            # Deleting only the mesh under a two-object placement deletes
            # the placement too: the empty left behind places nothing.
            data[offset:offset + SMD_ENTRY_SIZE] = bytes(SMD_ENTRY_SIZE)
            changed += 1
            continue
        matrix = _placement_matrix(bl_placement)
        if _same_matrix(matrix, _entry_matrix(entry)):
            continue
        struct.pack_into(ENTRY_TRANSFORM_FORMAT, data, offset,
                         *_matrix_to_entry(matrix, bl_placement.name))
        changed += 1

    models = _write_models(bl_obj, data, smd, placements.values())
    print(f"[re4uhd] scenario {bl_obj.name}: {changed} entries rewritten, "
          f"{models} models rewritten")
    return [VirtualFileData(asset.app_id, asset.relative_path, data_bytes=bytes(data))]


def _entry_matrix(entry):
    """The whole transform an entry places its model at, in Blender's axes."""
    placement, rotation = _entry_matrices(entry)
    return placement if rotation is None else placement @ rotation


def _has_mesh(bl_placement):
    return bl_placement.type == "MESH" or any(c.type == "MESH" for c in bl_placement.children)


def _placement_matrix(bl_placement):
    """The transform a placement puts its model at, relative to the room.

    A placement is one object, or an empty with the rotated model under it
    (see _place); either way it is the product of the matrices from the
    room's object down to the mesh.
    """
    matrix = bl_placement.matrix_basis.copy()
    meshes = [c for c in bl_placement.children if c.type == "MESH"]
    if bl_placement.type != "MESH" and meshes:
        matrix = matrix @ meshes[0].matrix_basis
    return matrix


def _same_matrix(a, b):
    return all(abs(a[i][j] - b[i][j]) <= TRANSFORM_TOLERANCE
               for i in range(4) for j in range(4))


def _matrix_to_entry(matrix, name="A room placement"):
    """(position, angles, scale) for an entry placing its model at `matrix`,
    nine floats in the order the entry stores them - the inverse of
    _entry_matrices.

    Back in the game's axes the linear part is the scale times the rotation,
    each row of the rotation scaled by one axis (see _entry_matrices), so a
    row's length is that axis's scale and dividing it out leaves the
    rotation. A mirrored placement carries its reflection on X.

    Done in double precision: mathutils works in single, and taking the
    angles through it lost up to a centimetre on a large prop turned close
    to 90 degrees about Y.

    Not every transform is one an entry can hold. An entry scales after it
    rotates, a Blender object before - so an object turned and then
    stretched along its own axis is a shear in the game's terms, and the
    nearest entry puts its model somewhere else. That is refused rather than
    written: the placement is recomposed from the entry and compared with
    the one in Blender.
    """
    import numpy as np

    to_blender = np.array(Matrix.Rotation(math.radians(90), 4, "X"), dtype=np.float64)
    blender = np.array(matrix, dtype=np.float64)
    in_game = np.linalg.inv(to_blender) @ blender @ to_blender
    position = in_game[:3, 3] / GLOBAL_SCALE
    linear = in_game[:3, :3]
    scale = np.linalg.norm(linear, axis=1)
    if np.linalg.det(linear) < 0:
        scale[0] = -scale[0]
    if np.any(np.abs(scale) < 1e-12):
        raise AlbamCheckFailure(
            f"{name} is scaled to nothing on one axis",
            details="An entry with a zero scale is what the game treats as unused",
            solution="Give the object a non-zero scale, or delete it",
        )
    # The nearest rotation to what is left once the scale is divided out,
    # which is that rotation itself whenever an entry can express the whole.
    u, _, vt = np.linalg.svd(linear / scale[:, None])
    rotation = u @ vt
    angles = _euler_xyz(rotation)

    recomposed = _game_matrix(position * GLOBAL_SCALE, angles, scale)
    size = max(1.0, float(np.abs(scale).max()))
    error = float(np.abs(recomposed - in_game).max())
    if error > EXPRESSIBLE_TOLERANCE * size:
        raise AlbamCheckFailure(
            f"{name} is transformed in a way a room entry can't hold",
            details="An entry stretches its model after rotating it, along the "
                    "room's axes, while a Blender object stretches before "
                    "rotating. A placement both rotated and scaled unevenly along "
                    f"its own axes would land up to {error:.3g} m off.",
            solution="Rotate the mesh under an empty and scale the empty instead "
                     "(the way import builds such placements), or scale evenly",
        )
    return (*position, *angles, *scale)


def _euler_xyz(rotation):
    """Angles (x, y, z) such that Euler((x, y, z), "XYZ").to_matrix() is
    `rotation` - X applied first, so the matrix is Rz @ Ry @ Rx."""
    sin_y = -rotation[2, 0]
    cos_y = math.hypot(rotation[2, 1], rotation[2, 2])
    y = math.atan2(sin_y, cos_y)
    if cos_y > 1e-9:
        x = math.atan2(rotation[2, 1], rotation[2, 2])
        z = math.atan2(rotation[1, 0], rotation[0, 0])
    else:
        # Gimbal lock: only x - z (or x + z) is defined; z is taken as 0.
        z = 0.0
        x = math.atan2(rotation[0, 1] if sin_y > 0 else -rotation[0, 1], rotation[1, 1])
    return x, y, z


def _game_matrix(translation, angles, scale):
    """translation @ scale @ rotation in the game's axes, double precision -
    the transform an entry holds, as _entry_matrices builds it."""
    import numpy as np

    x, y, z = angles
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    out = np.identity(4)
    out[:3, :3] = np.diag(scale) @ (rz @ ry @ rx)
    out[:3, 3] = translation
    return out


def _mesh_fingerprint(bl_mesh):
    """A digest of everything a room model is written from: positions,
    faces, UVs, normals, vertex colours, which material each face uses and
    which image each material binds. Recorded at import and compared at
    export - a model is only written again if this changed, since a model
    written from Blender is not byte for byte what shipped even unedited."""
    import numpy as np

    digest = hashlib.sha1()

    def add(collection, attribute, count, dtype):
        values = np.empty(count, dtype=dtype)
        collection.foreach_get(attribute, values)
        digest.update(values.tobytes())

    add(bl_mesh.vertices, "co", len(bl_mesh.vertices) * 3, np.float32)
    add(bl_mesh.loops, "vertex_index", len(bl_mesh.loops), np.int32)
    add(bl_mesh.polygons, "loop_total", len(bl_mesh.polygons), np.int32)
    add(bl_mesh.polygons, "material_index", len(bl_mesh.polygons), np.int32)
    add(bl_mesh.corner_normals, "vector", len(bl_mesh.corner_normals) * 3, np.float32)
    uv_layer = bl_mesh.uv_layers.active
    if uv_layer is not None:
        add(uv_layer.data, "uv", len(uv_layer.data) * 2, np.float32)
    colors = bl_mesh.color_attributes.get(VERTEX_COLOR_ATTRIBUTE)
    if colors is not None:
        add(colors.data, "color_srgb", len(colors.data) * 4, np.float32)
    for bl_material in bl_mesh.materials:
        digest.update(b"\0" + (bl_material.name.encode() if bl_material else b""))
        if bl_material is None or not bl_material.node_tree:
            continue
        # Which image feeds which shader input is what a material's texture
        # slots are written from (see mesh._texture_slot).
        for link in bl_material.node_tree.links:
            image = getattr(link.from_node, "image", None)
            if image is not None:
                digest.update(f"\1{image.name}\2{link.to_socket.name}".encode())
    return digest.hexdigest()


def _write_models(bl_obj, data, smd, bl_placements):
    """Write every edited room model back into `data`, the .smd being
    exported, and return how many were.

    A model that still fits the space it had - up to the next thing the file
    is known to hold - is written where it was. If one does not, the region
    the models and .tpl files fill is laid out again: every one of them in
    the order they were, on the alignment they shipped with, unedited ones
    copied as they are, and both offset tables pointed at the new places.
    That only depends on the tables being the only thing pointing into that
    region, which is what the game showed when every model of a room was
    moved to the end of its file and it drew the moved copies. Where the
    region is not made of models and .tpl files alone, the model is appended
    at the end instead and the old bytes are left where they were.
    """
    meshes = _edited_models(bl_obj, bl_placements)
    if not meshes:
        return 0

    model_table = smd.header.offset_model_table
    tpl_table = smd.header.offset_tpl_table
    # (absolute start, table position of its offset, which table it is in).
    items = [(model_table + o, model_table + 4 * i, model_table)
             for i, o in enumerate(smd.offsets_models[:-1])]
    items += [(tpl_table + o, tpl_table + 4 * i, tpl_table)
              for i, o in enumerate(smd.offsets_tpls[:-1])]
    starts = sorted({start for start, _, _ in items})
    known = sorted(set(starts) | {model_table, tpl_table, len(data)})

    def slot(start):
        return start, min(k for k in known if k > start)

    rewritten = {}
    for model_id, bl_mesh in sorted(meshes.items()):
        start, end = slot(model_table + smd.offsets_models[model_id])
        rewritten[start] = export_room_model(bl_mesh, bytes(data[start:end]))

    if all(len(new) <= slot(start)[1] - start for start, new in rewritten.items()):
        for start, new in rewritten.items():
            end = slot(start)[1]
            data[start:end] = new + bytes(end - start - len(new))
        return len(meshes)

    region_start = starts[0]
    if any(region_start <= table < len(data) for table in (model_table, tpl_table)):
        # A table sits among the models: the region is not models and .tpl
        # files alone, so it is not laid out again.
        for start, new in rewritten.items():
            end = slot(start)[1]
            if len(new) <= end - start:
                data[start:end] = new + bytes(end - start - len(new))
                continue
            data.extend(bytes(-len(data) % SMD_MODEL_ALIGNMENT))
            for item_start, offset_position, table in items:
                if item_start == start:
                    struct.pack_into("<I", data, offset_position, len(data) - table)
            data.extend(new)
        return len(meshes)

    region = bytearray()
    moved = {}
    for start in starts:
        region.extend(bytes(-(region_start + len(region)) % SMD_MODEL_ALIGNMENT))
        moved[start] = region_start + len(region)
        end = slot(start)[1]
        region.extend(rewritten.get(start, data[start:end]))
    del data[region_start:]
    data.extend(region)
    for start, offset_position, table in items:
        struct.pack_into("<I", data, offset_position, moved[start] - table)
    if smd.header.offset_first_model in moved:
        # Only a hint (see structs/re4-uhd-smd.ksy), kept consistent anyway.
        struct.pack_into("<I", data, 12, moved[smd.header.offset_first_model])
    return len(meshes)


def _edited_models(bl_obj, bl_placements):
    """{model id: mesh} for every room model whose mesh no longer matches
    the fingerprint import recorded."""
    meshes = {}
    for bl_placement in bl_placements:
        for bl_object in [bl_placement] + list(bl_placement.children):
            if bl_object.type != "MESH" or MODEL_PROPERTY not in bl_object.data:
                continue
            bl_mesh = bl_object.data
            if bl_mesh.get(FINGERPRINT_PROPERTY) == _mesh_fingerprint(bl_mesh):
                continue
            model_id = bl_mesh[MODEL_PROPERTY]
            other = meshes.setdefault(model_id, bl_mesh)
            if other != bl_mesh:
                raise AlbamCheckFailure(
                    f"Model {model_id} of {bl_obj.name} was edited as two different "
                    f"meshes, {other.name} and {bl_mesh.name}",
                    details="The room stores the model once, so only one version of "
                            "it can be written. Import makes a second mesh for a "
                            "model textured through a different .tpl.",
                    solution="Make the edit on one of them only",
                )
    return meshes
