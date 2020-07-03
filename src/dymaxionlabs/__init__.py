# -*- coding: utf-8 -*-
"""
Package to integrate the DymaxionLabs's funcionality:

 - Upload images
 - Predict imagenes based in object detection models
 - Download results

"""
import os
from pkg_resources import get_distribution, DistributionNotFound

from . import files
from . import models
from . import utils

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound
