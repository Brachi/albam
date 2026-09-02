"""Animation support for MT Framework's .lmt.

Four jobs kept apart: the keyframe codec, reading a file in, writing one back
out, and the custom properties that carry an .lmt through a .blend between the
two. Importing the submodules is what runs their registry decorators, so it has
to happen even though nothing here calls into them.

Order matters: registration order is meaningful for property dependencies, and
ui's ImportOptionsLMT registered before properties' classes when all of this
was one file.
"""
from .keyframes import (  # noqa: F401  re-exported for callers of this package
    APPID_VERSION_MAPPER,
    LMTKeyFrames,
    LMTKeyframeBounds,
    USAGE,
    to_signed_32,
    to_unsigned_32,
)
from . import animation_import  # noqa: F401  registers the import side
from . import ui  # noqa: F401  registers the import panel's options
from . import properties  # noqa: F401  registers the custom property groups
from . import animation_export  # noqa: F401  registers the export side
from .animation_import import (  # noqa: F401  re-exported
    CHAIN_LENGTH_PROP,
    CHAIN_TARGET_PROP,
    ROOT_MOTION_BONE_NAME,
    get_block_index,
)
from .animation_export import _lmt_blocks  # noqa: F401  re-exported
