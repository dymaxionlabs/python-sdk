from .files import File
from .models import Estimator
from .utils import fetch_from_list_request, request


class Task:

    base_path = "/tasks"

    def __init__(self, id, name, updated_at, created_at, finished_at, state,
                 metadata, args, kwargs):
        """Task constructor

        Used to represent backend jobs

        Args:
            id: internal id
            name: name
            updated_at: updated datetime
            created_at: created datetime
            finished_at: finished datetime
            state: job state
            metadata: job metadata
            args: args
            kwargs: kwargs
        """
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
        """Creates a job class from an +attrs+ dictionary

        This method also fetches related entities.

        Used internally by other class methods
        """
        return cls(**attrs)

    def is_running(self):
        """Decides whether job is running or not and update the job attrs if is necesary"""
        if self.state == 'FINISHED' or self.state == 'FAILED':
            return False
        self.refresh()
        return not (self.state == 'FINISHED' or self.state == 'FAILED')

    def refresh(self):
        """Refresh attrs of the job"""
        attrs = request(
            'get', '{base_path}/{id}'.format(base_path=self.base_path,
                                             id=self.id))
        self.__dict__.update(self._from_attributes(attrs).__dict__)
        return self