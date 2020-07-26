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
    :param str name: task name
    :param datetime updated_at: updated datetime
    :param datetime created_at: created datetime
    :param datetime finished_at: finished datetime
    :param str state: job state
    :param dict metadata: job metadata
    :param str args: args
    :param str kwargs: kwargs
    """

    base_path = "/tasks"

    def __init__(self, id, name, updated_at, created_at, finished_at, state,
                 metadata, args, kwargs):
        self.id = id
        self.name = name
        self.updated_at = updated_at
        self.created_at = created_at
        self.finished_at = finished_at
        self.state = state
        self.metadata = metadata
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def _from_attributes(cls, attrs):
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
        if self.state == 'FINISHED' or self.state == 'FAILED':
            return False
        self.refresh()
        return not (self.state == 'FINISHED' or self.state == 'FAILED')

    def refresh(self):
        """Refreshes attributes of the task.

        :returns: itself
        :rtype: Task

        """
        attrs = request(
            'get', '{base_path}/{id}'.format(base_path=self.base_path,
                                             id=self.id))
        self.__dict__.update(self._from_attributes(attrs).__dict__)
        return self
