import os
import bpy

from albam.lib.dds import DDSHeader


def build_blender_textures(texture_paths, context):
    vfs = context.scene.albam.vfs
    tex_mapping = {}
    for path in texture_paths:
        texture_vfile = vfs.get_vfile("reorc", path)
        texture_bytes = texture_vfile.get_bytes()
        dds_header = DDSHeader()
        import io
        io.BytesIO(texture_bytes).readinto(dds_header)
        bl_image = bpy.data.images.new(os.path.basename(path), dds_header.dwWidth, dds_header.dwHeight)
        bl_image.source = "FILE"
        bl_image.pack(data=bytes(texture_bytes), data_len=len(texture_bytes))

        tex_mapping[path] = bl_image

    return tex_mapping
