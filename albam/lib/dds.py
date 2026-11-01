from ctypes import Structure, c_int, c_char, sizeof
import io
import math

from ..exceptions import AlbamCheckFailure


class DDSHeader(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
    DDSD_CAPS = 0x1
    DDSD_HEIGHT = 0x2
    DDSD_WIDTH = 0x4
    DDSD_PITCH = 0x8
    DDSD_PIXELFORMAT = 0x1000
    DDSD_MIPMAPCOUNT = 0x20000
    DDSD_LINEARSIZE = 0x80000
    DDSD_DEPTH = 0x800000

    DDSCAPS_COMPLEX = 0x8
    DDSCAPS_MIPMAP = 0x400000
    DDSCAPS_TEXTURE = 0x1000

    DDSCAPS2_CUBEMAP = 0x200
    DDSCAPS2_CUBEMAP_POSITIVEX = 0x400
    DDSCAPS2_CUBEMAP_NEGATIVEX = 0x800
    DDSCAPS2_CUBEMAP_POSITIVEY = 0x1000
    DDSCAPS2_CUBEMAP_NEGATIVEY = 0x2000
    DDSCAPS2_CUBEMAP_POSITIVEZ = 0x4000
    DDSCAPS2_CUBEMAP_NEGATIVEZ = 0x8000
    DDSCAPS2_VOLUME = 0x200000
    CUBEMAP_ALL_FACES = (
        DDSCAPS2_CUBEMAP |
        DDSCAPS2_CUBEMAP_POSITIVEX | DDSCAPS2_CUBEMAP_NEGATIVEX |
        DDSCAPS2_CUBEMAP_POSITIVEY | DDSCAPS2_CUBEMAP_NEGATIVEY |
        DDSCAPS2_CUBEMAP_POSITIVEZ | DDSCAPS2_CUBEMAP_NEGATIVEZ
    )

    DDPF_ALPHAPIXELS = 0x1
    DDPF_FOURCC = 0x4
    DDPF_RGB = 0x40

    REQUIRED_FLAGS = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT

    _fields_ = (
        ("id_magic", c_char * 4),
        ("dwSize", c_int),
        ("dwFlags", c_int),
        ("dwHeight", c_int),
        ("dwWidth", c_int),
        ("dwPitchOrLinearSize", c_int),
        ("dwDepth", c_int),
        ("dwMipMapCount", c_int),
        ("dwReserved1", c_int * 11),
        ("pixelfmt_dwSize", c_int),
        ("pixelfmt_dwFlags", c_int),
        ("pixelfmt_dwFourCC", c_char * 4),
        ("pixelfmt_dwRGBBitCount", c_int),
        ("pixelfmt_dwRBitMask", c_int),
        ("pixelfmt_dwGBitMask", c_int),
        ("pixelfmt_dwBBitMask", c_int),
        ("pixelfmt_dwABitMask", c_int),
        ("dwCaps", c_int),
        ("dwCaps2", c_int),
        ("dwCaps3", c_int),
        ("dwCaps4", c_int),
        ("dwReserved2", c_int),
    )

    def set_constants(self):
        self.id_magic = b"DDS "
        self.dwSize = 124
        self.dwFlags = self.REQUIRED_FLAGS
        self.pixelfmt_dwSize = 32
        self.dwCaps = self.DDSCAPS_TEXTURE

    def set_variables(self, compressed=True, cubemap=False):
        if not compressed:
            self.dwPitchOrLinearSize = 0
        else:
            try:
                self.dwPitchOrLinearSize = self.calculate_linear_size(
                    self.dwWidth, self.dwHeight, self.pixelfmt_dwFourCC
                )
                self.dwFlags |= self.DDSD_LINEARSIZE
            except Exception as err:
                print(f"failed to set dwPitchOrLinearSize: {err}")

        if self.dwMipMapCount:
            self.dwFlags |= self.DDSD_MIPMAPCOUNT
            self.dwCaps |= self.DDSCAPS_MIPMAP
            self.dwCaps |= self.DDSCAPS_COMPLEX
            # TODO: add 'or cubic or mipmapped_volume'

        if compressed:
            self.pixelfmt_dwFlags |= self.DDPF_FOURCC
        else:
            # specific for observed .tex in RE5 so far
            self.pixelfmt_dwFlags |= self.DDPF_RGB
            self.pixelfmt_dwFlags |= self.DDPF_ALPHAPIXELS  # TODO: need without alpha?
            self.pixelfmt_dwRGBBitCount = 32
            self.pixelfmt_dwRBitMask = 0xFF0000
            self.pixelfmt_dwGBitMask = 0xFF00
            self.pixelfmt_dwBBitMask = 0xFF
            self.pixelfmt_dwABitMask = 0xFF000000
        if cubemap:
            self.dwCaps2 |= self.DDSCAPS2_CUBEMAP
            self.dwCaps2 |= self.DDSCAPS2_CUBEMAP_POSITIVEX
            self.dwCaps2 |= self.DDSCAPS2_CUBEMAP_NEGATIVEX
            self.dwCaps2 |= self.DDSCAPS2_CUBEMAP_POSITIVEY
            self.dwCaps2 |= self.DDSCAPS2_CUBEMAP_NEGATIVEY
            self.dwCaps2 |= self.DDSCAPS2_CUBEMAP_POSITIVEZ
            self.dwCaps2 |= self.DDSCAPS2_CUBEMAP_NEGATIVEZ

    @property
    def is_proper_cubemap(self):
        return self.dwCaps2 & self.CUBEMAP_ALL_FACES == self.CUBEMAP_ALL_FACES

    @property
    def is_volume(self):
        if self.dwCaps2 & self.DDSCAPS2_VOLUME:
            return True
        return bool(self.dwFlags & self.DDSD_DEPTH) and self.dwDepth > 1

    @property
    def mipmap_sizes(self):
        h = self.dwWidth
        w = self.dwHeight
        fmt = self.pixelfmt_dwFourCC
        # FIXME: last 2 seem always duplicate
        return [self.calculate_mipmap_size(w, h, i, fmt) for i in range(self.dwMipMapCount)]

    @staticmethod
    def get_block_size(fmt):
        if fmt in (b"DXT1", b"BC1", b"BC4"):
            return 8
        elif fmt in (b"DXT3", b"DXT5"):
            return 16
        else:
            raise RuntimeError("Unrecognized format in dds: {}".format(fmt))

    @classmethod
    def calculate_linear_size(cls, width, height, fmt):
        block_size = cls.get_block_size(fmt)
        return ((width + 3) >> 2) * ((height + 3) >> 2) * block_size

    @property
    def block_size(self):

        fmt = self.pixelfmt_dwFourCC
        if fmt == b"DXT1" or fmt == b"DXT4":
            return 8
        return 16

    @staticmethod
    def calculate_mipmap_size(width, height, level, fmt):
        w = max(1, width >> level)
        h = max(1, height >> level)
        w <<= 1
        h <<= 1

        size = 0

        if w > 1:
            w >>= 1
        if h > 1:
            h >>= 1
        if not fmt:
            size += (w * h) * 4
        else:
            size += ((w + 3) // 4) * ((h + 3) // 4)
            if fmt == b"DXT1" or fmt == b"DXT4":
                size *= 8
            else:
                size *= 16

        return size

    @property
    def data(self):
        return self._dds_data

    @property
    def image_count(self):
        return 6 if self.is_proper_cubemap else 1

    @staticmethod
    def static_calculate_mipmap_count(width, height):
        return int(math.log(max(width, height), 2))

    def calculate_mipmap_count(self):
        return self.static_calculate_mipmap_count(self.dwWidth, self.dwHeight)

    def calculate_mimpap_offsets(self, base_offset):
        current_offset = base_offset
        mipmap_offsets = [current_offset]
        for im in range(self.image_count):
            for i in range(self.dwMipMapCount):
                # Don't calculate last offset since we already start with one extra
                if im == self.image_count - 1 and i == self.dwMipMapCount - 1:
                    break
                current_offset += self.mipmap_sizes[i]
                mipmap_offsets.append(current_offset)
        return mipmap_offsets

    @staticmethod
    def calculate_mipmap_size_halved_blocks(width, height, level, fmt):
        """Size of a mipmap level when the block count, rather than the pixel
        size, is halved per level. Capcom's own non-power-of-two .tex data is
        laid out this way (e.g. a 400x400 DXT1 has 12x12 blocks at level 3,
        not 13x13), so it can be smaller than calculate_mipmap_size()."""
        if not fmt:
            return DDSHeader.calculate_mipmap_size(width, height, level, fmt)
        blocks_w = max(1, ((width + 3) // 4) >> level)
        blocks_h = max(1, ((height + 3) // 4) >> level)
        block_size = 8 if fmt in (b"DXT1", b"DXT4") else 16
        return blocks_w * blocks_h * block_size

    @property
    def has_size_checked_format(self):
        """Whether calculate_mipmap_size() knows this pixel format's layout:
        DXT1/3/5, or uncompressed 32 bits per pixel."""
        fmt = self.pixelfmt_dwFourCC
        if fmt:
            return fmt in (b"DXT1", b"DXT3", b"DXT5")
        return bool(self.pixelfmt_dwFlags & self.DDPF_RGB) and self.pixelfmt_dwRGBBitCount == 32

    def check_mipmap_consistency(self, source_name):
        """Raise AlbamCheckFailure when the pixel data is shorter than the
        mipmap chain the header declares, which would otherwise make export
        write mipmap offsets past the end of the texture.

        Only data that is too short is rejected: extra bytes are harmless,
        and a non-power-of-two chain can be laid out with either rounding
        (see calculate_mipmap_size_halved_blocks), so the smaller of the two
        is the minimum. Volume textures and pixel formats the size math
        doesn't cover are not checked.
        """
        if self.is_volume or not self.has_size_checked_format:
            return
        w, h, fmt = self.dwWidth, self.dwHeight, self.pixelfmt_dwFourCC
        level_sizes = (
            min(self.calculate_mipmap_size(w, h, level, fmt),
                self.calculate_mipmap_size_halved_blocks(w, h, level, fmt))
            for level in range(self.dwMipMapCount)
        )
        min_size = sum(level_sizes) * self.image_count
        actual_size = len(self.data)
        if actual_size < min_size:
            raise AlbamCheckFailure(
                f"DDS image '{source_name}' has less pixel data than its header declares",
                details=(
                    f"The header declares {self.dwMipMapCount} mipmap level(s) for a {w}x{h} "
                    f"image, which needs at least {min_size} bytes of pixel data, "
                    f"but the file has {actual_size}"
                ),
                solution=(
                    "Re-save the DDS file, either with mipmaps generated or with mipmaps "
                    "turned off"
                ),
            )

    @classmethod
    def from_bl_image(cls, bl_im):
        from bpy.path import abspath

        if bl_im.packed_file:
            data = bl_im.packed_file.data
        else:
            with open(abspath(bl_im.filepath), "rb") as f:
                data = f.read()
        id_magic = data[:4]
        if not id_magic == b"DDS ":
            raise TypeError(f"Image {bl_im.name} is not a dds image. Id: {id_magic}")
        return cls.from_dds_bytes(data, bl_im.name)

    @classmethod
    def from_dds_bytes(cls, data, source_name):
        dds_header = cls()
        header_size = sizeof(dds_header)
        header_data = io.BytesIO(data[:header_size])  # FIXME unnecessary copy
        header_data.readinto(dds_header)
        dds_header._dds_data = data[header_size:]
        # A DDS without a mip chain may leave dwMipMapCount at 0 (GIMP,
        # Paint.NET and NVTT do); the base level alone still counts as one.
        dds_header.dwMipMapCount = max(1, dds_header.dwMipMapCount)
        dds_header.check_mipmap_consistency(source_name)
        return dds_header
