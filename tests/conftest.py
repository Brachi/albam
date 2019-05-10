import os
from pathlib import Path



SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample-files')
ALBAM_ROOT_DIR = Path(__file__).parent.parent
ALBAM_MODULE_DIR = ALBAM_ROOT_DIR / 'albam'
COVERAGERC_FILE = ALBAM_ROOT_DIR / '.coveragerc'
TEMPLATE_PATH = ALBAM_ROOT_DIR / 'tests' / 'run_albam.template.py'


def pytest_addoption(parser):
    parser.addoption('--dirarc', help='Specified a custom folder for arc files (RE5)')



def assert_same_attributes(obj1, obj2, attr, binary=False, length=False):
    attr_1 = getattr(obj1, attr)
    attr_2 = getattr(obj2, attr)
    if binary:
        attr_1 = bytes(attr_1)
        attr_2 = bytes(attr_2)
    elif length:
        attr_1 = len(attr_1)
        attr_2 = len(attr_2)

    assert attr_1 == attr_2


def assert_approximate_fields(obj1, obj2, attr_name, max_ratio):
    attr_1 = getattr(obj1, attr_name)
    attr_2 = getattr(obj2, attr_name)
    difference = abs(attr_1 - attr_2)

    try:
        ratio = difference / attr_1
    except ZeroDivisionError:
        ratio = difference

    assert ratio < max_ratio


