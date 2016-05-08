Albam
=====
[![Build Status](https://travis-ci.org/Brachi/albam.svg?branch=master)](https://travis-ci.org/Brachi/albam)
[![Coverage Status](https://coveralls.io/repos/Brachi/albam/badge.svg?branch=master&service=github)](https://coveralls.io/github/Brachi/albam?branch=master)

This is the source code of Albam, a [Blender](https://www.blender.org) addon that lets you import and export video game models.

### Installation
Albam works in Blender versions 2.70 and above. Other versions below might work but haven't been tested.
If you don't already have blender, you can download a copy at the official [website](https://www.blender.org/downloads/)

* Download the latest release from the [releases section](https://github.com/Brachi/albam/releases)
* Without unzipping the file downloaded, [install as an addon](https://www.blender.org/manual/advanced/scripting/python/add_ons.html#installation-of-a-3rd-party-add-on) by going to File--> User Preferences and then to the 'Addons' tab. There click 'Install from file' and select the zip file downloaded. Lastly, enable the addond by checking the checkbox.


### List of games supported
Currently the project is in alpha stage, but many more games are to be added soon once the code becomes more stable
As of version 0.0.1, the only game supported is Resident Evil 5 (Biohazard 5) for PC.


### What?
Albam is aimed to 2 types of audiences: modders and researchers.
Modders change games visuals and behaviors, by using tools like this to provide new experiences, improve games quality and fun. Albam goal is to provide the best user experience by being simple to use[1] and taking all the hassle of dealing with different formats by keeping everything inside Blender, so modders can focus on the art.
Researchers like to understand how certain parts of a game works and how the different file formats are used and structured, usually by reverse engineering. Albam tries to make the process of adding a new unknown format simple[2], keeps a comprehensive set of tests for each file format and will add tools for auto-documentation and help in the research process.

[1] Simple as in 'one button to import, one to export', to have a model usable
[2] Still a work in progress, but more info on how dynamic structures are used will be added


### Examples

Click the image below for a video on how to import, modify and export a model from the game Resident Evil 5:

[![Importing/Exporting in Resident Evil 5](http://img.youtube.com/vi/mbXSFLhitOk/0.jpg)](https://www.youtube.com/watch?v=mbXSFLhitOk)


### Contributing
Contributions are welcome, especially from researchers to add new game formats or fill the current unknowns.
The test suite provided uses py.test, but the original game files are not provided. More information will be added soon.

