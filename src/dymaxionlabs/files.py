import mimetypes
import io
import os
import requests

from .utils import fetch_from_list_request, request
from .upload import CustomResumableUpload

MIN_SIZE_RESUMABLE_UPLOAD = 1024 * 1024  #1MB
DEFAULT_CHUNK_SIZE = 1024 * 1024  #1MB


class File:
    base_path = '/storage'

    def __init__(self, name, path, metadata, **extra_attributes):
        """The File class represents files stored in Dymaxion Labs.

        Files are owned by the authenticated user.

        Args:
            name: file name
            path: file path
            metadata: file metadata
            extra_attributes: extra attributes from API endpoint

        """
        self.name = name
        self.path = path
        self.metadata = metadata
        self.tiling_job = None
        self.extra_attributes = extra_attributes

    @classmethod
    def all(cls, path="*"):
        """Get all File in +path+"""
        response = request(
            'get', '/storage/files/?path={path}'.format(
                path=requests.utils.quote(path)))
        return [File(**attrs) for attrs in response]

    @classmethod
    def get(cls, path):
        """Get a specific File in +path+"""
        attrs = request(
            'get', '{base_path}/file/?path={path}'.format(
                base_path=cls.base_path, path=requests.utils.quote(path)))
        return File(**attrs['detail'])

    def delete(self):
        """Delete file"""
        request(
            'delete',
            '{base_path}/file/?path={path}'.format(base_path=self.base_path,
                                                   path=requests.utils.quote(
                                                       self.path)))
        return True

    @classmethod
    def _resumable_url(cls, storage_path, size):
        url_path = '{base_path}/create-resumable-upload/?path={path}&size={size}'.format(
            base_path=cls.base_path,
            path=requests.utils.quote(storage_path),
            size=size)
        response = request('post', url_path)
        return response

    @classmethod
    def _resumable_upload(cls, input_path, storage_path, chunk_size):
        chunk_size = DEFAULT_CHUNK_SIZE if chunk_size is None else DEFAULT_CHUNK_SIZE * chunk_size
        total_size = os.path.getsize(input_path)
        f = open(input_path, "rb")
        stream = io.BytesIO(f.read())
        metadata = {u'name': os.path.basename(input_path)}
        res = cls._resumable_url(storage_path, os.path.getsize(input_path))
        upload = CustomResumableUpload(res['session_url'], chunk_size)
        upload.initiate(
            stream,
            metadata,
            mimetypes.MimeTypes().guess_type(input_path)[0],
            res['session_url'],
        )
        print("Uploaded 0 %", end='\r', flush=True)
        while (not upload.finished):
            upload.transmit_next_chunk()
            print("Uploaded {} %".format(
                int(upload.bytes_uploaded * 100 / total_size)),
                  end='\r',
                  flush=True)
        print("")
        return cls.get(storage_path)

    @classmethod
    def _upload(cls, input_path, storage_path):
        print("Uploaded 0 %", end='\r', flush=True)
        filename = os.path.basename(input_path)
        with open(input_path, 'rb') as fp:
            data = fp.read()
        path = '{base_path}/upload/'.format(base_path=cls.base_path)
        response = request(
            'post',
            path,
            body={'path': storage_path},
            files={'file': data},
        )
        print("Uploaded 100 %")
        return File(**response['detail'])

    @classmethod
    def upload(cls, input_path, storage_path="", chunk_size=None):
        """Upload a file to storage

        Args:
            input_path -- path to local file
            storage_path -- destination path
            chunk_size -- size [MB] of chunks for resumable uploading

        Raises:
            FileNotFoundError: Path
        """
        print("Uploading {}...".format(os.path.basename(input_path)))
        if storage_path.strip() == "" or list(storage_path).pop() == "/":
            storage_path = "".join(
                [storage_path, os.path.basename(input_path)])
        if (os.path.getsize(input_path) > MIN_SIZE_RESUMABLE_UPLOAD):
            file = cls._resumable_upload(input_path, storage_path, chunk_size)
        else:
            file = cls._upload(input_path, storage_path)
        return file

    def download(self, output_dir="."):
        """Download file and save it to +output_dir+

        If +output_dir+ does not exist, it will be created.

        Args:
            output_dir: path to store file
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        path = '{base_path}/download/?path={path}'.format(
            base_path=self.base_path, path=requests.utils.quote(self.path))
        content = request('get', path, binary=True, parse_response=False)
        output_file = os.path.join(output_dir, self.name)
        with open(output_file, 'wb') as f:
            f.write(content)

    def tiling(self, output_path, tile_size=500):
        """Tiling

        This function will start a tiling job over the specified file.
        You can set the +tile_size+ that you want for the output tiles and
        the +output_path+ for the path where the tiles will be storage

        Args:
            output_path: storage folder
            tile_size: tile size

        Returns:
            Returns a Task with info about the new tailing job
        """
        if not output_path:
            raise RuntimeError("Output path can not be null")
        from .tasks import Task
        response = request('post',
                           '/estimators/start_tiling_job/',
                           body={
                               'path': self.path,
                               'output_path': output_path,
                               'tile_size': tile_size,
                           })
        self.tiling_job = Task._from_attributes(response['detail'])
        return self.tiling_job

    def __repr__(self):
        return "<File name={name!r}".format(name=self.name)
