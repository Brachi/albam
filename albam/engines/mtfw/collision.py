from ctypes import Structure, c_ulonglong
import io
import struct

import bpy
from kaitaistruct import KaitaiStream
from mathutils import Matrix

from albam.registry import blender_registry
from .structs.sbc_156 import Sbc156
from .structs.sbc_21 import Sbc21

SBC_CLASS_MAPPER = {
    49: Sbc156,
    255: Sbc21,
}


@blender_registry.register_import_function(app_id="re0", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="re1", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="re5", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="re6", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="rev1", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="rev2", extension='sbc', file_category="COLLISION")
@blender_registry.register_import_function(app_id="dd", extension='sbc', file_category="COLLISION")
def load_sbc(file_item, context):
    sbc_bytes = file_item.get_bytes()
    sbc_version = sbc_bytes[3]
    assert sbc_version in SBC_CLASS_MAPPER, f"Unsupported version: {sbc_version}"
    SBCCls = SBC_CLASS_MAPPER[sbc_version]
    sbc = SBCCls.from_bytes(sbc_bytes)
    sbc._read()
    print(sbc_version)
