# Modding a character (RE4UHD)

A worked example: taking the player character, changing something about him, and
getting the result back into the game.

The same steps apply to any character or enemy. Everything here has been done end
to end and confirmed in the running game.

## Before you start

- Blender 5.2 with albam installed.
- A legitimate installation of the game.
- **A backup of any archive you replace.** albam never writes into your install;
  you do, and the game will not put a file back for you.

## 1. Pick the app

In the Albam sidebar, set the app to **RE4UHD**. Everything below
is keyed off that: which importers run, which formats are offered, how an
archive is repacked.

## 2. Add the character's archive

Use **Add Files** in the File Explorer panel and choose the archive holding the
character you want. Characters and enemies each live in their own `.udas.lfs`
inside the game's character folder, named after the character's own id.

**Add Folder is not useful for this game**, unlike the MT Framework titles. An
archive here keeps its file table *inside* its compressed stream, so listing one
means decompressing the whole thing - about 0.38 MB/s, against several GB across
an install. albam therefore mounts one archive at a time. This is a deliberate
limitation, not an oversight; see `albam/engines/cie/fs.py`.

A mounted archive expands into numbered entries, because the container stores no
names - only positions. A `.bin` is a model, a `.tpl` is a texture list, and the
rest are animation and script data albam does not read yet.

## How the files fit together

Worth five minutes before you change anything: what you edit in Blender is one
file inside one archive, and its textures are in a different archive entirely.

```
pl00.udas.lfs                  the archive you add - LZX compressed
|
+-- pl00.udas                  the container inside it, entries in order,
    |                          none of them named
    +-- pl00_000.bin           a model (the body)
    +-- pl00_001.bin           another part of the same character
    +-- ...                    25 of them for a main character
    +-- pl00_015.tpl           a texture list
             |
             |  entry 3 says: pack 44000002, texture 7
             v
    44000002.pack.lfs          a DIFFERENT archive, in ImagePackHD/
    +-- 44000002_007.dds       the actual texture bytes
```

An archive holds no names for its entries, only positions, so albam numbers
them after the archive's own filename: `pl00.udas.lfs` gives `pl00_000.bin`,
`pl00_001.bin` and so on. **Rename the archive and every entry inside it is
renamed too** - which is why step 6 insists you write the repacked file under
the original name.

| Entry | What it is | What albam does |
| --- | --- | --- |
| `.bin` with the mesh flag | a model | imports and exports it |
| `.bin` without it | camera, lighting, collision | refuses it with an error |
| `.tpl` | a texture list: slot -> pack id + index | reads it |
| `.pack` (separate archive) | the texture bytes, DDS or TGA | reads it |
| everything else | animation, script data | not read yet |

Three things follow, and they are what catches people out:

- **A material names a slot, not a texture.** Its `diffuse_map` is an index
  into a `.tpl`, and the model never says which `.tpl` - so picking the wrong
  one textures your character with someone else's textures. Step 3 covers the
  setting that decides this.
- **Textures live outside the archive you are modding**, so the archive alone
  is not enough to import a textured model. Step 3 covers what to do when you
  are working from a copy.
- **A pack is shared by many models**, so anything done to a texture is done to
  every model using it. About a third of the packs are named `*.pack.yz2.lfs`;
  that extra segment is bookkeeping, and the payload is a plain pack like any
  other - true of every one in an install. Step 4 covers how a new texture is
  added without touching the ones other models share.

The parts of a character also share one skeleton, which is why the order you
import them in matters - again, step 3.

## 3. Import the model

Select a `.bin` entry and press **Import**.

Not every `.bin` is a model: cameras, lighting and collision data share the
extension. albam only offers the ones that really are models.

A character is not one model. The example character is 25 of them - body,
jacket, head, hands, weapon attachments, level-of-detail copies. Import the ones
you want to work on; you do not need all of them.

### The two import options

Both default to doing the right thing, and both are worth understanding.

**Textures.** A model does not name its texture list. Its materials hold indices
into one, and its archive can hold dozens - one enemy archive carries 75 for 120
models. Left on **Auto**, albam works out which one the model's own materials
fit, and is right about 99.9% of the time across every character and enemy in the
game. Override it only if you know better.

The textures themselves live in a *separate* archive named after the pack id the
texture list refers to. albam finds it next to the model's own archive, so
importing from the install just works. If you have copied an archive out to a
working folder, add any archive from the install too and albam will look beside
that one as well.

**Attach to armature.** Leave it empty. A character archive holds one model
carrying the whole skeleton and many carrying only the bones they need, so albam
reuses a rig already imported from the same archive that covers the model's
bones. Import the body first and the head, jacket and hands attach to the same
skeleton rather than arriving with part-skeletons of their own. The field is an
override for when you want a specific one.

## 4. Make your change

Anything you do to the mesh is what gets written:

- **Vertex edits** - move, scale, sculpt, add or remove geometry.
- **Object transforms** - moving, rotating or scaling the mesh itself is baked
  in on export, so you do not need to apply transforms first. What is baked is
  the mesh's placement *relative to its armature*, so moving the armature
  object carries the whole model with it in Blender and changes nothing in the
  exported file - where a model sits in the world is the room's data, not the
  model's.
- **Materials and textures** - the exporter reads back which image each
  texture node holds, so what you wire up is what the model uses:
  - **Another image from the same texture list** re-points the material at
    that slot. Nothing else changes.
  - **A new image** - one you open or create in Blender - is added as a new
    texture: appended to the texture pack the model draws from, given a new
    slot in its `.tpl`, and the material points at that slot. Nothing that
    already exists changes, so other models sharing the pack are unaffected.
    The image is encoded the way the texture it took the place of was (DXT1,
    DXT5, uncompressed DDS and TGA stay what they were, DXT3 becomes DXT5); a
    `.dds` you open goes in exactly as it is.
  - **A texture imported for another model** gets a slot in this model's
    `.tpl` pointing at it where it already is.
  - **Editing an imported image itself** - painting on it, or unpacking it and
    changing its file - rewrites that texture in its pack, which **every model
    using it** then shows. Note that *Image > Replace* does nothing to an
    imported image: albam packs them into the .blend, and Blender keeps a
    packed image's bytes when its path changes. Open the new file as its own
    image and wire that in instead.

  A new or edited texture needs the model's archive and its texture pack
  reachable at export, the same way import found them.
- **Facial morphs** - a model's morph targets arrive as shape keys named `000`,
  `001`, ... and are written back, edits included.

Three things to keep in mind:

- **Keep the vertex groups.** They are the skinning, named after bone ids. A
  vertex in no group gets pinned to the first bone.
- **Keep the shape key names.** The game asks for a morph by its number, and
  a key named `007` is written as morph 7 wherever it sits in the list.
  Renaming one moves it: an animation asking for a smile gets whatever now has
  that number. A number no key has is exported as an empty morph, and a key
  with any other name is added after the numbered ones.
- **There is a size limit.** Both vertex counts in the format are 16-bit, so a
  model cannot exceed 65535 face corners. Corners are shared along a triangle
  strip but never across a UV seam or a shading split, so a mesh needs somewhere
  between one and three per triangle. Exceeding it is reported, not silently
  truncated. Only one model in the whole game is near it.
- **There is a bone limit as well.** A bone is named by a single byte, so a
  model can write at most 255 of them. Only the bones the model actually needs
  count - the ones it was imported with, plus the ones its weights name - so
  control and IK bones nothing is weighted to are free, however many of them a
  rig carries. Going past the limit is reported too, rather than exported with
  bones silently sharing an id.

## 5. Export the model

Select the imported object in the Exportable list and press **Export**. The
result appears in the second File Explorer panel, the export side.

Export builds the file from what is in Blender now. The only things carried over
rather than rebuilt are the handful of header values Blender has nowhere to keep,
which ride on the mesh's and materials' albam custom properties.

Export each model you changed. Models you did not touch do not need exporting -
the repack keeps the archive's own copy.

A model whose textures changed exports more than its `.bin`: its `.tpl`, if it
gained a slot, and every texture that is new or was edited, named after the pack
entry it becomes (`00000010_212.dds`). New textures are numbered from the pack
as it is on disk, so add textures to **one model per pack at a time**, and pack
it before exporting the next. Two exports adding to the same pack or `.tpl`
give their new textures the same numbers, and the second export overwrites the
first's new textures in the export list: an export replaces files of the same
name already there. Once the first model's archive and packs are packed and
installed, the next export numbers its textures after them.

## 6. Repack the archive

With the source archive selected on the import side and your exported files
selected on the export side, press **Pack item** and choose where to write.

This rebuilds the whole archive: your files substituted for the entries they came
from, the file table rebuilt around their new sizes, and the result recompressed.

**Name the output exactly as the original.** Entries are numbered after the
archive's own filename, so an archive under a different name produces differently
named entries and its replacements will not match.

If the export carries textures, **Pack item** also rebuilds the texture packs
they belong to, under their original names, in `ImagePack/` and `ImagePackHD/`
beside the folder you write the archive into - where the game and albam look
for them. Writing `BIO4/Em/pl08.udas.lfs` puts the packs in
`BIO4/ImagePack/` and `BIO4/ImagePackHD/`, so writing straight into the
install, or into a mod folder laid out like `BIO4`, needs nothing more, and
re-importing the written archive finds its new textures. The report at the
bottom of the window lists every file written. Both copies are written because
which one the game loads is its texture quality setting, and a slot the `.tpl`
names has to exist in whichever it picks. A pack's HD copy can be tens of
megabytes, so recompressing it takes a few minutes. Nothing is written if
either step fails.

Archives albam writes come out about 6% larger than the originals. Its LZX
encoder does not find quite as many matches as the one the game shipped with,
which costs size and nothing else.

## 7. Install and test

Back up the original, drop yours in its place under the same name, and start the
game. Texture packs go the same way: back up the original packs in
`BIO4/ImagePack` and `BIO4/ImagePackHD` and put the written ones in their
place. If you wrote into a folder laid out like `BIO4`, that is copying its
`Em`, `ImagePack` and `ImagePackHD` folders over the install's.

If you are iterating, keep the backup outside the install and swap the two files
with a one-line script rather than by hand - it is easy to lose the original
otherwise, and the game will not restore it for you.

## 8. Check your work before you ship it

Importing a model and exporting it again proves less than it looks. albam reads
its own output, so a file it writes wrongly still comes back looking right in
Blender. Several archives that crashed or visibly broke the game passed exactly
that check.

What catches those is comparing a **no-edit re-export against the bytes the
archive shipped with**:

```
python tests/tools/cie_build_mod.py <archive> <out-dir> [scale]
```

It re-exports every model with no changes, compares bone tables, texture slots,
material counts and geometry against the original, and only then writes an edited
archive - keeping the original bytes for any model that did not reproduce. If
something is wrong with the exporter, you find out before the game does.

## If the game does not load it

Add one layer of albam at a time, and whichever fails first names the layer:

1. **The container only** - repack with every file inside taken from the original
   archive. If this fails, nothing about your model is involved.
2. **Models re-exported, unedited** - adds the mesh exporter.
3. **Your edit** - adds the change itself.

`cie_build_mod.py` writes the second and third of those for you.

## Modding a room

Rooms follow the same steps with a different file. A room's archive is under
`BIO4/St<n>/`, named after the room (`St1/r102.udas.lfs` is the typewriter
room of chapter 1-3). The room itself is its `.smd` entry: importing it builds
one empty named after the file, with an object for every model the room
places under it.

- **Move, rotate, scale or delete** those objects and the room's entries follow.
  A placement that was imported as an empty with the model under it (the room
  stretched and rotated that model) keeps that shape: transform the empty, or
  scale the room's object evenly. A transform the file can't hold is refused
  with a message rather than written off target.
- **Add a placement** by duplicating one (Shift+D or Alt+D), or by putting an
  object that shows one of the room's meshes under the room.
- **Edit a model's mesh** and every placement of it changes, since the room
  stores each model once. Models you don't touch keep their shipped bytes.
- **Export** the room's object, then **Pack item** with the room's archive
  selected, as for a character.

Two things the room's `.smd` does not cover:

- **Collision is a separate file.** What the player walks on and bumps into
  lives in the room's `.sat`/`.eat` entries, which albam does not write.
  Moving a wall moves what is drawn, not where Leon stops.
- **Some rooms are split across archives** (`r100_00.dat.lfs`,
  `r100_01.dat.lfs`, ... sharing models with `r100.udas.lfs`). Import finds the
  shared archive next to the one you open; if it is not there, the shared
  models are not built, and export leaves their entries exactly as they were.

## What does not work yet

- **Rooms** export their placements and their models. Moving, rotating, scaling
  or deleting the objects placed in a room's `.smd`, and editing the meshes
  themselves, is written back; a model left alone keeps its shipped bytes, and
  so does everything else in the file. If an edited model no longer fits where
  it was, the models are laid out again and the file grows only by what the
  edit added. Duplicating a placement in Blender, or putting one of the room's
  meshes under the room as a new object, adds an entry for it. Adding models
  the room doesn't have, and the one room assembled from several files, are
  not supported yet.
- **Textures are only partly confirmed in the running game.** Adding a texture
  works with the HD texture setting: a new image on Leon's `pl08` got its new
  `.tpl` slot and appended pack entry drawn in game. The SD setting, and editing
  an imported texture in place, have not been checked in game yet. The files
  are laid out the way the shipped ones are: rebuilding the shipped `.tpl`
  files of an install gives back the same bytes for 1907 of 1919, another 10
  differ only by trailing zero padding, and the 2 system files with palettes
  are refused; a rebuilt pack keeps every texture it did not change byte for
  byte. Whether the game limits how many textures a pack or a `.tpl` can hold
  is not known yet.
- **A `.tpl` holds at most 255 slots**, since a material names one in a single
  byte; adding past that is reported.
