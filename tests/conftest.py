import os

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')


def pytest_addoption(parser):
    parser.addoption('--dirtex', help='Specified a custom folder for tex files (Re5)')
    parser.addoption('--dirarc', help='Specified a custom folder for arc files (Re5)')
    parser.addoption('--arcregex', help='Regex that will be applied while searching for arc files')
    parser.addoption('--blender', help='Path to Blender executable for performing functional tests')
