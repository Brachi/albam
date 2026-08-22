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

## Next

A separate pass is cross-referencing this `.ksy`'s many `unk_*`/`test_*`/
`TODO` placeholders against RE-Mesh-Editor (a non-Kaitai RE Engine mesh
importer that already has much of this figured out) to fill in real field
names/meanings before further format work.
