# Modding a character (Resident Evil 4 UHD)

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

In the Albam sidebar, set the app to **Resident Evil 4 UHD**. Everything below
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
- **Object transforms** - moving, rotating or scaling the object itself is baked
  in on export, so you do not need to apply transforms first.
- **Materials** - swapping the image in a texture node changes which texture the
  model uses, because the exporter reads the binding back rather than a stored
  value.

Two things to keep in mind:

- **Keep the vertex groups.** They are the skinning, named after bone ids. A
  vertex in no group gets pinned to the first bone.
- **There is a size limit.** Both vertex counts in the format are 16-bit, so a
  model cannot exceed 65535 face corners. Corners are shared along a triangle
  strip but never across a UV seam or a shading split, so a mesh needs somewhere
  between one and three per triangle. Exceeding it is reported, not silently
  truncated. Only one model in the whole game is near it.

## 5. Export the model

Select the imported object in the Exportable list and press **Export**. The
result appears in the second File Explorer panel, the export side.

Export builds the file from what is in Blender now. The only things carried over
rather than rebuilt are the handful of header values Blender has nowhere to keep,
which ride on the mesh's and materials' albam custom properties.

Export each model you changed. Models you did not touch do not need exporting -
the repack keeps the archive's own copy.

## 6. Repack the archive

With the source archive selected on the import side and your exported files
selected on the export side, press **Pack item** and choose where to write.

This rebuilds the whole archive: your files substituted for the entries they came
from, the file table rebuilt around their new sizes, and the result recompressed.

**Name the output exactly as the original.** Entries are numbered after the
archive's own filename, so an archive under a different name produces differently
named entries and its replacements will not match.

Archives albam writes are larger than the originals - it stores its chunks rather
than compressing them. That is deliberate: albam has an LZX encoder, but archives
written with it are rejected by the game while stored ones load. Size is the
right thing to trade for a file that works.

## 7. Install and test

Back up the original, drop yours in its place under the same name, and start the
game.

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

## What does not work yet

- **A model whose bone table names one bone id twice** cannot be exported
  faithfully; import collapses the two. 69 of 738 models are affected, and the
  build tool keeps their original bytes rather than shipping them wrong.
- **Morph targets, bone pairs and adjacency** are not written back. A model with
  facial morphs loses them on export.
- **Rooms** import - geometry, props and placement - but there is no exporter for
  them.
- **The LZX encoder** produces archives the game rejects, so archives are stored
  instead and come out larger.
