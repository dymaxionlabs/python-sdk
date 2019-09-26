from . import AUTH_TOKEN, API_URL, API_KEY
from src.terra import file

import json
import requests

TERRA_PREDICT = '/estimators/{estimatorId}/predict/'
TERRA_PREDICTED = '/estimators/{estimatorId}/predicted/'
TERRA_PREDICTION_DETAIL = '/predictionjob/{estimatorId}'


class PredictionJob:

    def __init__(self, id, estimator, finished, image_files, result_files):
        self.id = id
        self.estimator = estimator
        self.finished = finished
        self.image_files = image_files
        self.results_files = result_files

    def status(self):
        if self.finished:
            return self.finished
        else:
            headers = {'Authorization': 'Api-Key {}'.format(API_KEY), 'Accept-Language': 'es' }
            url = '{url}{path}'.format(
                url=API_URL, 
                path=TERRA_PREDICTION_DETAIL.format(
                    estimatorId=self.estimator
                )
            )
            r = requests.get(url, headers=headers)
            data = json.loads(r.text)
            if data['finished']:
                self.finished = data['finished']
                self.results_files = data['result_files']
            return data['finished']

    def download_results(self, output_dir = "."):
        if self.status():
            for f in self.results_files:
                file.download(f, output_dir)


class Estimator:

    def __init__(self, uuid):
        self.uuid = uuid
        self.prediction_job = None

    def predict(self, preload_files = [], local_files = []):
        for local_file in local_files:
            f = file.upload(local_file)
            preload_files.append(f['name'])

        data = {'files': preload_files}
        headers = {'Authorization': 'Api-Key {}'.format(API_KEY), 'Accept-Language': 'es' }
        url = '{url}{path}'.format(
            url=API_URL, 
            path=TERRA_PREDICT.format(
                estimatorId=self.uuid
            )
        )
        r = requests.post(url, json=data, headers=headers)
        data = json.loads(r.text)['detail']
        self.prediction_job = PredictionJob(
            id = data['id'],
            estimator = data['estimator'],
            finished = data['finished'],
            image_files = data['image_files'],
            result_files = data['result_files']
        )
        return self.prediction_job

