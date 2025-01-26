# Albam Redux
 
Albam redux is a Blender addon intended to simplify modding by leveraging the Kaitai Struct parser.

This is a fork of Albam and the spiritual successor of Albam Reloaded

<p align="left">
<a href="https://github.com/HenryOfCarim/albam_redux/actions"><img alt="Actions Status" src="https://github.com/HenryOfCarim/albam_redux/workflows/Test/badge.svg"></a>
<img alt="Code coverage" src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HenryOfCarim/8d9d772c4e886406cfead04f0a5febc1/raw/covbadge.json">
</p>

This is the source of _Albam_, a [Blender](https://blender.org) [addon](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html) for importing and exporting 3d models and other game engine formats.   

For user documentation and modding tutorials, refer to the [Wiki](https://github.com/HenryOfCarim/albam_redux/wiki)
If you are willing to help in development or get quick help you can visit our discord server

[<img src="https://discord.com/api/guilds/1008767651578925076/widget.png?style=banner2" alt="Discord Banner 2"/>](https://discord.gg/69sphky9UX)

## Quickstart

Creating a virtualenv, installing dependencies and running tests (headless Blender)  

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
* Knabsi
* Henry of Carim
* AsteriskAmpersand
* Che
