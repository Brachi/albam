import os
import sys
import time

import bpy

FILES = {files}


def import_export_file(file_path):
    try:
        bpy.ops.albam_import.item(files=[{{'name': file_path}}])
    except Exception as err:
        sys.stderr.write('[ALBAM] Error Importing ' + str(err))
        sys.exit(1)

    time.sleep(0.5)
    imported_name = os.path.basename(file_path)

    try:
        bpy.context.scene.albam_item_to_export = imported_name
        bpy.ops.albam_export.item(filepath=file_path + '.exported')
    except Exception as err:
        sys.stderr.write('[ALBAM] Error Exporting ' + str(err))
        sys.exit(1)

for f in FILES:
    import_export_file(f)
