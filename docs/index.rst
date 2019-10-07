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

Install the latest client package via pip:

.. code-block:: bash

    pip install dymaxionlabs


Authentication
==============

Sing up at https://app.dymaxionlabs.com/signup if you don't have a user yet,
otherwise log in.

When entering the first time, you will be asked to create a new Project. After
nameing your project you will enter the main dashboard.  Take note of your
Project Id.

Now enter the API Key section, create a new API key and copy the generated key.

You need to set both keys as environment variables, like this:

.. code-block:: bash

  export DYM_API_KEY=...
  export DYM_PROJECT_ID=...


You can also do this from Python:

.. code-block:: python

  import os

  os.environ["DYM_API_KEY"] = "insert-api-key"
  os.environ["DYM_PROJECT_ID"] = "insert-project-id"


From now on, you have full access to the Dymaxion Labs API from Python.


Examples
========

To use your models for predicting, you have to know their UUID.

You can obtain this by visiting the models page:
https://app.dymaxionlabs.com/home/models.
Click on the Edit button of your model, then on Show UUID menu option. Copy
this and pass it as parameter to the ``Estimator`` constructor.

You can predict objects in local images. For example, if you have ``img.jpg``:

.. code-block:: python

    import time
    from dymaxionlabs.model import Estimator

    model = Estimator('b4676699-27c8-4193-a24c-cffaf88cce92')

    job = model.predict_files(local_files=['./img.jpg'])

    # Wait for results
    while not job.status():
        print("Waiting for results...")
        time.sleep(60)

    # Download results to ./results directory (will be created if not exists)
    job.download_results("./results")


or use previously uploaded files (*remote*)

.. code-block:: python

    from dymaxionlabs.model import Estimator, Project
    import time

    project = Project()
    files = project.files()
    first_file = files[0]

    model = Estimator('b4676699-27c8-4193-a24c-cffaf88cce92')

    job = model.predict_files(remote_files=[first_file.name])

    # Wait for results
    while not job.status():
        print("Waiting for seconds results...")
        time.sleep(60)

    # Download results to ./results directory (will be created if not exists)
    job.download_results("./results")


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
