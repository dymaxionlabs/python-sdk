from .utils import request, fetch_from_list_request
from .models import Estimator
from .files import File


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
            results_files: array of strings that contains the names of results
        """
        self.id = id
        self.estimator = estimator
        self.finished = finished
        self.image_files = image_files
        self.results_files = result_files

    @classmethod
    def all(cls):
        for attrs in fetch_from_list_request('{base_path}/'.format(base_path=cls.base_path)):
            self.from_attributes(**attrs)

    @classmethod
    def from_attributes(**attrs):
        estimator = Estimator.get(attrs['estimator'])
        image_files = [File.get(name) for name in attrs['image_files']]
        results_files = [File.get(name) for name in attrs['results_files']]
        cls(**attrs, estimator=estimator, image_files=image_files, results_files)

    @classmethod
    def get(cls, id):
        attrs = request(
            'get', '{base_path}/{uuid}'.format(base_path=cls.base_path, uuid=uuid))
        return cls(**attrs)

    def is_running(self):
        if self.finished:
            return False
        self.refresh()
        return not self.finished

    def refresh(self):
        """Refresh status of a PredictionJob"""
        attrs = request('get', '{base_path}/predictionjob/{id}')
        # TODO Update the other fields
        self.finished = attrs['finished']

    def download_results(self, output_dir="."):
        """Download results from a finished PredictionJob

        Args:
            output_dir: path for storing results
        """
        if not self.is_running():
            for f in self.results_files:
                f.download(output_dir)
        else:
            raise RuntimeError("Job is still running")
