import json
import os

from .files import File
from .utils import fetch_from_list_request, request


class Estimator:
    """
    The Estimator class represents a Model that can be trained to solve
    different kinds of tasks, like object detection or classification.

    To instance an Estimator, you should use one of the following class
    methods: :meth:`all()`, :meth:`get()`, or :meth:`create()`.

    :param str uuid: internal id
    :param str name: name
    :param list classes: list of labels/classes
    :param str estimator_type: type of estimator (i.e. )
    :param list image_files: list of associated image files used for training
    :param dict metadata: user metadata
    :param dict configuration: estimator configuration
    :param dict extra_attributes: extra attributes from API endpoint

    """

    TYPES = dict(object_detection='OD')

    base_path = '/estimators'

    def __init__(self, *, uuid, name, classes, estimator_type, metadata,
                 image_files, configuration, **extra_attributes):
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
        """Creates an ``Estimator`` class from an ``attrs`` dictionary.

        This method also fetches related entities.

        Used internally by other class methods

        :params attrs dict: Estimator attributes
        :rtype: Estimator

        """
        attrs['image_files'] = [
            File(name=os.path.basename(path), path=path, metadata=None)
            for path in attrs['image_files']
        ]
        return cls(**attrs)

    @classmethod
    def all(cls):
        """Fetches all estimators in the current project."""
        return [
            cls._from_attributes(**attrs)
            for attrs in fetch_from_list_request(f'{cls.base_path}/')
        ]

    @classmethod
    def get(cls, uuid):
        """Gets an estimator identified by ``uuid``.

        :param uuid str: Estimator UUID
        :rtype: Estimator

        """
        attrs = request('get', f'{cls.base_path}/{uuid}/')
        return cls._from_attributes(**attrs)

    @classmethod
    def create(cls, *, name, type, classes, metadata=None, configuration={}):
        """Creates a new Estimator named ``name`` of ``type`` with
        ``classes`` as labels with ``training_hours`` hour of training job.

        A metadata dictionary can be added via the ``metadata`` parameter. A
        configuration dictionary can be added via the ``configuration``
        parameter.

        :param name str: A name to identify the estimator
        :param type str: Type of estimator ("object_detection")
        :param classes list: List of classes/labels of objects
        :param metadata dict: Optional metadata dictionary to store extra attributes
        :param configuration dict: Optional configuration dictionary for training
        :rtype: Estimator

        """
        if type not in cls.TYPES:
            raise TypeError("{} should be one of these: {}".format(
                type, cls.TYPES.keys()))
        body = dict(name=name,
                    estimator_type=cls.TYPES[type],
                    classes=classes,
                    metadata=metadata,
                    configuration=configuration)
        response = request('post', f'{cls.base_path}/', body)
        return cls._from_attributes(**response)

    def save(self):
        """Updates the estimator.

        :returns: itself

        """
        body = dict(name=self.name,
                    classes=self.classes,
                    metadata=self.metadata,
                    configuration=self.configuration)
        response = request('patch', f'{self.base_path}/{self.uuid}/', body)
        return self._from_attributes(**response)

    def delete(self):
        """Deletes the estimator.

        :returns: ``True`` if estimator was succesfully deleted.

        """
        request('delete', f'{self.base_path}/{self.uuid}/')
        return True

    def add_image(self, *images):
        """Adds an image :class:`File` to the estimator, for training.

        :param images: one or multiple image :class:`File` instances
        :returns: itself

        """
        new_image_files = [
            img.path for img in set(self.image_files + list(images))
        ]
        body = dict(image_files=new_image_files)
        request('patch', f'{self.base_path}/{self.uuid}/', body)
        self.image_files = list(set(self.image_files + list(images)))
        return self

    def add_labels_for(self, vector_file, image_file, label):
        """Adds labels from an already uploaded ``vector_file`` related to
        ``image_file`` and tags these labels like ``label``.

        :param File vector_file: a GeoJSON file with polygons representing annotated objects
        :param File image_file: the corresponding image file to be annotated.
        :param str label: the class/label to use for the annotations
        :returns: itself

        """
        if label not in self.classes:
            raise ValueError(
                "Label '{}' is invalid. Must be one of: {}".format(
                    label, self.classes))
        body = dict(vector_file=vector_file.path,
                    related_file=image_file.path,
                    label=label)
        request('post', f'{self.base_path}/{self.uuid}/load_labels/', body)
        return self

    def train(self):
        """Start a training job using this estimator.

        It will build a custom model based on all the images from the
        estimator and the associates annotations.

        :returns: a dict with info about the new TrainingJob

        """
        from .tasks import Task

        response = request('post', f'{self.base_path}/{self.uuid}/train/')
        self.training_job = Task._from_attributes(**response['detail'])
        return self.training_job

    def predict_files(self, tile_dirs, output_path=".", confidence=0.2):
        """Starts a prediction job on the specified ``tile_dirs``, and stores
        the results using ``confidence`` as a threshold, into
        ``output_path``.

        :param list tile_dirs: list of directories with tiles to predict
        :param str output_path: results output path
        :param float confidence: confidence value for results

        :returns: a dict with info about the new :class:`PredictionJob`

        """
        from .tasks import Task

        if not tile_dirs:
            raise RuntimeError("Tile directories is empty")
        if not output_path:
            raise RuntimeError("Output path can not be null")
        if not (confidence >= 0.0 and confidence <= 1):
            raise RuntimeError("Confidence's value has to be betwen 0.0 and 1")
        body = dict(files=tile_dirs,
                    output_path=output_path,
                    confidence=confidence)
        response = request('post',
                           f'{self.base_path}/{self.uuid}/predict/',
                           body=body)
        job_attrs = response['detail']
        self.prediction_job = Task._from_attributes(**job_attrs)
        return self.prediction_job

    def __repr__(self):
        return "<Estimator uuid={uuid!r} name={name!r}>".format(name=self.name,
                                                                uuid=self.uuid)
