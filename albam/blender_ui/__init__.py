from .import_panel import (
    ALBAM_UL_FileList,
    ALBAM_PT_FileExplorer,
    ALBAM_PT_ImportSection,
    ALBAM_PT_ImportButton,
    ALBAM_OT_Import,
    ALBAM_OT_AddFiles,
    ALBAM_OT_FileItemCollapseToggle,
)
from .export_panel import ALBAM_UL_ExportableObjects, ALBAM_PT_Export


# Order is important
CLASSES_TO_REGISTER = (
    ALBAM_OT_Import,
    ALBAM_OT_AddFiles,
    ALBAM_OT_FileItemCollapseToggle,
    ALBAM_UL_ExportableObjects,
    ALBAM_UL_FileList,
    ALBAM_PT_ImportSection,
    ALBAM_PT_FileExplorer,
    ALBAM_PT_ImportButton,
    ALBAM_PT_Export,
)
