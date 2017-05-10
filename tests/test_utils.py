import ctypes
import struct
import os

from albam.lib.structure import DynamicStructure
from albam.lib.half_float import unpack_half_float, pack_half_float
from albam.lib.misc import ensure_posixpath, ensure_ntpath


def test_base_structure(tmpdir):
    test_values = [4, 2, 1, 2, 3, 4, 0, 30, 31]  # TODO: randomize
    test_bytes = struct.pack('=IH IIII I II', *test_values)
    test_file_name = os.path.join(str(tmpdir), 'test.struct')
    with open(test_file_name, 'wb') as w:
        w.write(test_bytes)

    class MyStructure(DynamicStructure):
        _fields_ = (('arr_size', ctypes.c_uint),
                    ('foo', ctypes.c_ushort),
                    ('arr', lambda s: ctypes.c_uint * s.arr_size),
                    ('bar', ctypes.c_uint),
                    ('arr_2', lambda s: ctypes.c_uint * s.foo),
                    )
    my_struct = MyStructure(file_path=test_file_name)

    with open(test_file_name, 'rb') as f:
        f.readinto(my_struct)

    assert my_struct.arr_size == 4
    assert my_struct.foo == 2
    assert list(my_struct.arr) == [1, 2, 3, 4]
    assert my_struct.bar == 0
    assert list(my_struct.arr_2) == [30, 31]


def test_unpack_pack_half_float():
    # FIXME: Research half float and find out if these are actual limitations or
    # a bug in the function.
    # if it's not an actual limitation, raise an exception
    # https://en.wikipedia.org/wiki/Half-precision_floating-point_format
    expected_fail = 0
    for short_input in range(0, 65535):
        if (short_input in range(31745, 33792) or
                short_input in range(1, 1024) or
                short_input in range(64512, 65535)):
            expected_fail += 1
        else:
            float_output = unpack_half_float(short_input)
            short_again = pack_half_float(float_output)
            assert short_input == short_again
    assert expected_fail == 4093


def test_ensure_posixpath_from_ntpath():
    path = 'foo\\bar\\spam\\eggs'

    assert ensure_posixpath(path) == 'foo/bar/spam/eggs'


def test_ensure_posixpath_from_posixpath():
    path = 'foo/bar/spam/eggs'

    assert ensure_posixpath(path) == 'foo/bar/spam/eggs'


def test_ensure_ntpath_from_posixpath():
    path = 'foo/bar/spam/eggs'

    assert ensure_ntpath(path) == 'foo\\bar\\spam\\eggs'


def test_ensure_ntpath_from_ntpath():
    path = 'foo\\bar\\spam\\eggs'

    assert ensure_ntpath(path) == 'foo\\bar\\spam\\eggs'
