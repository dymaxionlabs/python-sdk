============
dymaxionlabs
============

This is the Python package for accessing the Dymaxion Labs Platform.


Features
========

The Dymaxion Labs Platform allows you:

 - Download and upload satellite and drone images.
 - Train machine learning models for object detection, segmentation, change
   detection, and more.
 - Work your data using a REST API and Python.

This is a publicly installable package. However, if you want access to our full
Platform, you will need to create a Dymaxion Labs account.


Install
=======

The package is currently in beta, so we recommend to install it via pip from
the GitHub repository:

.. code-block:: bash

    pip install git+https://github.com/dymaxionlabs/dymaxionlabs-python.git

To install the latest stable version:

.. code-block:: bash

    pip install dymaxionlabs


Authentication
==============

Sign up at https://app.dymaxionlabs.com/signup if you do not have a user yet,
otherwise log in.

Enter the API Key section, create a new API key and copy the generated key.

You need to set the API key using an environment variable, like this:

.. code-block:: bash

  export DYM_API_KEY=...


You can also do this from Python:

.. code-block:: python

  import os

  os.environ["DYM_API_KEY"] = "insert-api-key"


From now on, you have full access to the Dymaxion Labs API from Python.


Examples
========

Suppose you want to detect pools in a residential area. First, you need to
create an Estimator. In this case, you want an `"object_detection"` type of
model, and there is only one class of object.

.. code-block:: python

  from dymaxionlabs.models import Estimator

  pools_detector = Estimator.create(name="Pools detector",
                                    type="object_detection",
                                    classes=["pool"])


Now, you should upload the images you want to use for training, add them
to your estimator, and create the tiles from the image.

.. code-block:: python

  from dymaxionlabs.files import File

  img = File.upload("pools-2020-02-01.tif", "pools/images/")
  pools_detector.add_image(img)

  tiling_job = img.tiling(output_path="pools/tiles/")
  tiling_job.is_running()
  #=> True


The tiling process generates tiles of 500x500 by default, but you can adjust
the tile size with the `tile_size` parameter.

.. code-block:: python

  # Tile image in 250x250
  tiling_job = img.tiling(output_path="pools/tiles/", tile_size=250)


Next step is to upload your labels file (GeoJSON file) and add them to your
estimator. The labels file must be a GeoJSON of polygons for a specific
class. If you have more than one class, you have to separate your labels in
different files for each class.

.. code-block:: python

  labels = File.upload("labels.geojson", 'pools/labels/')
  pools_detector.add_labels_for(labels, img, "pool")


Now you are ready to train the model. Training might take a few hours to
finish, so the `train()` method returns a `TrainingJob` instance, that
represents the current training job.

.. code-block:: python

  job = pools_detector.train()
  job.is_running()
  #=> True


You can adjust a few parameters when training by updating the `configuration`
dictionary:

.. code-block:: python

  job.configuration.update(epochs=25, steps=500)


Currently there are two training parameters:

* ``epochs``: Number of training epochs (default=15)
* ``steps``: Number of steps per epoch (default=1000)

When the job finishes, your model will be ready to be used for prediction.

Unless you want to predict over the same image you used for training, you
should upload another image and again, create the tiles for that image.

.. code-block:: python

  predict_img = File.upload("pools.tif", 'pools/predict-images/')
  predict_tiles_folder = 'pools/predict-tiles/'
  tiling_job = predict_img.tiling(output_path=predict_tiles_folder)
  tiling_job.is_running()
  #=> True


You are now ready to start a prediction job.  This process might take a few
minutes.

.. code-block:: python

  pools_detector.predict_files([predict_tiles_folder], output_path='pools/predict-results/')
  pools_detector.prediction_job.is_running()
  #=> True


You can download the results when the prediction job has completed.

.. code-block:: python

  for path in pools_detector.prediction_job.metadata["results_files"]:
      File.get(path).download("results/")


Contents
========

.. toctree::
   :maxdepth: 2

   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: http://sphinx-doc.org/domains.html#the-python-domain
.. _Sphinx: http://www.sphinx-doc.org/
.. _Python: http://docs.python.org/
.. _Numpy: http://docs.scipy.org/doc/numpy
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: http://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: http://scikit-learn.org/stable
.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _Google style: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
