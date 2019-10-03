# -*- coding: utf-8 -*-
"""
Package to integrate the DymaxionLabs's funcionality:
    -Upload images
    -Predict imagenes based in object detection models
    -Download results
"""
import os
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

API_URL = os.getenv('DYM_API_URL', 'https://api.dymaxionlabs.com')

API_KEY = os.getenv('DYM_API_KEY')

PROJECT_ID = os.getenv('DYM_PROJECT_ID')

