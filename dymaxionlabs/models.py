import json
import os

from .files import File
from .utils import fetch_from_list_request, request


class Model:
    """
    The Model class represents a pre-trained ML model that can be trained to solve
    different kinds of tasks, like object detection or classification.

    To instance a Model, you should use one of the following class methods:
    :meth:`all()` or :meth:`get()`

    """

    def __init__(self, owner, name, version, description, tags, repo_url, is_public, **extra_attributes):
        self.owner = owner
        self.name = name
        self.version = version
        self.description = description
        self.tags = tags
        self.repo_url = repo_url
        self.is_public = is_public
        self.extra_attributes = extra_attributes

    @classmethod
    def _from_attributes(cls, **attrs):
        """Creates a ``Model`` class from an ``attrs`` dictionary.

        Used internally by other class methods

        :params attrs dict: Model attributes
        :rtype: Model

        """
        return cls(**attrs)

    @classmethod
    def all(cls, username: str):
        """Fetches all available models."""
        return [
            cls._from_attributes(**attrs, version=attrs["latest_version"])
            for attrs in fetch_from_list_request(_get_model_base_path(username=username))
        ]

    @classmethod
    def get(cls, username_modelname: str, *, version: str = None):
        """Gets a model from user

        :param username_modelname str: User name and model name, separated by /
        :param version str: Specific version to fetch, if not specified will use latest version
        :rtype: Model

        """
        parts = username_modelname.split("/")
        if len(parts) != 2:
            raise ValueError("you must specify '{username}/{modelname}'")
        username, modelname = parts
        attrs = request('get', _get_model_base_path(username=username, modelname=modelname))
        version_name = version if version else attrs["latest_version"]
        return cls._from_attributes(**attrs, version=version_name)

    def predict(self, input_dir: str, **kwargs):
        """Start a prediction task using this model.

        :returns: a dict with info about the new Task

        """
        from .tasks import Task

        path = _get_model_base_path(username=self.owner, modelname=self.name, version=self.version)
        attrs = request('post', f'{path}predict/', body=dict(parameters={'input_dir': input_dir, **kwargs}))
        return Task._from_attributes(**attrs)

    def __repr__(self):
        return "<Model owner={owner!r} name={name!r} version={version!r}>".format(owner=self.owner, name=self.name, version=self.version)
