import unittest
from requests.utils import quote
from unittest.mock import patch
from dymaxionlabs.files import File

__author__ = "Dymaxion Labs"
__copyright__ = "Dymaxion Labs"
__license__ = "apache-2.0"

class FileTest(unittest.TestCase):

    @patch("dymaxionlabs.files.request")
    def test_all(self, mock_request):
        mock_request.return_value = [
            {'name':'foo', 'path':'/foo', 'metadata':'metadata_foo'},
            {'name':'bar', 'path':'/bar', 'metadata':'metadata_bar'},
        ]
        rv = File.all()
        names = [f.name for f in rv]
        paths = [f.path for f in rv]
        # test URL *
        mock_request.assert_called_once_with('get', '/storage/files/?path={path}'.format(
                path=quote('*')))
        # test received file names
        self.assertListEqual(names, ['foo', 'bar'])
        # test received file paths
        self.assertListEqual(paths, ['/foo', '/bar'])


    @patch("dymaxionlabs.files.request")
    def test_get(self, mock_request):
        mock_request.return_value = {'detail':
            {'name':'foo', 'path':'/foo', 'metadata':'metadata_foo'}
        }
        rv = File.get('/foo')
        mock_request.assert_called_once_with('get', '/storage/file/?path={path}'.format(
            path=quote('/foo')))
        self.assertEqual(rv.name,'foo')
        self.assertEqual(rv.path,'/foo') 
        self.assertEqual(rv.metadata,'metadata_foo')
    
    @patch("dymaxionlabs.files.request")
    def test_delete(self, mock_request):
        mock_request.return_value = True
        rv = File('foo', '/foo', 'metadata_foo').delete()
        mock_request.assert_called_once_with('delete', '/storage/file/?path={path}'.format(
            path=quote('/foo')))
        self.assertTrue(rv)



