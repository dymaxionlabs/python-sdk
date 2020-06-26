import json
import os
import requests

from .files import File
from .utils import fetch_from_list_request, request

DYM_PREDICT = '/estimators/{estimatorId}/predict/'


class Estimator:
    """
    The Estimator class represents a Model that can be trained to solve
    different kinds of tasks, like object detection or classification.

    """

    TYPES = dict(object_detection='OD')

    base_path = '/estimators'

    def __init__(self, *, uuid, name, classes, estimator_type, metadata,
                 image_files, configuration, **extra_attributes):
        """Estimator constructor

        Usually created when using other classmethods: all(), get(), or create()

        Args:
            uuid: internal id
            name: name
            classes: list of labels/classes
            estimator_type: type of estimator (i.e. )
            image_files: list of associated image files used for training
            metadata: user metadata
            configuration: estimator configuration
            extra_attributes: extra attributes from API endpoint
        """
        self.uuid = uuid
        self.name = name
        self.classes = classes
        self.estimator_type = estimator_type
        self.metadata = metadata
        self.image_files = image_files
        self.configuration = configuration
        self.extra_attributes = extra_attributes

        self.training_job = None
        self.prediction_job = None

    @classmethod
    def _from_attributes(cls, **attrs):
        """Creates an Estimator class from an +attrs+ dictionary

        This method also fetches related entities.

        Used internally by other class methods
        """
        attrs['image_files'] = [
            File(name=os.path.basename(path), path=path, metadata=None)
            for path in attrs['image_files']
        ]
        return cls(**attrs)

    @classmethod
    def all(cls):
        """Fetch all estimators"""
        return [
            cls._from_attributes(**attrs)
            for attrs in fetch_from_list_request('{base_path}/'.format(
                base_path=cls.base_path))
        ]

    @classmethod
    def get(cls, uuid):
        """Get estimator with +uuid+"""
        attrs = request(
            'get', '{base_path}/{uuid}'.format(base_path=cls.base_path,
                                               uuid=uuid))
        return cls._from_attributes(**attrs)

    @classmethod
    def create(cls,
               *,
               name,
               type,
               classes,
               training_hours=None,
               metadata=None,
               configuration={}):
        """Creates a new Estimator named +name+ of +type+ with +classes+ as labels
            with +training_hours+ hour of training job

        A metadata dictionary can be added via the +metadata+ parameter
        A config dictionary con be added via the +configuration+ parameter
        """
        if type not in cls.TYPES:
            raise TypeError("{} should be one of these: {}".format(
                type, cls.TYPES.keys()))
        if training_hours is not None:
            configuration['training_hours'] = training_hours
        body = dict(name=name,
                    estimator_type=cls.TYPES[type],
                    classes=classes,
                    metadata=metadata,
                    configuration=configuration)
        response = request('post',
                           '{base_path}/'.format(base_path=cls.base_path),
                           body)
        return cls._from_attributes(**response)

    def save(self):
        """Update estimator"""
        body = dict(name=self.name,
                    classes=self.classes,
                    metadata=self.metadata,
                    configuration=self.configuration)
        response = request(
            'patch', '{base_path}/{uuid}/'.format(base_path=self.base_path,
                                                  uuid=self.uuid), body)
        return self._from_attributes(**response)

    def delete(self):
        """Delete estimator"""
        request(
            'delete', '{base_path}/{uuid}'.format(base_path=self.base_path,
                                                  uuid=self.uuid))
        return True

    def add_image(self, *images):
        """Add an Image File to the estimator, for training"""
        new_image_files = [
            img.path for img in set(self.image_files + list(images))
        ]
        body = dict(image_files=new_image_files)
        response = request(
            'patch', '{base_path}/{uuid}/'.format(base_path=self.base_path,
                                                  uuid=self.uuid), body)
        self.image_files = list(set(self.image_files + list(images)))
        return self

    def add_labels_for(self, vector_file, image_file, label):
        """
        Add labels from an already uploaded +vector_file+ related to
        +image_file+ and tags these labels like +label+
        """
        if label not in self.classes:
            raise ValueError(
                "Label '{}' is invalid. Must be one of: {}".format(
                    label, self.classes))
        body = dict(vector_file=vector_file.path,
                    related_file=image_file.path,
                    label=label)
        response = request(
            'post',
            '{base_path}/{uuid}/load_labels'.format(base_path=self.base_path,
                                                    uuid=self.uuid), body)
        return self

    def train(self):
        from .tasks import Task
        """Train

        This function will start a training job over the current estimator.
        I will create a model based on all the images from the estimator
        and the associates annotations.

        Returns:
            Returns a dict with info about the new TrainingJob
        """
        response = request(
            'post', '{base_path}/{uuid}/train'.format(base_path=self.base_path,
                                                      uuid=self.uuid))
        self.training_job = Task._from_attributes(response['detail'])
        return self.training_job

    def predict_files(self, *files, output_path, confidence=0.2):
        from .tasks import Task
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
        if not output_path:
            raise RuntimeError("Output path can not be null")
        if not (confidence >= 0.0 and confidence <= 1):
            raise RuntimeError("Confidence's value has to be betwen 0.0 and 1")
        path = '{base_path}/{uuid}/predict/'.format(base_path=self.base_path,
                                                    uuid=self.uuid)
        response = request('post',
                           path,
                           body={
                               'files': [f.path for f in files],
                               'output_path': output_path,
                               'confidence': confidence,
                           })
        job_attrs = response['detail']
        self.prediction_job = Task._from_attributes(job_attrs)
        return self.prediction_job

    def __repr__(self):
        return "<Estimator uuid={uuid!r} name={name!r}>".format(name=self.name,
                                                                uuid=self.uuid)
