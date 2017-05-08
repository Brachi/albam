from base64 import b64decode
import os
from urllib.parse import urljoin

import requests


BASE = 'https://gitlab.com/api/v3/'
path = 'projects/{0}/repository/files?private_token={1}&file_path=tests/samples/re5/arc/uPl00ChrisNormal.arc&ref=master'


def download_sample_files():
    '''quick test'''
    token = os.environ['SECRET_TOKEN']
    id_ = os.environ['SECRET_ID']
    file_test_url = urljoin(BASE, path.format(id_, token))
    r = requests.get(file_test_url)
    data = r.json()
    final_dir = 'tests/sample-files/re5/arc'  # XXX import it!
    if not os.path.isdir(final_dir):
        os.makedirs(final_dir)
    try:
        final_path = os.path.join(final_dir, data['file_name'])
    except KeyError:
        raise ValueError('data does not have the file_name key: {}'.format(data))

    with open(final_path, 'wb') as w:
        w.write(b64decode(data['content']))


if __name__ == '__main__':
    download_sample_files()
