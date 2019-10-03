============
dymaxionlabs
============

Introduction
============



Features
========
DymaxionLabs's funcionality:

   Upload images.

   Predict imagenes based in object detection models.

   Download results.


Instalation
===========

Install the latest client library via pip

pip install dymaxionlabs


Authentication
==============

Sing up at `<https://app.dymaxionlabs.com>`_  if you don't have a user yet. Or log in if you have it.

Enter in the API Key section and create a nuevo API Key. Copy the generated key and set this as a enviroment variable called DYM_API_URL

You is already available to use the functionalities from the client

Examples
========

For create instances of models or project you have to know their uuid. 

About the models you can obtaing that information in the models section 
of our app https://app.dymaxionlabs.com/home/models .
You have to pass this uuid to the constructor of your model instance

And for projects you have to visitr your home page https://app.dymaxionlabs.com/home 
and there you can see the uuid of the project that you had selected
You have to set this uuid as a environment variable called DYM_PROJECT_ID 
and the Project will use it for create the instance


You can predict objects in yours locales images

.. code-block:: python

    from dymaxionlabs.model import Estimator
    import time

    model = Estimator('b4676699-27c8-4193-a24c-cffaf88cce92')

    job = model.predict(local_files=['img.jpg'])

    while not job.status():
        print("Waiting for results...")
        time.sleep(60)

    job.download_results("./results")

or use the previously uploaded


.. code-block:: python

    from dymaxionlabs.model import Project
    import time

    project = Project()
    files = project.files()

    model = Estimator('b4676699-27c8-4193-a24c-cffaf88cce92')

    job = model.predict(preload_files=[files[0].name])

    while not job.status():
        print("Waiting for seconds results...")
        time.sleep(60)

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
