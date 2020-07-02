import unittest
from unittest.mock import patch
from dymaxionlabs.files import File

__author__ = "Dymaxion Labs"
__copyright__ = "Dymaxion Labs"
__license__ = "apache-2.0"

class FileTest(unittest.TestCase):
    def setUp(self):
        self.test_file = File('test', '/test', 'metadata')

    def tearDown(self):
        del self.test_file

    @patch("dymaxionlabs.files.request")
    def test_all(self, mock_request):
        mock_request.return_value = [
            {'name':'foo', 'path':'/foo', 'metadata':'metadata_foo'},
            {'name':'bar', 'path':'/bar', 'metadata':'metadata_bar'},
        ]
        rv = self.test_file.all()
        names = [f.name for f in rv]
        mock_request.assert_called_once()
        self.assertListEqual(names, ['foo', 'bar'])
