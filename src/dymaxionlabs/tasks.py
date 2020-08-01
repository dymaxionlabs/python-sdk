from .files import File
from .models import Estimator
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
    :param dict extra_attributes: extra attributes from API response

    """

    base_path = "/tasks"

    def __init__(self, *, id, state, name, args, kwargs, created_at,
                 updated_at, finished_at, metadata, duration,
                 estimated_duration, **extra_attributes):
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

    @classmethod
    def all(cls, path="*"):
        """Fetches all Tasks

        :returns: a list of :class:`Task`
        :rtype: list

        """
        """Fetches all estimators in the current project."""
        return [
            cls._from_attributes(**attrs)
            for attrs in fetch_from_list_request(f'{cls.base_path}/')
        ]

    @classmethod
    def get(cls, id):
        """Gets an task identified by ``id``."""
        attrs = request('get', f'{cls.base_path}/{id}')
        return cls._from_attributes(**attrs)

    @classmethod
    def _from_attributes(cls, **attrs):
        """Creates a Task from an ``attrs`` dictionary.

        This method also fetches related entities.

        Used internally by other class methods.

        :param dict attrs: Task attributes

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

    def refresh(self):
        """Refreshes attributes of the task.

        :returns: itself
        :rtype: Task

        """
        attrs = request('get', f'{self.base_path}/{self.id}')
        self.__dict__.update(self._from_attributes(**attrs).__dict__)
        return self

    def __repr__(self):
        return (f"<dymaxionlabs.tasks.Task id={self.id} "
                f"name=\"{self.name}\" "
                f"state=\"{self.state}\">")
