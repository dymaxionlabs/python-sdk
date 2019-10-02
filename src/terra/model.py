from . import AUTH_TOKEN, API_URL, API_KEY
from src.terra import file

import json
import requests

TERRA_PREDICT = '/estimators/{estimatorId}/predict/'
TERRA_PREDICTED = '/estimators/{estimatorId}/predicted/'
TERRA_PREDICTION_DETAIL = '/predictionjob/{estimatorId}'


class PredictionJob:
    """
    Class that represent a PredictionJob in DymaxionLabs's server

    A PredictionJob is a job that can detect object in your 
    images with a model trained previously
    """
    def __init__(self, id, estimator, finished, image_files, result_files):
        """Constructor

        Keyword arguments:
        id -- PredictionJob pk in Dymaxionlabs's server
        estimator -- related estimator
        finished -- PredictionJob's state
        image_files -- array of strings that contains the names of image to predict
        results_files -- array of strings that contains the names of results
        """
        self.id = id
        self.estimator = estimator
        self.finished = finished
        self.image_files = image_files
        self.results_files = result_files

    def status(self):
        """Function to know the PredictionJob's status

        If the object's status is false requests updated information to DymaxionLabs's server
        for actualize it

        Returns a boolean that represents the status
        """
        if self.finished:
            return self.finished
        else:
            headers = {
                'Authorization': 'Api-Key {}'.format(API_KEY),
                'Accept-Language': 'es'
            }
            url = '{url}{path}'.format(url=API_URL,
                                       path=TERRA_PREDICTION_DETAIL.format(
                                           estimatorId=self.estimator))
            r = requests.get(url, headers=headers)
            data = json.loads(r.text)
            if data['finished']:
                self.finished = data['finished']
                self.results_files = data['result_files']
            return data['finished']

    def download_results(self, output_dir="."):
        """Function to download the PredictionJob's results

        Downloads all the results in the destination that was provides

        Keyword arguments:
        output_dir -- local destination to store the image
        """
        if self.status():
            for f in self.results_files:
                file.download(f, output_dir)


class Estimator:
    """
    Class that represent a Estimator in DymaxionLabs's server
    """
    def __init__(self, uuid):
        """Constructor

        Keyword arguments:
        uuid -- Estiamtor uuid in Dymaxionlabs's server
        prediction_job -- related PredictionJob
        """
        self.uuid = uuid
        self.prediction_job = None

    def predict(self, preload_files=[], local_files=[]):
        """Funcionality to predict files

        This funcionality will use a trained model to detect object in the files that you provides
        The local files will be uploaded before to predict

        Returns info about the PredictionJob started

        Keyword arguments:
        preload_files -- array of string with the names of files that was already loaded in DymaxionLabs's server
        local_files -- array of string with the names of local files
        """
        for local_file in local_files:
            f = file.upload(local_file)
            preload_files.append(f['name'])

        data = {'files': preload_files}
        headers = {
            'Authorization': 'Api-Key {}'.format(API_KEY),
            'Accept-Language': 'es'
        }
        url = '{url}{path}'.format(
            url=API_URL, path=TERRA_PREDICT.format(estimatorId=self.uuid))
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
        """Funcionality to obtain all uuid of estimators related to your project
        
        Returns a array with the uuid
        """
        headers = {
            'Authorization': 'Api-Key {}'.format(API_KEY),
            'Accept-Language': 'es'
        }
        url = '{url}{path}'.format(
            url=API_URL,
            path=TERRA_PROJECT_DETAIL.format(projectId=PROJECT_ID))
        r = requests.get(url, headers=headers)
        return json.loads(r.text)['estimators']


class Project:
    #Class that represent a Project in DymaxionLabs's server

    def __init__(self):
        """Constructor

        Uses the enviroment variable to create the object
        """
        self.uuid = PROJECT_ID

    def files(self):
        """Funcionality to obtain all info about the uploaded files related to your project 

        Returns a array of File objects
        """
        headers = {
            'Authorization': 'Api-Key {}'.format(API_KEY),
            'Accept-Language': 'es'
        }
        url = '{url}{path}'.format(
            url=API_URL, path=TERRA_PROJECT_FILES.format(projectId=self.uuid))
        r = requests.get(url, headers=headers)
        files = []
        for v in json.loads(r.text)['results']:
            files.append(File(self, v['name'], v['metadata']))
        return files
