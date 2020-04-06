import json

import requests

from .utils import fetch_from_list_request, request

DYM_PREDICT = '/estimators/{estimatorId}/predict/'


class Estimator:
    """
    The Estimator class represents a Model that can be trained to solve
    different kinds of tasks, like object detection or classification.

    """

    TYPES = dict(object_detection='OD')

    base_path = '/estimators'

    def __init__(self, *, uuid, name, classes, estimator_type, metadata, **extra_attributes):
        """Estimator constructor

        Usually created when using other classmethods: all(), get(), or create()

        Args:
            uuid: internal id
            name: name
            classes: list of labels/classes
            estimator_type: type of estimator (i.e. )
            metadata: user metadata
            extra_attributes: extra attributes from API endpoint
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
        """Fetch all estimators"""
        return [cls(**attrs)
                for attrs
                in fetch_from_list_request('{base_path}/'.format(base_path=cls.base_path))]

    @classmethod
    def get(cls, uuid):
        """Get estimator with +uuid+"""
        attrs = request(
            'get', '{base_path}/{uuid}'.format(base_path=cls.base_path, uuid=uuid))
        return Estimator(**attrs)

    @classmethod
    def create(cls, *, name, type, classes, metadata=None):
        """Creates a new Estimator named +name+ of +type+ with +classes+ as labels

        A metadata dictionary can be added via the +metadata+ parameter
        """
        if type not in cls.TYPES:
            raise TypeError(
                "{} should be one of these: {}".format(type, cls.TYPES.keys()))
        body = dict(name=name,
                    estimator_type=cls.TYPES[type],
                    classes=classes,
                    metadata=metadata)
        response = request(
            'post', '{base_path}/'.format(base_path=cls.base_path), body)
        return cls(**response)

    def delete(self):
        """Delete estimator"""
        request(
            'delete', '{base_path}/{uuid}'.format(base_path=self.base_path, uuid=self.uuid))
        return True

    def import_labels(self, vector_path):
        """Upload +vector_path+ as a vector file and load labels into current estimator"""
        vector_file = File.upload(vector_path)
        return self.load_labels_from(vector_file)

    def load_labels_from(self, file):
        """Load labels from already uploaded +file+"""
        body = dict(vector_file=vector_file.name)
        response = request(
            'post', '{base_path}/load_labels'.format(base_path=cls.base_path), body)
        return response

    def predict_files(self, *files):
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
        if not files:
            raise RuntimeError("files is empty")
        path = '{base_path}/{uuid}/predict/'.format(
            base_path=self.base_path, uuid=self.uuid)
        response = request('post', path, body={
                           'files': [f.name for f in files]})
        job_attrs = response['detail']
        self.prediction_job = PredictionJob.from_attributes(job_attrs)
        return self.prediction_job

    def __repr__(self):
        return "<Estimator uuid={uuid!r} name={name!r}>".format(name=self.name, uuid=self.uuid)
