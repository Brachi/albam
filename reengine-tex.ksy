#import ctypes as c
#from albam.image_formats.dds import DDS_Header
#from albam.lib.structure import DynamicStructure, DynamicArray
#
#
#class Tex(DynamicStructure):
#
#    _fields_ = (
#        ("id_magic", c.c_char * 4),
#        ("unk_1", c.c_uint),
#        ("width", c.c_ushort),
#        ("height", c.c_ushort),
#        ("unk_2", c.c_ushort),
#        ("unk_3", c.c_ushort),
#        ("dxt_type", c.c_uint),
#        ("unk_4", c.c_uint),
#        ("unk_5", c.c_uint),
#        ("unk_6", c.c_uint),
#        ("offset_data", c.c_uint),
#        ("unk_7", c.c_uint),
#        ("unk_8", c.c_uint),
#        ("size_data", c.c_uint),
#        ("dds_data", DynamicArray(c.c_ubyte, "size_data")),
#    )
#
#    def to_dds(self):
#        # XXX copy paste from mtframework
#
#        header = DDS_Header(
#            dwHeight=self.height,
#            dwWidth=self.width,
#            # dwMipMapCount=self.mipmap_count,
#            # pixelfmt_dwFourCC=pixelfmt
#        )
#        header.set_constants()
#        header.set_variables()
#        dds = bytearray(header)
#        dds.extend(bytes(self.dds_data))
#        return dds
