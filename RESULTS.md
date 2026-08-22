# mesh.ksy parsing sweep — RE3

Initial pass at exercising `albam/engines/reng/structs/mesh.ksy` (via the
generated `ReengineMesh` parser) against a real, varied sample of RE3
`.mesh` files, to find parsing failures before doing any deeper format
work.

## Dataset

16 files added to `tests/reng/datasets/mesh_parsing_hashes.json` (up from
the pre-existing single entry), picked from the real RE3 install for
category variety rather than random sampling. Only path hashes are
committed (see `tests/mtfw/scripts/catalog_paths.py`); the plaintext paths
below are documentation, not what's stored in the dataset file.

| Label | Category | path_hash |
|---|---|---|
| player_jill | player character | `094caac02ef9c93b` (pre-existing entry) |
| player_carlos | player character | `89712762256d673f` |
| enemy_zombie | enemy character | `c498a87fad0acbcb` |
| enemy_dog | enemy character | `a11076aa6dca2ec7` |
| enemy_nemesis | enemy character (boss) | `755b8857f0bbc46c` |
| enemy_zombie_cutscene_body | enemy character, cutscene-quality variant (`sectionroot`, not `escape`) | `a6c0a468efaf1765` |
| weapon_pistol | weapon | `9e28dab100234404` |
| building_police_terrain | building/stage geometry | `232a628a72324dee` |
| building_police_occ | building occlusion-culling mesh | `ea077b0c68d5007d` |
| building_hospital_terrain | building/stage geometry, different stage | `d9f9825d6b4ecf17` |
| object_tree | natural object prop | `7e9f6f7126f42ebb` |
| object_furniture | artifact/furniture prop | `778af66996774db1` |
| object_item | pickup item prop | `e16f29872f8e5869` |
| object_door_gimmick | interactive gimmick (door) | `19b8f7e49154bf45` |
| vfx_debris | shared engine VFX library mesh | `6d8f58efa06a01c4` |
| vfx_character_bakeanim | per-level VFX mesh | `f2edc64a24e9c582` |

All 16 hashes were verified present in the committed
`tests/reng/datasets/re3_catalog.json` before being added (the dataset's
own `test_dataset_hashes_are_in_catalog` test also asserts this on every
run).

## How to run

```
pytest tests/reng/test_mesh_parsing.py -v \
  --game-dir=re3::/path/to/RE3::tests/data/re3/RE3Z_RT_STM_Release.list
```

(Path list is gitignored `tests/data/`, copy from wherever it's kept
locally.)

## Result: 16 passed, 1 failed

### Failure: `building_police_occ` (`ea077b0c68d5007d`)

```
model = mesh.model_info.model_offsets[0].model
EOFError: requested 4 bytes, but only 0 bytes available
```

**Root cause**: this file's `header.offset_data == 0`. Every other header
offset that can legitimately be absent already has an `if: ... != 0` guard
in the `.ksy` (e.g. `bones_header: {..., if: header.offset_bones != 0}`),
but the `model_info` instance does not:

```yaml
model_info:
    {pos: header.offset_data, type: model_info}
```

With `offset_data == 0`, Kaitai reads `model_info` starting at the very
first byte of the file — i.e. it reinterprets the `MESH` magic and version
fields as `model_info`'s own fields (`len_offsets_models=77` from `'M'`,
`num_materials=69` from `'E'`, etc.), and `num_meshes` comes out as
`21041600` (the file's actual `version` value, read 4 bytes later).
`offset_lod_info` then happens to read as `0`, so `model_offsets[0]` reads
a garbage `u8` "offset" from byte 0 of the file and tries to parse a
`model` there, running off the end of the 10784-byte file.

Inspected fields for this file (`version=21041600`, `size=10784`):

```
offset_data=0, offset_bones=0, offset_unk_2=128,
offset_buffers_header=208, offset_names=208
```

So this occlusion-culling mesh has buffers (vertex/index) and named nodes,
but genuinely no model/mesh-group tree — consistent with it being a
simplified culling proxy rather than a renderable model. This isn't
corruption; it's a real mesh sub-variant the format supports and the
`.ksy`/parser don't yet.

**Fixed**: guarded `model_info` the same way `bones_header` already is
(`if: header.offset_data != 0`), regenerated `reengine_mesh.py`. Accessing
`mesh.model_info` on a buffers-only file now returns `None` instead of
running off the end of the file, matching the existing `bones_header`
pattern. `test_mesh_parsing.py::test_mesh` and `build_blender_model`
(`albam/engines/reng/mesh.py`) both now handle `model_info is None`
explicitly — the Blender importer skips the mesh-group loop and produces
an empty object rather than crashing. Full dataset (17 files) and the rest
of the suite pass.

## Cross-reference against RE-Mesh-Editor

A separate pass cross-referenced this `.ksy`'s many `unk_*`/`test_*`/`TODO`
placeholders against RE-Mesh-Editor (a mature, non-Kaitai RE Engine mesh
importer/exporter at `/home/seba/Repos/_Ext/RE-Mesh-Editor`) to identify
real field names/meanings. Two rounds of fixes followed, each verified
against the full dataset:

**Round 1 - bit-packing bugs.** Several fields were reading 2-4 packed
sub-fields as one wider int, only "working" because the extra sub-fields
happened to be zero in the one sample file the `.ksy` was originally
written against (`file_size`, `model_info.num_meshes`,
`model_info`'s offset+reserved, `model.num_mesh_groups`, `model.unk`
(actually a float LOD-distance), `model.padding` (actually a computed
0-or-8-byte alignment gap, not a fixed size), `mesh.material_id`,
`buffers_header.unk_00_a/unk_00_b`). Also fixed `id_to_names_remap`
(renamed `material_name_remap`): it read `header.num_named_nodes` entries
unconditionally, which is the combined size of three separate name-remap
tables sharing one string table, not just the material one - it only
avoided crashing because the other two tables happen to sit right after
it in the file. Verified every split field reads a small, sane value
(not garbage) and that LOD distances come out as plausible floats, across
the whole 17-file dataset.

**Round 2 - identified all 9 previously-unnamed header offsets** (shadow
mesh, occlusion mesh, normal-recalc, blend shapes, per-bone AABB, unknown
floats, bone/blend-shape name-remaps) and added two new instances:
`bone_name_remap` and `blend_shape_name_remap` (the counterparts to
`material_name_remap`, at their own offsets/counts), plus
`occlusion_mesh_group`.

**This corrects Round 1's characterization of the failing occlusion mesh
(`ea077b0c68d5007d`)**: it does *not* lack real geometry. It has no *main*
model tree (`header.offset_data == 0`), but a distinct
`header.offset_occlusion_mesh_group` points to its own standalone LOD-group
tree - for this file, verified as 1 mesh group / 1 mesh, real geometry.
"Buffers-only, no mesh-group tree" was wrong; "no *main* mesh-group tree,
but a real occlusion-specific one" is correct.

Also verified `material_name_remap`/`bone_name_remap` resolve to real,
sane strings for every file with materials/bones (e.g. `pl0000_Skin_Mat`,
`em1000_Body_Mat`, bone names like `root`/`COG`/`spine_2`/`hips`) - this
wasn't previously checked at all.

`blend_shape_name_remap` is implemented per RE-Mesh-Editor's identified
offset/count formula but **unverified** - every file in the current
dataset has `offset_blend_shape_name_remap == 0`, including a
`pl0001_blend.mesh` file that looked like a plausible candidate by name.
Left as a known gap rather than fabricating verification.

**Not modeled**: `offset_shadow_mesh_group`, `offset_normal_recalc`,
`offset_blend_shapes`, `offset_bone_aabb`, `offset_floats` are identified
(named, commented) but their pointed-to struct layouts aren't - only
partial/uncertain layouts were available even from RE-Mesh-Editor. Left as
bare `u8` offsets rather than guessing.

**`mesh.normals`'s `repeat-expr: 100` FIXME**: resolved conceptually (real
count comes from the *next* sibling submesh's `pos_vertex_buffer`, or
`mesh_group.num_vertices` for a group's last submesh) but **not fixable in
the `.ksy` itself** - Kaitai's Python codegen doesn't correctly support
`_index`/sibling look-ups from a lazily-evaluated instance on a repeated
type (confirmed with a minimal reproduction: it emits a reference to a
loop variable that's out of scope at property-access time, raising
`NameError`). Real code already doesn't depend on this field: it derives
per-submesh vertex count from unique index-buffer values instead
(`albam/engines/reng/mesh.py::build_blender_mesh`). Removed as dead/
unfixable rather than left with a wrong hardcoded value.

**`primitive_accessor.primitive_type`** TODO enum was wrong/incomplete
(guessed 4 values: POSITION/NORMAL/TEXCOORD/JOINT_WEIGHT). Real values (8,
from RE-Mesh-Editor's own enum): `0 position, 1 nor_tan (packed normal+
tangent, not normal alone), 2 uv, 3 uv2 (there are 2 separate UV-channel
types, not one generic TEXCOORD), 4 weight, 5 color, 6 sf6_unknown, 7
extra_weight`. Confirmed against the dataset: every accessor's `size`
(stride) matches the documented byte layout exactly - `position`=12
(3xf32), `nor_tan`=8, `uv`/`uv2`=4, `weight`=16 - across all 16 files that
have them.

**`bone` fields**: `parent_idx` and 4 of its `unk_02` sub-fields
(`sibling_idx`, `child_idx`, `symmetric_idx`, `use_secondary_weight`) are
signed, using `-1` as a "none" sentinel (e.g. root bones have no parent) -
were unsigned, reading as `65535`.

**Naming cleanup**: `model`/`model_offset` types and `model_offsets`
field renamed to `lod_group`/`lod_group_offset`/`lod_group_offsets` (a
"model" in the RE Engine sense is the whole mesh; each of these is one LOD
level). `test_name` renamed to `name_offset`, replacing a dead type of the
same name that was defined but never referenced. `mesh_group_test`
renamed to `mesh_group_offset`.
