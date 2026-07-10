# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [unreleased]

### Added

- Autofixer for export: automatic mesh tweaks such as mesh triangulation and set object transformations. This is more beginner friendly.
- Import option to batch import all `.mod` files from a selected folder at once
- Export option to remove orphaned textures from `.arc` files when using custom texture paths

### Fixed

- Import of meshes with Nan UVs
- Triangulation function(now it keeps custom normals)
- Missed value in .tex `value` enumerator for RE6 render targets

### Changed

### Removed

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
