from unittest.mock import patch
import pytest
import dymaxionlabs
import unittest
import responses
import requests

from dymaxionlabs.files import File
from dymaxionlabs.utils import NotFoundError

__author__ = "Dymaxion Labs"
__copyright__ = "Dymaxion Labs"
__license__ = "apache-2.0"

class FileTest(unittest.TestCase):
    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")
    
    @responses.activate
    @patch("dymaxionlabs.utils.request")
    def test_all(self, mock_request):
        test_file = File('foo.txt', '/', 'metadata')
        path="*"
        response = {'error': 'not found'}
        responses.add(responses.GET, 'https://api.dymaxionlabs.com{base_path}/files/?path={path}'.format(
                base_path=test_file.base_path, path=requests.utils.quote(path)),
                  json=response, status=404)
        self.assertIs(mock_request, dymaxionlabs.utils.request)
        try:
            test_file.all()
        except Exception as ex:
            self.assertEqual(type(ex), NotFoundError)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].response.text, '{"error": "not found"}')
