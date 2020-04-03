import json
import mimetypes
import requests
import os
import urllib3
from dymaxionlabs.utils import get_api_url, get_api_key

DYM_UPLOAD_FILE = '/files/upload/{file_name}?project_uuid={project_uuid}'
DYM_DOWNLOAD_FILE = '/files/download/{file_name}?project_uuid={project_uuid}'


class File:
    def __init__(self, project, name, metadata):
        """Constructor

        Args:
            project: related project
            name: image's name in DymaxionLabs's server
            metada: image metada
        """
        self.project = project
        self.name = name
        self.metadata = metadata

    def download(output_dir):
        """Download file and save it to +output_dir+

        If the directory does not exist it will be created.

        Args:
            output_dir: path to store file
        """
        download(self.name, output_dir)

    def __repr__(self):
        return "<dymaxionlabs.file.File name=\"{name}\"".format(name=self.name)


def upload(filename):
    """Upload a file named +filename+

    Args:
        filename -- path to local file

    Returns:
        Returns the detail of the object that was created in DymaxionLabs's server

    Raises:
        FileExistsError: The filename argument does not correspond to an existing file
    """
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        http = urllib3.PoolManager()
        headers = {
            'Authorization': 'Api-Key {}'.format(get_api_key()),
            'Accept-Language': 'es',
            'Content-Type': mimetypes.MimeTypes().guess_type(filename)[0]
        }
        upload_url = DYM_UPLOAD_FILE.format(
            file_name=os.path.basename(filename),
            project_uuid=get_project_id())
        url = '{url}{path}'.format(url=get_api_url(), path=upload_url)
        with open(filename, 'rb') as fp:
            file_data = fp.read()
        r = http.request('POST', url, body=file_data, headers=headers)
        return json.loads(r.data.decode('utf-8'))['detail']
    else:
        raise FileExistsError


def download(filename, output_dir="."):
    """Download a file named +filename+ to +output_dir+

    If the output directory does not exist it will be created.

    Args:
        filename: image name
        output_dir: local destination to store the image
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    headers = {
        'Authorization': 'Api-Key {}'.format(get_api_key()),
        'Accept-Language': 'es'
    }
    download_url = DYM_DOWNLOAD_FILE.format(
        file_name=os.path.basename(filename), project_uuid=get_project_id())
    url = '{url}{path}'.format(url=get_api_url(), path=download_url)
    r = requests.get(url, headers=headers)
    output_file = os.path.sep.join([output_dir, filename])
    with open(output_file, 'wb') as f:
        f.write(r.content)
