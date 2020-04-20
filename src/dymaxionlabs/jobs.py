from .files import File
from .models import Estimator
from .utils import fetch_from_list_request, request


class TrainingJob:
    """
    Class that represents a TrainingJob in DymaxionLabs API

    A TrainingJob is a background job that crates a model using a
    previously loaded files and annotation realted to a Estimator.
    """

    base_path = '/estimators'

    def __init__(self, id, estimator, finished, updated_at, created_at,
                 metadata):
        """Constructor

        Args:
            id: PredictionJob id
            estimator: related estimator instance
            finished: TrainingJob's state
        """
        self.id = id
        self.updated_at = updated_at
        self.created_at = created_at
        self.estimator = estimator
        self.finished = finished
        self.metadata = metadata

    @classmethod
    def _from_attributes(cls, attrs):
        """Creates a job class from an +attrs+ dictionary

        This method also fetches related entities.

        Used internally by other class methods
        """
        attrs['estimator'] = Estimator.get(attrs['estimator'])
        return cls(**attrs)

    def is_running(self):
        """Decides whether job is running or not"""
        if self.finished:
            return False
        self.refresh()
        return not self.finished

    def refresh(self):
        """Refresh status of the job"""
        attrs = request(
            'get',
            '{base_path}/{uuid}/finished/'.format(base_path=self.base_path,
                                                  uuid=self.estimator.uuid))
        self.finished = attrs['detail']


class PredictionJob:
    """
    Class that represents a PredictionJob in DymaxionLabs API

    A PredictionJob is a background job that performs the prediction using a
    previously trained Estimator and your uploaded images.
    """

    base_path = '/predictionjob'

    def __init__(self, id, estimator, finished, image_files, result_files):
        """Constructor

        Args:
            id: PredictionJob id
            estimator: related estimator instance
            finished: PredictionJob's state
            image_files: array of strings that contains the names of image to predict
            result_files: array of strings that contains the names of results
        """
        self.id = id
        self.estimator = estimator
        self.finished = finished
        self.image_files = image_files
        self.result_files = result_files

    @classmethod
    def all(cls):
        """Fetches all jobs"""
        for attrs in fetch_from_list_request(
                '{base_path}/'.format(base_path=cls.base_path)):
            cls._from_attributes(**attrs)

    @classmethod
    def get(cls, id):
        """Get a job by id"""
        attrs = request(
            'get', '{base_path}/{id}'.format(base_path=cls.base_path, id=id))
        return cls._from_attributes(**attrs)

    @classmethod
    def _from_attributes(cls, attrs):
        """Creates a job class from an +attrs+ dictionary

        This method also fetches related entities.

        Used internally by other class methods
        """
        attrs['estimator'] = Estimator.get(attrs['estimator'])
        attrs['image_files'] = [
            File.get(name) for name in attrs['image_files']
        ]
        attrs['result_files'] = [
            File.get(name) for name in attrs['result_files']
        ]
        return cls(**attrs)

    def is_running(self):
        """Decides whether job is running or not"""
        if self.finished:
            return False
        self.refresh()
        return not self.finished

    def refresh(self):
        """Refresh status of the job"""
        attrs = request('get', '{base_path}/predictionjob/{id}')
        # TODO Update the other fields
        self.finished = attrs['finished']

    def download_results(self, output_dir="."):
        """Download results from a finished job

        Args:
            output_dir: path for storing results
        """
        if not self.is_running():
            for f in self.results_files:
                f.download(output_dir)
        else:
            raise RuntimeError("Job is still running")
