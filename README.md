# Albam

⚠️  
Albam is currently in heavy development and may be unstable.  
There's no documentation yet.  
⚠️  
<p align="left">
<a href="https://github.com/Brachi/albam/actions"><img alt="Actions Status" src="https://github.com/Brachi/albam/workflows/Test/badge.svg"></a>
<img alt="Code coverage" src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Brachi/879e4f106f38b080ff10d3f46e3336e6/raw/covbadge.json">
</p>

This is the source of _Albam_, a [Blender](https://blender.org) [addon](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html) for importing and exporting 3d models and other game engine formats.   

For understanding what's going on, start [here](https://github.com/Brachi/albam/blob/05a53c1b9ff12005243a12da9099a4ecf170c9e1/albam/blender_ui/import_panel.py#L73)  

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
