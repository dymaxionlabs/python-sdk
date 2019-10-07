from dymaxionlabs import files
from dymaxionlabs.utils import get_api_url, get_api_key, get_project_id

import json
import requests

DYM_PREDICT = '/estimators/{estimatorId}/predict/'
DYM_PREDICTED = '/estimators/{estimatorId}/predicted/'
DYM_PREDICTION_DETAIL = '/predictionjob/{predictionId}'
DYM_PROJECT_DETAIL = '/projects/{projectId}'
DYM_PROJECT_FILES = '/files/?limit=1000&project_uuid={projectId}'


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


class Estimator:
    """
    Class that represents an Estimator in DymaxionLabs API
    """
    def __init__(self, uuid):
        """Constructor

        Args:
            uuid: Estiamtor uuid
            prediction_job: related PredictionJob
        """
        self.uuid = uuid
        self.prediction_job = None

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

    @classmethod
    def all(cls):
        """Obtain all UUIDs of estimators from your project

        Returns:
            Returns an array of UUIDs
        """
        headers = {
            'Authorization': 'Api-Key {}'.format(get_api_key()),
            'Accept-Language': 'es'
        }
        url = '{url}{path}'.format(
            url=get_api_url(),
            path=DYM_PROJECT_DETAIL.format(projectId=get_project_id()))
        r = requests.get(url, headers=headers)
        return json.loads(r.text)['estimators']


class Project:
    def __init__(self):
        """Constructor

        Uses the environment variable to create the object
        """
        self.uuid = get_project_id()

    def files(self):
        """Obtain all info about the uploaded files from your project

        Returns:
            Returns a array of File objects
        """
        headers = {
            'Authorization': 'Api-Key {}'.format(get_api_key()),
            'Accept-Language': 'es'
        }
        url = '{url}{path}'.format(
            url=get_api_url(),
            path=DYM_PROJECT_FILES.format(projectId=self.uuid))
        r = requests.get(url, headers=headers)
        files = []
        for v in json.loads(r.text)['results']:
            files.append(files.File(self, v['name'], v['metadata']))
        return files
