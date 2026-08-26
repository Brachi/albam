# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [unreleased]

### Added

- Autofixer for export: automatic mesh tweaks such as mesh triangulation and set object transformations. This is more beginner friendly.
- Import option to batch import all `.mod` files from a selected folder at once
- Export option to remove orphaned textures from `.arc` files when using custom texture paths
- Error message for the case when there is no mesh to export
- Support for navigation mesh import-export (Resident Evil 5)
- Autosorter tool to automatically set `alpha priority` values ​​for hair cards
- App Settings button next to App selection. Allows to set the root folder of an app. Its content is stored in apps-userdata.ini, in Albam's extension directory.

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
- Duplicate file-load handlers left behind after disabling and re-enabling the addon

### Changed

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
