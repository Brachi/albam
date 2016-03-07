import csv
import os

import pytest


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')


def pytest_addoption(parser):
    parser.addoption('--dirmod', help='Specified a custom folder for mod files (Re5)')
    parser.addoption('--dirtex', help='Specified a custom folder for tex files (Re5)')
    parser.addoption('--dirarc', help='Specified a custom folder for arc files (Re5)')
    parser.addoption('--blender', help='Path to Blender executable for performing functional tests')
