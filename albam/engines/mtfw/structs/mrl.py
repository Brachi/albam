# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mrl(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not self.id_magic == b"\x4D\x52\x4C\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x52\x4C\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.num_materials = self._io.read_u4le()
        self.num_textures = self._io.read_u4le()
        self.unk_01 = self._io.read_u4le()
        self.ofs_textures = self._io.read_u4le()
        self.ofs_materials = self._io.read_u4le()
        self.textures = []
        for i in range(self.num_textures):
            self.textures.append(Mrl.TextureSlot(self._io, self, self._root))

        self.materials = []
        for i in range(self.num_materials):
            self.materials.append(Mrl.Material(self._io, self, self._root))


    class AnimSubEntry1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(24):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((20 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



    class AnimSubEntry5(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(12):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((8 * self._parent.info.num_entry)):
                self.values.append(self._io.read_u1())



    class CmdTexIdx(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tex_idx = self._io.read_u4le()


    class ShdHalfLambert(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(4):
                self.data.append(self._io.read_f4le())



    class HashBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.index = self._io.read_bits_int_le(12)
            self.value = self._io.read_bits_int_le(20)


    class AnimInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unk = self._io.read_bits_int_le(2)
            self.num_entry2 = self._io.read_bits_int_le(16)
            self.num_entry1 = self._io.read_bits_int_le(14)


    class CmdInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd_type = self._io.read_bits_int_le(4)
            self.unk = self._io.read_bits_int_le(16)
            self.shader_obj_idx = self._io.read_bits_int_le(12)


    class AnimSubEntry0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(12):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((8 * self._parent.info.num_entry)):
                self.values.append(self._io.read_u1())



    class AnimSubEntry7(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(36):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((24 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



    class ShdHash(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.shader_hash = self._io.read_u4le()


    class ShdCbMaterial(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(32):
                self.data.append(self._io.read_f4le())



    class TextureSlot(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type_hash = self._io.read_u4le()
            self.unk_02 = self._io.read_u4le()
            self.unk_03 = self._io.read_u4le()
            self.texture_path = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ascii")


    class BlockOffset(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofc_block = self._io.read_u4le()

        @property
        def body(self):
            if hasattr(self, '_m_body'):
                return self._m_body

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_anim_data + self.ofc_block))
            self._m_body = Mrl.AnimEntry(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, '_m_body', None)


    class CmdOfsBuffer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_float_buff = self._io.read_u4le()


    class ShdToon2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(4):
                self.data.append(self._io.read_f4le())



    class AnimDataInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_bits_int_le(4)
            self.unk_00 = self._io.read_bits_int_le(4)
            self.num_entry = self._io.read_bits_int_le(24)


    class AnimSubEntry4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((20 * self._parent.info.num_entry)):
                self.values.append(self._io.read_f4le())

            self.hash = self._io.read_u4le()


    class ShdIndirectUser(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(12):
                self.data.append(self._io.read_f4le())



    class Material(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type_hash = self._io.read_u4le()
            self.name_hash_crcjam32 = self._io.read_u4le()
            self.cmd_buffer_size = self._io.read_u4le()
            self.blend_state_hash = self._io.read_u4le()
            self.depth_stencil_state_hash = self._io.read_u4le()
            self.rasterizer_state_hash = self._io.read_u4le()
            self.cmd_list_info = Mrl.HashBlock(self._io, self, self._root)
            self.material_info_flags = []
            for i in range(4):
                self.material_info_flags.append(self._io.read_u1())

            self.unk_nulls = []
            for i in range(4):
                self.unk_nulls.append(self._io.read_u4le())

            self.anim_data_size = self._io.read_u4le()
            self.ofs_cmd = self._io.read_u4le()
            self.ofs_anim_data = self._io.read_u4le()

        @property
        def resources(self):
            if hasattr(self, '_m_resources'):
                return self._m_resources

            _pos = self._io.pos()
            self._io.seek(self.ofs_cmd)
            self._m_resources = []
            for i in range(self.cmd_list_info.index):
                self._m_resources.append(Mrl.ResourceBinding(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_resources', None)

        @property
        def anims(self):
            if hasattr(self, '_m_anims'):
                return self._m_anims

            if self.anim_data_size != 0:
                _pos = self._io.pos()
                self._io.seek(self.ofs_anim_data)
                self._m_anims = Mrl.AnimData(self._io, self, self._root)
                self._io.seek(_pos)

            return getattr(self, '_m_anims', None)


    class AnimSubEntry6(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(36):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((24 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



    class AnimData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entry_count = self._io.read_u4le()
            self.ofs_entry = self._io.read_u4le()
            self.unk_00 = []
            for i in range(self.entry_count):
                self.unk_00.append(self._io.read_u4le())

            self.info = Mrl.AnimInfo(self._io, self, self._root)
            self.ofs_list_entry1 = self._io.read_u4le()
            self.unk_hash = self._io.read_u4le()
            self.ofs_entry2 = []
            for i in range(self.info.num_entry2):
                self.ofs_entry2.append(Mrl.BlockOffset(self._io, self, self._root))

            self.set_buff_hash = []
            for i in range(self.info.num_entry1):
                self.set_buff_hash.append(self._io.read_u4le())



    class OfsBuff(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_const_buff = self._io.read_u4le()


    class ShdDiffColCorrect(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(4):
                self.data.append(self._io.read_f4le())



    class ShdSGlobals(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            for i in range(76):
                self.data.append(self._io.read_f4le())



    class TexOffset(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.texture_id = self._io.read_u4le()


    class AnimEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.shader_hash = self._io.read_u4le()
            self.info = Mrl.AnimDataInfo(self._io, self, self._root)
            _on = self.info.type
            if _on == 0:
                self.entry = Mrl.AnimSubEntry0(self._io, self, self._root)
            elif _on == 4:
                self.entry = Mrl.AnimSubEntry4(self._io, self, self._root)
            elif _on == 6:
                self.entry = Mrl.AnimSubEntry6(self._io, self, self._root)
            elif _on == 7:
                self.entry = Mrl.AnimSubEntry7(self._io, self, self._root)
            elif _on == 1:
                self.entry = Mrl.AnimSubEntry1(self._io, self, self._root)
            elif _on == 3:
                self.entry = Mrl.AnimSubEntry3(self._io, self, self._root)
            elif _on == 5:
                self.entry = Mrl.AnimSubEntry5(self._io, self, self._root)
            elif _on == 2:
                self.entry = Mrl.AnimSubEntry2(self._io, self, self._root)


    class ResourceBinding(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.info = Mrl.CmdInfo(self._io, self, self._root)
            _on = self.info.cmd_type
            if _on == 0:
                self.value_cmd = Mrl.HashBlock(self._io, self, self._root)
            elif _on == 4:
                self.value_cmd = Mrl.HashBlock(self._io, self, self._root)
            elif _on == 1:
                self.value_cmd = Mrl.CmdOfsBuffer(self._io, self, self._root)
            elif _on == 3:
                self.value_cmd = Mrl.CmdTexIdx(self._io, self, self._root)
            elif _on == 2:
                self.value_cmd = Mrl.HashBlock(self._io, self, self._root)
            self.shader_object_hash = self._io.read_u4le()

        @property
        def float_buffer(self):
            if hasattr(self, '_m_float_buffer'):
                return self._m_float_buffer

            if self.info.cmd_type == 1:
                _pos = self._io.pos()
                self._io.seek((self._parent._io.pos() + self.value_cmd.ofs_float_buff))
                _on = self.shader_object_hash
                if _on == 1820332537:
                    self._m_float_buffer = Mrl.ShdCbMaterial(self._io, self, self._root)
                elif _on == 2066489676:
                    self._m_float_buffer = Mrl.ShdSGlobals(self._io, self, self._root)
                elif _on == 2066489689:
                    self._m_float_buffer = Mrl.ShdSGlobals(self._io, self, self._root)
                elif _on == 2066489695:
                    self._m_float_buffer = Mrl.ShdSGlobals(self._io, self, self._root)
                elif _on == 1820332522:
                    self._m_float_buffer = Mrl.ShdCbMaterial(self._io, self, self._root)
                elif _on == 2066489694:
                    self._m_float_buffer = Mrl.ShdSGlobals(self._io, self, self._root)
                elif _on == 1820332542:
                    self._m_float_buffer = Mrl.ShdCbMaterial(self._io, self, self._root)
                elif _on == 2066489685:
                    self._m_float_buffer = Mrl.ShdSGlobals(self._io, self, self._root)
                elif _on == 1820332532:
                    self._m_float_buffer = Mrl.ShdCbMaterial(self._io, self, self._root)
                elif _on == 1820332544:
                    self._m_float_buffer = Mrl.ShdCbMaterial(self._io, self, self._root)
                self._io.seek(_pos)

            return getattr(self, '_m_float_buffer', None)


    class AnimSubEntry3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(24):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((16 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



    class AnimSubEntry2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = []
            for i in range(12):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((8 * self._parent.info.num_entry)):
                self.values.append(self._io.read_u1())




