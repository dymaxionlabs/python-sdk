import mimetypes
import os

from dymaxionlabs.utils import fetch_from_list_request, request


class File:
    base_path = '/files'

    def __init__(self, name, metadata, **extra_attributes):
        """The File class represents files stored in Dymaxion Labs.

        Files are owned by the authenticated user.

        Args:
            name: file name
            metadata: file metadata
            extra_attributes: extra attributes from API endpoint

        """
        self.name = name
        self.metadata = metadata
        self.extra_attributes = extra_attributes

    @classmethod
    def all(cls):
        return [File(**attrs) for attrs in fetch_from_list_request(cls.base_path + '/')]

    @classmethod
    def get(cls, name):
        attrs = request(
            'get', '{base_path}/{name}'.format(base_path=cls.base_path, name=name))
        return File(**attrs)

    def delete(self):
        request(
            'delete', '{base_path}/{name}'.format(base_path=self.base_path,
                                                  name=self.name))
        return True

    @classmethod
    def upload(cls, input_path):
        """Upload a file to storage

        Args:
            filename -- path to local file

        Raises:
            FileNotFoundError: Path
        """
        filename = os.path.basename(input_path)
        with open(input_path, 'rb') as fp:
            data = fp.read()
        path = '{base_path}/upload/{filename}'.format(
            base_path=cls.base_path, filename=filename)
        response = request('post', path, headers={
            'Content-Type': mimetypes.MimeTypes().guess_type(filename)[0]
        }, body=data, binary=True)
        return response

    def download(self, output_dir="."):
        """Download file and save it to +output_dir+

        If +output_dir+ does not exist, it will be created.

        Args:
            output_dir: path to store file
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        path = '{base_path}/download/{name}'.format(
            base_path=self.base_path,
            name=self.name)
        content = request('get', path, binary=True, parse_response=False)
        output_file = os.path.join(output_dir, self.name)
        with open(output_file, 'wb') as f:
            f.write(content)

    def __repr__(self):
        return "<File name={name!r}".format(name=self.name)
