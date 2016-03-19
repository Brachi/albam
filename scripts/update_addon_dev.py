#!/usr/bin/python3

import os
import shutil
import sys


def update_addon(blender_version):
    project_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    src_path = os.path.join(project_path, 'albam')
    addons_path = os.path.join(os.path.expanduser('~'), '.config/blender/{0}/scripts/addons'.format(blender_version))
    dst_path = os.path.join(addons_path, 'albam')
    if not os.path.exists(addons_path):
        raise ValueError('path {} does not exist'.format(addons_path))
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    shutil.copytree(src_path, dst_path)


if __name__ == '__main__':
    try:
        blender_version = sys.argv[1]
    except IndexError:
        blender_version = '2.76'
    update_addon(blender_version)
