import io
import mimetypes
import os

from tqdm import tqdm

from .upload import CustomResumableUpload
from .utils import fetch_from_list_request, request, NotFoundError

MIN_SIZE_RESUMABLE_UPLOAD = 2**20  # 1MB
DEFAULT_CHUNK_SIZE = 2**20  # 1MB


class File:
    """
    The File class represents files stored in Dymaxion Labs.

    Files are owned by the authenticated user.

    :param str name: file name
    :param str path: file path in storage
    :param dict metadata: file metadata
    :param dict extra_attributes: extra attributes from API endpoint

    """

    base_path = '/storage'

    def __init__(self, name, path, metadata, **extra_attributes):
        self.name = name
        self.path = path
        self.metadata = metadata
        self.tiling_job = None
        self.extra_attributes = extra_attributes

    @classmethod
    def all(cls, path=""):
        """Fetches all files found in ``path``.

        Glob patterns are allowed, to search recursively in directories::

            File.all("foo/b*/images/*.tif")
            #=> [<dymaxionlabs.file.File name="foo/bar/images/01.tif">, ...]

        :param str path: path glob pattern (default: "")
        :returns: a list of :class:`File` of files found in path
        :rtype: list

        """
        response = request('get',
                           f'{cls.base_path}/files/',
                           params=dict(path=path))
        if response:
            return [File(**attrs) for attrs in response]
        else:
            return []

    @classmethod
    def get(cls, path, raise_error=True):
        """Gets a specific file in ``path``.

        :param str path: file path
        :param bool raise_error: If False, do not raise NotFoundError if file not found
        :rtype: File

        """
        attrs = None
        try:
            attrs = request('get',
                            f'{cls.base_path}/file/',
                            params=dict(path=path))
            return File(**attrs['detail'])
        except NotFoundError as err:
            if not raise_error:
                return
            raise err

    @classmethod
    def _check_completed_file(cls, path):
        return request('post',
                       f'{cls.base_path}/check-completed-file/',
                       params=dict(path=path))

    @classmethod
    def _resumable_url(cls, storage_path, size):
        return request('post',
                       f'{cls.base_path}/create-resumable-upload/',
                       params=dict(path=storage_path, size=size))

    @classmethod
    def _resumable_upload(cls, input_path, storage_path, chunk_size):
        chunk_size = DEFAULT_CHUNK_SIZE if chunk_size is None else DEFAULT_CHUNK_SIZE * chunk_size
        total_size = os.path.getsize(input_path)
        with open(input_path, "rb") as f:
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
        with tqdm(total=total_size,
                  unit_scale=True,
                  unit='B',
                  unit_divisor=1024) as pbar:
            while not upload.finished:
                upload.transmit_next_chunk()
                pbar.update(chunk_size)
        cls._check_completed_file(storage_path)
        return cls.get(storage_path)

    @classmethod
    def _upload(cls, input_path, storage_path):
        with open(input_path, 'rb') as fp:
            data = fp.read()
        response = request(
            'post',
            f'{cls.base_path}/upload/',
            body=dict(path=storage_path),
            files=dict(file=data),
        )
        return File(**response['detail'])

    @classmethod
    def upload(cls, input_path, storage_path="", chunk_size=None):
        """Uploads a file to storage

        :param str input_path: path of local file to upload
        :param str storage_path: destination path in storage
        :param int chunk_size: size (in MB) of chunks for resumable uploading
        :raises: FileNotFoundError
        :returns: uploaded file
        :rtype: File

        """
        if storage_path.strip() == "" or list(storage_path).pop() == "/":
            storage_path = "".join(
                [storage_path, os.path.basename(input_path)])
        if (os.path.getsize(input_path) > MIN_SIZE_RESUMABLE_UPLOAD):
            file = cls._resumable_upload(input_path, storage_path, chunk_size)
        else:
            file = cls._upload(input_path, storage_path)
        return file

    def delete(self):
        """Deletes the file in storage.

        :returns: ``True`` if file was succesfully deleted
        :rtype: bool

        """
        request('delete',
                f'{self.base_path}/file/',
                params=dict(path=self.path))
        return True

    def download(self, output_dir="."):
        """Downloads the file and stores it on ``output_dir``.

        If ``output_dir`` does not exist, it will be created.

        :param str output_dir: directory path where file will be stored

        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        content = request('get',
                          f'{self.base_path}/download/',
                          params=dict(path=self.path),
                          binary=True,
                          parse_response=False)
        output_file = os.path.join(output_dir, self.name)
        with open(output_file, 'wb') as f:
            f.write(content)

    def tiling(self, output_path, tile_size=500):
        """Starts an image tiling job on the current file.

        By default, tiles are 500x500, but you can set the ``tile_size`` to a
        different size.

        ``output_path`` should be a directory path in storage where tiles
        will be generated.

        :param str output_path: tiles output directory
        :param int tile_size: tile size (default: 500)
        :returns: a Task with info about the new tiling job
        :raises: RuntimeError if output path is None
        :rtype: Task

        """
        if not output_path:
            raise RuntimeError("Output path can not be null")
        from .tasks import Task
        body = dict(path=self.path,
                    output_path=output_path,
                    tile_size=tile_size)
        response = request('post', '/estimators/start_tiling_job/', body=body)
        self.tiling_job = Task._from_attributes(**response['detail'])
        return self.tiling_job

    def __repr__(self):
        return f"<dymaxionlabs.files.File path=\"{self.path}\">"
