import json
import mimetypes
import requests
import os
import urllib3
from dymaxionlabs.utils import get_api_url, get_api_key, get_project_id

DYM_UPLOAD_FILE = '/files/upload/{file_name}?project_uuid={project_uuid}'
DYM_DOWNLOAD_FILE = '/files/download/{file_name}?project_uuid={project_uuid}'


class File:
    def __init__(self, project, name, metadata):
        """Constructor

        Keyword arguments:
        project -- related project
        name -- image's name in DymaxionLabs's server
        metada -- image metada
        """
        self.project = project
        self.name = name
        self.metadata = metadata

    def download(output_dir):
        """Function to download the image

        Keyword arguments:
        output_dir -- local destination to store the image
        """
        download(self.name, output_dir)

    def __repr__(self):
        return "<dymaxionlabs.file.File name=\"{name}\"".format(name=self.name)


def upload(img_name):
    """Function to load a image

    Returns the detail of the object that was created in DymaxionLabs's server

    Keyword arguments:
    img_name -- image local path
    """
    if os.path.isfile(img_name) and os.access(img_name, os.R_OK):
        http = urllib3.PoolManager()
        headers = {
            'Authorization': 'Api-Key {}'.format(get_api_key()),
            'Accept-Language': 'es',
            'Content-Type': mimetypes.MimeTypes().guess_type(img_name)[0]
        }
        upload_url = DYM_UPLOAD_FILE.format(
            file_name=os.path.basename(img_name),
            project_uuid=get_project_id())
        url = '{url}{path}'.format(url=get_api_url(), path=upload_url)
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
        'Authorization': 'Api-Key {}'.format(get_api_key()),
        'Accept-Language': 'es'
    }
    download_url = DYM_DOWNLOAD_FILE.format(
        file_name=os.path.basename(img_name), project_uuid=get_project_id())
    url = '{url}{path}'.format(url=get_api_url(), path=download_url)
    r = requests.get(url, headers=headers)
    output_file = os.path.sep.join([output_dir, img_name])
    with open(output_file, 'wb') as f:
        f.write(r.content)
