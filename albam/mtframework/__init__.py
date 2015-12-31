from albam.mtframework.arc import Arc
from albam.mtframework.mod import Mod156
from albam.mtframework.tex import Tex112
from albam.mtframework.mappers import FILE_ID_TO_EXTENSION, EXTENSION_TO_FILE_ID


__all__ = ('Arc', 'Mod156', 'Tex112', 'FILE_ID_TO_EXTENSION', 'EXTENSION_TO_FILE_ID')

# Not an arc file (s101.arc) and empty data/files_count
KNOWN_ARC_FAILS = ('s101.arc', 'uOmf303.arc', 'uOmS103ScrAdj.arc')

# segfaults and what not, not caught by the building mesh process
KNOWN_ARC_BLENDER_CRASH = (
    'ev108_10.arc',
    'ev612_00.arc',
    's109.arc',
    's119.arc',
    's300.arc',
    's301.arc',
    's305.arc',
    's311.arc',
    's312.arc',
    's315.arc',
    's404.arc',
    's702.arc',
    'uOm09882.arc',
)

# Memory corruptions, hangs blender and pytest
KNOWN_ARC_BLENDER_HANGS = (
    'ev204_00.arc',
    'ev606_00.arc',
    'ev613_00.arc',
    'ev614_00.arc',
    'ev615_00.arc',
    'ev616_00.arc',
    'ev617_00.arc',
    'ev618_00.arc',
    's302.arc',
    's303.arc',
    's304.arc',
    's310.arc',
    's403.arc',
    's600.arc',
    's706.arc'
)
