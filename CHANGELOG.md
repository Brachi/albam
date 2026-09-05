# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [unreleased]

### Added

- Support for Resident Evil 4 UHD: import and export of characters and enemies, room
  import, and repacking edited files back into the game's archives. See
  `docs/modding-a-character.md` for the full edit-and-repack workflow.
- Autofixer for export: automatic mesh tweaks such as mesh triangulation and set object transformations. This is more beginner friendly.
- Import option to batch import all `.mod` files from a selected folder at once
- Export option to remove orphaned textures from `.arc` files when using custom texture paths
- Error message for the case when there is no mesh to export
- Support for navigation mesh import-export (Resident Evil 5)
- Autosorter tool to automatically set `alpha priority` values for hair cards
- Experimental support for LMT export (Resident Evil 5)
- App Settings button next to App selection. Allows to set the root folder of an app. Its content is stored in apps-userdata.ini, in Albam's extension directory.
- Reading `.arc` archives from Devil May Cry 4, whose entries are XMemCompress (LZX) streams rather than zlib, and which number their file types differently. Models and textures inside them can now be imported. Read-only for now: packing into one is refused rather than writing an archive the game cannot read

### Fixed

- Import of meshes with Nan UVs
- Triangulation function(now it keeps custom normals)
- Missed value in .tex `value` enumerator for RE6 render targets
- Missed `FTransparencyDodgeMap` in `FTransparency` enum for RE6 maps
- Import SBC for DMC4
- Issue with SBC generation that broke high collision mesh (eff) and left holes in low collision mesh (scr)
- Typo that set wrong name ("name") for the color attribute layer
- Typo that brightened vertex colors on every import-export round trip
- Vertex colors losing precision on every import-export round trip
- Vertices export with multiple attributes, causing artifacts around UV seams
- Crash when disabling and re-enabling the addon within the same Blender session
- Duplicate file-load handlers left behind after disabling and re-enabling the addon
- Animation blocks that never move losing their length on export, so a static
  hold played back as a single frame
- Exported animation tracks that could not be read back, when a rotation's
  quantized components summed past unit norm
- Animation tracks landing on an unrelated bone when the skeleton has no bone
  for that animation id, dropping the id from an exported `.lmt`
- A second animation file imported onto the same skeleton leaving its limb
  chains solving towards goals none of its blocks move
- Spurious "Array iterator out of range" messages printed on every export of a mesh with fewer UV layers than the vertex format allows

### Changed

- A bone's animation re-targeting id is now an Albam custom property on the pose
  bone, shown as "Anim Retarget" in the Bone tab, instead of the raw
  `mtfw.anim_retarget` property. Rigs in `.blend` files saved with the old
  property are migrated the first time they are used

### Removed

- Split UV Seams tool, no longer needed now that export splits vertices automatically

## [0.5.0] - 2026-04-03

### Added

- Support for importing files from unpacked files, using folders
- Devil May Cry 4 import/export support (from uncompressed files only)
- Error message when exporting images with the same relative path
- Group ID to names of baked hand (hand shaker tool)
- Blender UI message when importing/exporting is finished
- Texture import support
- Blender 5 support
- Tools: Batch Transfer Weights operator
- Tools: Set Armature Object
- Tools: Use Clones toggle for Separate by Material operator
- Tools: messages when operators finish jobs

### Fixed

- Collision format (sbc) version 156 (RE5) import
- Render Targets format (rtex) export
- Issue with batch props pasting
- Tools: minor fixes
- RE6 import: em5600

### Changed

- Layout of import/export seetings in UI
- Layout of tools and minor renames

### Removed

- Blender 3.6 support
