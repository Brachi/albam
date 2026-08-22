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

# mdf.ksy parsing sweep — RE3

Same exercise as above, for `albam/engines/reng/structs/mdf.ksy` (RE
Engine's `.mdf2` material-info format - each `.mesh` file has a sibling
`.mdf2` referenced by heuristic filename match, see
`albam/engines/reng/material.py`).

## Dataset

13 files in `tests/reng/datasets/mdf_parsing_hashes.json`, each the real
sibling `.mdf2` of one file already in the mesh-parsing/import datasets -
same category variety (player/enemy/boss characters, weapon, 2 building
materials, natural object, furniture, item, gimmick, VFX-library debris),
all hash-verified against the committed catalog.

## Result: 13/13 passed

No parsing failures, unlike the `.mesh` sweep. Beyond the basic structural
assertions (`test_mdf_parsing.py`), spot-checked actual decoded values
across the whole dataset (material names, texture types/paths, property
names/counts) - all sane and self-consistent with each file's real-world
content: e.g. `em1000_Body_Mat` with `BaseMetalMap`/`NormalRoughnessMap`/
`EmissiveMap` textures and `BaseColor`/`Metallic`/`Roughness` properties;
`em3000`'s (an in-game "Licker") materials named `mat_body`/`mat_skin`/
`mat_back` referencing `licker_*_ALBM.tex`/`licker_*_NRMR.tex`; the police
station terrain material (29 sub-materials) including a
`shading=1` outlier (`st2_AreaBlood02`, a blood-decal material) among an
otherwise uniform `shading=0` set - real category variation, not noise.

## Cross-reference against RE-Mesh-Editor

A cross-reference pass (same methodology as the `.mesh` investigation
above) found real bugs despite this initial pass having found no parsing
failures - a clean parse doesn't mean every field is actually understood.
Verified against the dataset and fixed:

- **`alpha_flags` bit order was backwards** - Kaitai defaults to MSB-first
  bit consumption; the real struct this mirrors (RE-Mesh-Editor's ctypes
  `MDFFlags_bits`) is LSB-first, verified empirically by running the real
  ctypes struct and a minimal Kaitai repro of both bit orders side by
  side. Every flag except `no_ray_tracing` was reading the wrong physical
  bit. Fixed with `bit-endian: le`. Also fixed `phong_factor`, declared as
  a 1-bit flag ("## empty?") when it's really a full 0-255 value -
  correcting its size also accounts for a trailing `unk_01` that never
  existed once `phong_factor` is sized right (10+6+8+8 = 32 bits exactly).
  Verified post-fix: `base_alpha_test_enable` is now the flag that
  differs between a same-shape `"_AlphaTest"`- vs `"_Default"`-suffixed
  material pair - exactly matching their names. Pre-fix, the wrong bit
  (`base_two_side_enable`) happened to correlate instead, since
  alpha-tested foliage in this game is typically also double-sided - a
  coincidence that made the bug easy to miss by spot-checking alone.
- **Silent bug for RE8**: `properties_headers`' version switch
  (exact-match `cases: {10, 13, 21}`, no default) produced an empty
  properties list for any unmatched `mdf_version` - including `19`,
  RE8's own `.mdf2` version per `apps.py`. Kaitai's `switch-on` silently
  empties the array on an unmatched case rather than erroring, so this
  had no visible symptom before. There are only ever two real property-
  header layouts (`>=13` or `<13`), not a per-version list - switched to
  a boolean condition.
- **Packed-field bugs**, same pattern as `.mesh`: root `unk_02`/`unk_03`
  merged into one real `u8` `material_flags` (mostly 0; RE-Mesh-Editor
  only ever sets it, to 1, for MHWILDS); `material`'s `unk_01` (`>=19`)
  split into its 2 real packed `u4` counts (`num_gpbf_buffer_names`/
  `paths`); `properties_header_13`'s `num_params` (`u4`) split into
  `num_params`(`u2`) + an unexplained `unk_flag`(`u2`) - currently
  harmless only because `unk_flag` is 0 in every sampled file.
- **`ofs_first_material_name` (`>=19`) was misnamed** - unrelated to
  material names. It's an offset to a "GPBF" name/path table (paired with
  the counts above); "GPBF" is unexplained upstream too. Renamed to
  `ofs_gpbf_buffer` - confirmed dead code in albam either way (never read
  anywhere).
- **Not changed**: `material_shading_type` has a real enum available
  upstream, but RE-Mesh-Editor's own comment flags its values as sourced
  from one specific game version and possibly wrong on others - not
  modeled here to avoid asserting false confidence across RE2/RE3/RE8.
  `properties_header`'s `params` is confirmed to always be a flat,
  untyped `f4` array at the binary level in both tools; per-property
  typed interpretation (color vs. scalar) happens entirely out-of-band,
  by name-string lookup, appropriately out of scope for the format
  itself. `texture_header`'s `unk_01` (`>=13`) is genuinely still unknown
  in both tools - confirmed same size/gate, no further identity found.

# tex.ksy parsing/serialization sweep — RE3

Same methodology as the two sweeps above, for `albam/engines/reng/structs/tex.ksy`
(RE Engine's `.tex` texture format - a material's texture bindings, in
`.mdf2`, point to `.tex` files; see `albam/engines/reng/texture.py`).

## Dataset and test

14 files in `tests/reng/datasets/tex_serialization_hashes.json` (player/
enemy/boss characters, weapon, building/environment, and prop textures),
all hash-verified against the committed catalog. Unlike the mesh/mdf
sweeps, this one is a **byte-exact round-trip** test
(`test_tex_serialization.py`), not just structural parsing assertions:
read a real file, re-serialize it with the same `.ksy`-generated
read-write parser into a freshly allocated buffer, and assert the output
matches the source bytes exactly. This is deliberately stricter than a
plain parse - it fails if `.ksy` doesn't account for every byte of the
real file (a gap/padding region nothing writes to), independent of
manually reading the format. Result: **14/14 passed**, both before and
after every fix below - `.tex`'s declared fields already fully account
for every byte in this sample.

## Cross-reference against RE-Mesh-Editor

Same "wide field is secretly packed narrow fields" pattern the mesh.ksy/
mdf.ksy passes found repeatedly:

- `mipmap_data`'s `ofs_data`/`unk_01` (2× `u4`) merged into one real `u8`
  offset - harmless today only because no real file is anywhere near
  4GB, so the high 32 bits were always 0.
- `unk_04` (`u4`) split into its 2 real `u1` sub-fields + a null `u2`;
  `unk_05` (`u8`, version-gated) split into its 5 real sub-fields
  (swizzle metadata, unused on PC, + two upstream-unexplained "seven"/
  "one" markers). Both still unnamed/unexplained upstream too - split
  for byte-accuracy, not because their meaning is now known.

**Version thresholds generalized**: the mipmap-header layout choice and
`unk_05`'s presence were both hardcoded as literal version-number lists
(`10`/`190820018` → layout A, `30`/`34` → layout B; a separate exact-match
gate for `unk_05`). The real underlying conditions are `version > 11 and
version != 190820018` (mipmap header) and `version > 27 and version !=
190820018` (`unk_05`) - two genuinely independent thresholds, confirmed
upstream, not the same condition reused. Every version albam currently
supports resolves identically either way - this only matters for
correctly extrapolating to a future version instead of guessing which
literal list it belongs in.

**Identified and renamed**: `unk_00` → `depth` (3D/volume-texture depth -
mip level *N*'s depth is `max(depth >> N, 1)`); root `unk_02`/`unk_03` →
`swizzle_control` (now correctly signed - `-1` = no swizzle, which is
every case albam handles, PC only) / `cubemap_marker`; `mipmap_data`'s
`unk_02` → `scanline_length` (row pitch in bytes, used upstream to strip
per-row padding - **not** a per-mip width/height as first hypothesized
when briefing the investigation).

**`format` enum added** (`dxgi_format` - RE Engine's values are confirmed
1:1 with the real, standard DXGI_FORMAT enum). Checked against real data
before assuming this mattered: `texture.py` only special-cases 4 raw
values today (`98`/`99`→BC7, `71`/`72`→DXT1, else a warn-and-guess-BC7
fallback), and the initial concern was that `NormalRoughnessMap` textures
(BC5 is the industry-standard normal-map compression) might be silently
misdecoding. Verified directly: every texture across the whole dataset,
including all `_NRMR`/`NormalRoughnessMap` ones, is actually `format=98`
(BC7) or `format=72` (BC1/DXT1 `srgb`) - values `texture.py` already
handles correctly. So the enum is documentation/future-proofing, not a
fix for an observed live bug in this game.

**Not modeled** (out of scope - no supported version or sample file
exercises either): per-image mip-chain looping for cubemap/texture-array
files (`num_images` is real and distinct from `depth`, but albam's `.ksy`
only ever reads one image's mip chain regardless of its value - harmless
for every ordinary single-image texture, which is everything tested, but
an incomplete model for a real cubemap/array file); the newest titles'
(MHWilds/RE9/MHS3) GDeflate-compressed mip-payload section, which doesn't
exist at all for any version albam currently supports.

Verified via the round-trip serialization test (still 14/14 after every
change) and the full suite, including the mesh-import test (exercises
the real image-decode pipeline end-to-end).

# .mesh export (geometry only)

RE Engine had no export at all until now - `albam/engines/reng/mesh.py`'s
`export_reengine_mesh` (registered for re2/re3, `mesh.2109108288`) adds
geometry export, following MTFW's established architecture
(`register_export_function` -> the existing generic `export()` operator,
no new UI code). Scope, deliberately: `.mesh` geometry only - `.mdf2`
(material) and `.tex` (texture) export are not implemented; an exported
mesh still correctly references its existing materials by name, it just
never regenerates the `.mdf2` itself.

**Mechanism (reworked from an earlier raw-byte-patching version - see git
history)**: parses the original file into a real `ReengineMesh`, calls
`_fetch_instances()` once immediately (same reason `.tex`'s serialization
test needed it - `_write()` reassigns `_io` to the destination stream
before its own internal `_fetch_instances()` call would otherwise lazily
read a not-yet-touched instance from a source stream that's already
gone), mutates vertex/index buffer bytes and each submesh's
`material_index`/`is_quad`/`vertex_buffer_index` directly on that live
object graph, then lets Kaitai's real `_write()` serialize everything -
the same idiom MTFW's own `.mod` export already uses. This is a genuine
mechanical change, not cosmetic: every submesh field this doesn't
explicitly set (`num_indices`, `pos_index_buffer`, `pos_vertex_buffer`,
`unk_01`, ...) is simply whatever `_read()` already put there, with no
hand-maintained shadow model of the file's byte layout computing
absolute offsets (the previous version's `_mesh_entry_offsets`, deleted).

**Confronting what mesh.ksy doesn't model, instead of routing around it**:
before writing any Blender-facing code, diffed a real file against
itself through an unmodified `_read()`/`_write()` round trip (script,
not committed - the technique matches `test_tex_serialization.py`'s). Two
kinds of gap turned up, and both got resolved differently on purpose:

- `bone_header.offset_matrix_1`/`offset_matrix_2` (bone local/world
  transform matrices) were bare `u8` offsets with **no instance reading
  the data they point to at all** - a `_write()` left both regions
  zeroed, since nothing in the object graph had ever read them. Diffing
  confirmed the exact byte range of each mismatch fell precisely within
  `[offset_matrix_N, offset_matrix_N + num_bones*64)`, with plausible
  4x4-matrix float content (diagonal `1.0`s at 20-byte strides) - i.e.
  this was fully, confidently modelable with the `matrix4x4` type
  `inverse_bind_matrices` already uses. **Modeled** (`mesh.ksy`'s
  `bone_header.local_matrices`/`world_matrices`, new) - this is now a
  real fix, not a per-export patch, and closed the large majority of the
  observed gap for every skinned file tested.
- `header.offset_bone_aabb` (per-bone bounding box array) and, on one
  file, `header.offset_shadow_mesh_group` (an entire separate shadow-
  casting LOD/mesh-group tree) are the same kind of gap, but **not**
  confidently modelable in this pass: `offset_bone_aabb`'s region doesn't
  divide evenly by `num_bones` at any stride tried, so its real per-bone
  entry layout isn't nailed down (RESULTS.md's mesh.ksy section already
  flagged this as one of the offsets RE-Mesh-Editor itself only had
  partial/uncertain layouts for), and `offset_shadow_mesh_group` is a
  whole parallel tree structure, a materially bigger undertaking than a
  flat array. Rather than guess at a layout or let a real geometry-only
  export silently zero out real per-bone-AABB/shadow-mesh data, export's
  `_restore_unmodeled_regions` copies these specific, still-unmodeled
  byte ranges back from the source file after `_write()` - not
  reconstructed through the real mechanism, openly not, but not
  destroyed either. This list is generic (keyed off the actual header
  offset values, not per-file hardcoded) and already covers the other
  two currently-unmodeled offsets (`offset_normal_recalc`,
  `offset_blend_shapes`) in case a future dataset file has them nonzero.

**Custom properties, not an ad-hoc mesh attribute, for values that fit
that mechanism**: `is_quad`/`vertex_buffer_index` (per-submesh, real,
independently meaningful, small) are now a real
`ReengineSubMeshCustomProperties` (`register_custom_properties_mesh`),
following the exact pattern MTFW's own per-format custom properties use
(e.g. `Mod156MeshCustomProperties`) - populated from the parsed struct on
import, read back on export, visible/editable in Blender's UI like every
other albam custom property, not just internal round-trip plumbing.
`copy_custom_properties_to/from` work generically against the real
Kaitai `mesh` object with no per-field mapping code, because the
PropertyGroup's own attribute names were chosen to match Kaitai's. The
raw `nor_tan` bytes stay a plain Blender mesh attribute
(`NOR_TAN_LO_ATTR`/`NOR_TAN_HI_ATTR`) rather than being forced into this
system - it's genuinely per-vertex data, and albam's custom-properties
mechanism is a one-PropertyGroup-per-datablock model with no per-vertex
analogue anywhere else in the codebase (checked MTFW's usage before
concluding this); a real mesh attribute is the correct tool for that
shape of data, not a workaround.

**Fidelity results** (5-file dataset spanning a skinned character, a
skinned weapon, a skinned 8-LOD-group enemy, and two bone-less static
meshes - see `tests/reng/test_mesh_serialization.py`):

- **Whole file, byte-exact**: both bone-less files. Confirmed by comparing
  the entire exported file against the source, not just specific known
  regions.
- **Byte-exact everywhere except one region, for every skinned file**:
  position, UV, index buffer, normal+tangent (via the stashed raw
  bytes), header, name tables, bone data (including the newly-modeled
  local/world matrices), material remap, and all 7 non-LOD-0 levels of
  the 8-LOD-group enemy file - all byte-identical to source. The *only*
  remaining difference for any skinned file, confirmed by diffing the
  entire exported file against source and checking every mismatched byte
  falls inside a known skin-weight accessor range: **skin weights**. The
  *values* are exactly preserved (same set of (bone name, quantized
  weight) pairs per vertex, verified by decoding both sides) - but which
  of the 8 joint/weight byte-slots a given bone occupies isn't
  recoverable from a Blender vertex group at all (it's an unordered
  per-vertex set, not the original primary/secondary split), so export
  uses a deterministic weight-descending reassignment. This is the one
  remaining non-reproducible fidelity gap, and it's structural (nothing
  Blender's vertex-group data model exposes could fix it without a
  different, non-native way of storing weights) rather than an oversight.
- Everything not touched (any file with no bones at all; every mesh
  section this export doesn't set fields on) is exact by construction -
  either through the real `_write()` mechanism now that gaps are modeled
  or restored, not just by not being touched.

Verified against real re3 install data via the full test suite (re2's
export registration is untested - this machine's re2 install is broken,
see the RE2 dataset section above): structural-field equality, per-region
byte-exact geometry checks, per-vertex weight-set equality, and a
whole-file byte-diff assertion (the strongest check - fails if *any*
unaccounted-for byte differs anywhere in the file, not just the regions
the other tests happen to look at), each as its own assertion rather than
one diff, so a real regression in one region can't hide behind an
unrelated one staying identical - plus a dedicated negative test
(exporting a mesh with no main model tree raises a clear error instead of
silently no-op'ing).
