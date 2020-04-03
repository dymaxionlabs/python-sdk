from dymaxionlabs import files
from dymaxionlabs.utils import request, fetch_from_list_request

import json
import requests

DYM_PREDICT = '/estimators/{estimatorId}/predict/'
DYM_PREDICTED = '/estimators/{estimatorId}/predicted/'
DYM_PREDICTION_DETAIL = '/predictionjob/{predictionId}'


class Estimator:
    """
    The Estimator class represents a Model that can be trained to solve
    different kinds of tasks, like object detection or classification.

    """

    TYPES = dict(object_detection='OD')

    base_path = '/estimators'

    def __init__(self, *, uuid, name, classes, estimator_type, metadata, **extra_attributes):
        """Estimator constructor

        Usually created when using classmethods all(), get(), or create()

        Args:
            uuid: internal id
            name: name
            classes: list of labels/classes
            estimator_type: type of estimator (i.e. )
            metadata: user metadata
            extra_attributes: extra attributes from API
        """
        self.uuid = uuid
        self.name = name
        self.classes = classes
        self.estimator_type = estimator_type
        self.metadata = metadata
        self.extra_attributes = extra_attributes

        self.prediction_job = None

    @classmethod
    def all(cls):
        return [Estimator(**attrs) for attrs in fetch_from_list_request(cls.base_path + '/')]

    @classmethod
    def create(cls, *, name, type, classes, metadata=None):
        if type not in cls.TYPES:
            raise TypeError(
                "{} should be one of these: {}".format(type, cls.TYPES.keys()))
        params = dict(name=name,
                      estimator_type=cls.TYPES[type],
                      classes=classes,
                      metadata=metadata)
        response = request(
            'post', '{base_path}/'.format(base_path=self.base_path), params)
        return cls(**response)

    def delete(self):
        request(
            'delete', '{base_path}/{uuid}'.format(base_path=self.base_path, uuid=self.uuid))
        return True

    # FIXME
    def predict_files(self, remote_files=[], local_files=[]):
        """Predict files

        This function will start a prediction job over the specified files.
        You can predict over already upload images by providing a list of
        +remote_files+, or over images in your disk by providing a list of
        +local_files+.  Local files will be uploaded before prediction.

        Args:
            remote_files: array of string with the names of already uploaded files
            local_files: array of string with the names of local files

        Returns:
            Returns a dict with info about the new PredictionJob
        """
        for local_file in local_files:
            f = file.upload(local_file)
            remote_files.append(f['name'])

        data = {'files': remote_files}
        headers = {
            'Authorization': 'Api-Key {}'.format(get_api_key()),
            'Accept-Language': 'es'
        }
        url = '{url}{path}'.format(
            url=get_api_url(), path=DYM_PREDICT.format(estimatorId=self.uuid))
        r = requests.post(url, json=data, headers=headers)
        data = json.loads(r.text)['detail']
        self.prediction_job = PredictionJob(id=data['id'],
                                            estimator=data['estimator'],
                                            finished=data['finished'],
                                            image_files=data['image_files'],
                                            result_files=data['result_files'])
        return self.prediction_job

    def __repr__(self):
        return "<Estimator uuid={uuid!r} name={name!r}>".format(name=self.name, uuid=self.uuid)


class PredictionJob:
    """
    Class that represents a PredictionJob in DymaxionLabs API

    A PredictionJob is a background job that performs the prediction using a
    previously trained Estimator and your uploaded images.
    """

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

    def status(self):
        """Get status of a PredictionJob

        Returns:
            Returns a boolean whether the job finished or not
        """
        if self.finished:
            return self.finished
        else:
            headers = {
                'Authorization': 'Api-Key {}'.format(get_api_key()),
                'Accept-Language': 'es'
            }
            url = '{url}{path}'.format(
                url=get_api_url(),
                path=DYM_PREDICTION_DETAIL.format(predictionId=self.id))
            r = requests.get(url, headers=headers)
            data = json.loads(r.text)
            if data['finished']:
                self.finished = data['finished']
                self.results_files = data['result_files']
            return data['finished']

    def download_results(self, output_dir="."):
        """Download results from a finished PredictionJob

        Args:
            output_dir: path for storing results
        """
        if self.status():
            for f in self.results_files:
                file.download(f, output_dir)
