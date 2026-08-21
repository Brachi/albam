# Albam
 

<p align="left">
<a href="https://github.com/Brachi/albam/actions"><img alt="Actions Status" src="https://github.com/Brachi/albam/workflows/Test/badge.svg"></a>
<img alt="Code coverage" src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Brachi/879e4f106f38b080ff10d3f46e3336e6/raw/covbadge.json">
</p>

This is the source of _Albam_, a [Blender](https://blender.org) [addon](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html) for importing and exporting 3d models and other game engine formats.   

For user documentation and modding tutorials, refer to the [Wiki](https://github.com/HenryOfCarim/albam_redux/wiki)
If you are willing to help in development or get quick help you can visit our discord server

[<img src="https://discord.com/api/guilds/1008767651578925076/widget.png?style=banner2" alt="Discord Banner 2"/>](https://discord.gg/69sphky9UX)

## Quickstart

Creating a virtualenv, installing dependencies and running tests (headless Blender)  

[bpy](https://pypi.org/project/bpy/) needs a specific Python version, matching the one used by the official release of Blender.
This might not be the case in certain Linux distros.

```
python -m venv .venv
source .venv/bin/activate
pip install .[tests]
pytest
```
Note: you need application data to run most useful tests.

### Running against a real Blender in development mode

Blender loads extensions from its per-version `extensions/user_default/` directory, keyed by the
`id` in `albam/blender_manifest.toml` (`albam`). Blender's extension scanner explicitly follows
symlinks there, so instead of copying or installing a built zip, symlink this repo's `albam/`
directory straight in. Blender then sees live edits immediately, no rebuild/reinstall step:
```
# Linux
ln -s "$(pwd)/albam" ~/.config/blender/<bl-version>/extensions/user_default/albam
# Windows (as Administrator)
mklink /D "%APPDATA%\Blender Foundation\Blender\<bl-version>\extensions\user_default\albam" "%CD%\albam"
```
After symlinking, (re)start Blender and enable "Albam" under Preferences > Get Extensions
(or Add-ons) if it isn't already.

Dependencies:
Blender's own bundled Python doesn't have this addon's pip-installed dependencies,
only the `.venv` above does. Launch Blender with
[`--python-use-system-env`](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
and `PYTHONPATH` pointing at the venv's site-packages, so Blender's bundled Python
resolves imports through it.
```
source .venv/bin/activate
PYTHONPATH="$VIRTUAL_ENV/lib/python3.13/site-packages" blender --python-use-system-env
```


### Regenerating the Kaitai Struct parsers

Binary formats are described by `.ksy` files under each engine's `structs/` directory and compiled
to the `*.py` next to them with [Kaitai Struct](https://kaitai.io/) (currently 0.11):

```
kaitai-struct-compiler --target python -w --outdir . <file>.ksy
```

`-w`/`--read-write` applies to every parser, including formats albam only reads today, so there is
one command rather than a per-file split that nothing in a `.ksy` records. It implies
`--no-auto-read`, which is the one thing callers have to know: constructing a parser (or calling
`from_bytes()`) no longer parses anything on its own, so every call site follows it with an
explicit `_read()`.

`tests/test_generated_structs.py` keeps all of this honest: every `.ksy` has to compile, every
parser has to be generated read-write, and the generated `Mesh` classes have to keep the lazy-write
attributes `albam/engines/mtfw/mesh.py` assigns to by hand (`<field>__enabled`). Those were named
`<field>__to_write` before the 0.11 release; since assigning an attribute a class doesn't define is
legal Python, that rename would otherwise have left exporting running while silently writing the
vertex and index buffers twice.

The vendored runtime in `albam/albam_vendor/kaitaistruct.py` reports `0.11.dev1` and satisfies the
`API_VERSION >= (0, 11)` check the generated code makes.

## Supported Engines

* [MT Framework](https://en.wikipedia.org/wiki/MT_Framework)


## Similar Tools

* [RevilMax](https://github.com/PredatorCZ/RevilMax])
* [Mod3-MHW-Importer](https://github.com/AsteriskAmpersand/Mod3-MHW-Importer)
* [umvc3-tools](https://github.com/tge-was-taken/umvc3-tools)
* 3ds script by Maliwei777, Aman, Mariokart64n and others

## Special Thanks

* Lukas Cone
* Ekey
* Henry of Carim
* AsteriskAmpersand
* Che
* Kami
