from . import API_URL, API_KEY, PROJECT_ID

import json
import mimetypes
import requests
import os
import urllib3

TERRA_UPLOAD_FILE = '/files/upload/{file_name}?project_uuid={project_uuid}'
TERRA_DOWNLOAD_FILE = '/files/download/{file_name}?project_uuid={project_uuid}'


class File:
    def __init__(self, project, name, url, metadata):
        self.project = project
        self.name = name
        self.url = url
        self.metadata = metadata

    def download(output_dir):
        download(self.name, output_dir)


def upload(img_name):
    """Function to load a image

    Returns the detail of the object that was created in DymaxionLabs's server

    Keyword arguments:
    img_name -- image local path
    """
    if os.path.isfile(img_name) and os.access(img_name, os.R_OK):
        http = urllib3.PoolManager()
        headers = {
            'Authorization': 'Api-Key {}'.format(API_KEY),
            'Accept-Language': 'es',
            'Content-Type': mimetypes.MimeTypes().guess_type(img_name)[0]
        }
        upload_url = TERRA_UPLOAD_FILE.format(
            file_name=os.path.basename(img_name), project_uuid=PROJECT_ID)
        url = '{url}{path}'.format(url=API_URL, path=upload_url)
        with open(img_name, 'rb') as fp:
            file_data = fp.read()
        r = http.request('POST', url, body=file_data, headers=headers)
        return json.loads(r.data.decode('utf-8'))['detail']
    else:
        raise FileExistsError


def download(img_name, output_dir="."):
    """Function to download a image

    Keyword arguments:
    img_name -- image name
    output_dir -- local destination to store the image
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    headers = {
        'Authorization': 'Api-Key {}'.format(API_KEY),
        'Accept-Language': 'es'
    }
    download_url = TERRA_DOWNLOAD_FILE.format(
        file_name=os.path.basename(img_name), project_uuid=PROJECT_ID)
    url = '{url}{path}'.format(url=API_URL, path=download_url)
    r = requests.get(url, headers=headers)
    output_file = os.path.sep.join([output_dir, img_name])
    with open(output_file, 'wb') as f:
        f.write(r.content)
