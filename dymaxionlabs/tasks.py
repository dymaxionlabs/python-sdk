import os
import time

from .utils import fetch_from_list_request, request


class Task:
    """A Task represents a long running job.

    Currently, Tasks are used to query about the status of a model training
    or prediction job (see :meth:`Estimator.train` and
    :meth:`Estimator.predict_files`), or an image tiling process (see
    :meth:`File.tiling`).

    :param int id: internal id
    :param str state: job state
    :param str name: task name
    :param list args: args
    :param dict kwargs: kwargs
    :param datetime created_at: created datetime
    :param datetime updated_at: updated datetime
    :param datetime finished_at: finished datetime
    :param dict metadata: job metadata
    :param int duration: duration (in seconds)
    :param int estimated_duration: estimated duration (in seconds)
    :param str error: latest error message (if task failed)
    :param dict extra_attributes: extra attributes from API response

    """

    base_path = "/tasks"

    def __init__(self, *, id, state, name, args, kwargs, created_at,
                 updated_at, finished_at, metadata, duration,
                 estimated_duration, error, **extra_attributes):
        self.id = id
        self.state = state
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.created_at = created_at
        self.updated_at = updated_at
        self.finished_at = finished_at
        self.metadata = metadata
        self.duration = duration
        self.estimated_duration = estimated_duration
        self.error = error

    @classmethod
    def all(cls, path="*"):
        """Fetches all tasks.

        :returns: a list of :class:`Task`
        :rtype: list

        """
        return [
            cls._from_attributes(**attrs)
            for attrs in fetch_from_list_request(f'{cls.base_path}/')
        ]

    @classmethod
    def get(cls, id):
        """Gets an task identified by ``id``.

        :param id int: Task id
        :returns: the specified :class:`Task` instance
        :rtype: Task

        """
        attrs = request('get', f'{cls.base_path}/{id}/')
        return cls._from_attributes(**attrs)

    @classmethod
    def _from_attributes(cls, **attrs):
        """Creates a Task from an ``attrs`` dictionary.

        This method also fetches related entities.

        Used internally by other class methods.

        :param dict attrs: Task attributes
        :rtype: Task

        """
        return cls(**attrs)

    def is_running(self):
        """Decides whether a task is running or not, and update the task
        attributes if is necesary.

        :rtype: bool

        """
        stopped_states = ('FINISHED', 'FAILED', 'CANCELED')
        if self.state in stopped_states:
            return False
        self.refresh()
        return self.state not in stopped_states

    def wait_until_finished(self, interval: float = 5, timeout: float = 60 * 60):
        timeout_start = time.time()
        is_valid = time.time() < timeout_start + timeout
        while self.is_running() and is_valid:
            time.sleep(interval)

    def has_artifacts(self):
        """Checks if completed task has generated output artifacts.

        :returns: True if it has output artifacts, False if not.
        :rtype: bool

        """
        files = self.list_artifacts()
        return len(files) > 0

    def list_artifacts(self):
        """Returns a list of the generated output artifacts.

        :returns: list of file paths (strings)
        :rtpe: list

        """
        response = request('get',
                           f'{self.base_path}/{self.id}/list-artifacts/')
        return response['files']

    def download_artifacts(self, output_dir="."):
        """Downloads output artifacts in a compressed Zip file,
        and stores it on ``output_dir``.

        If ``output_dir`` does not exist, it will be created.

        :param str output_dir: directory path where file will be stored
        :returns: path to the artifacts zip file
        :rtype: str

        """
        os.makedirs(output_dir, exist_ok=True)
        content = request('get',
                          f'{self.base_path}/{self.id}/download-artifacts/',
                          binary=True,
                          parse_response=False)
        output_file = os.path.join(output_dir, f'artifacts_{self.id}.zip')
        with open(output_file, 'wb') as f:
            f.write(content)
        return output_file

    def export_artifacts(self, storage_dir):
        """Stores output artifacts in ``storage_dir``.

        :param str storage_dir: directory path where file will be stored
        """
        if not storage_dir:
            raise RuntimeError("``storage_dir`` directories can not be null")
        response = request('post',
                           f'{self.base_path}/{self.id}/export-artifacts/',
                           body=dict(path=storage_dir))
        return response

    def refresh(self):
        """Refreshes attributes of the task.

        :returns: itself
        :rtype: Task

        """
        attrs = request('get', f'{self.base_path}/{self.id}/')
        self.__dict__.update(self._from_attributes(**attrs).__dict__)
        return self

    def cancel(self):
        """Cancel the task if it is possible.

        :returns: itself
        :rtype: Task
        """
        response = request('post', f'{self.base_path}/{self.id}/cancel/')
        return self.refresh()

    def __repr__(self):
        return (f"<dymaxionlabs.tasks.Task id={self.id} "
                f"name=\"{self.name}\" "
                f"state=\"{self.state}\">")
