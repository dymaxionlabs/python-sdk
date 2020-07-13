import unittest
from requests.utils import quote
from unittest.mock import patch
from dymaxionlabs.models import Estimator

import dymaxionlabs

__author__ = "Dymaxion Labs"
__copyright__ = "Dymaxion Labs"
__license__ = "apache-2.0"

class EstimatorTest(unittest.TestCase):

    @patch("dymaxionlabs.utils.request")
    def test_all(self, mock_request):
        mock_request.return_value = {'results':[
            {'uuid':'u1', 'name':'n1', 'classes':'c1', 'estimator_type':'t1', 'metadata':'m1',
                 'image_files':['f1','f2'], 'configuration':'conf1'}
        ], 'next':None}
        rv = Estimator.all()
        print(rv)
        mock_request.assert_called_once_with('get', '/estimators/', params={})
        self.assertEqual(rv[0].uuid, 'u1')
        self.assertEqual(rv[0].name, 'n1')

    @patch("dymaxionlabs.models.request")
    def test_get(self, mock_request):
        mock_request.return_value = {'uuid':'u1', 'name':'n1', 'classes':'c1', 
            'estimator_type':'t1', 'metadata':'m1',
            'image_files':['f1','f2'], 'configuration':'conf1'}
        rv = Estimator.get('u1')
        mock_request.assert_called_once_with('get', '/estimators/u1')
        self.assertEqual(rv.uuid, 'u1')
        self.assertEqual(rv.name, 'n1')
 
    @patch("dymaxionlabs.models.request")
    def test_create(self, mock_request):
        mock_request.return_value = {'uuid':'u1', 'name':'n1', 'classes':'c1', 
            'estimator_type':'object_detection', 'metadata':'m1',
            'image_files':['f1','f2'], 'configuration':'conf1'}
        rv = Estimator.create(name='u1', type='object_detection', classes='c1')
        body = {'name': 'u1', 'estimator_type': 'OD', 'classes': 'c1', 'metadata': None, 'configuration': {}}
        mock_request.assert_called_once_with('post', '/estimators/', body)
        self.assertEqual(rv.uuid, 'u1')
        self.assertEqual(rv.name, 'n1')

    @patch("dymaxionlabs.models.request")
    def test_save(self, mock_request):
        mock_request.return_value = {'uuid':'u1', 'name':'n1', 'classes':'c1', 
            'estimator_type':'object_detection', 'metadata':'m1',
            'image_files':['f1','f2'], 'configuration':'conf1'}
        rv = Estimator(
            uuid='u1',
            name='n1',
            classes='c1',
            estimator_type='object_detection',
            metadata='m1',
            image_files=['f1','f2'],
            configuration='conf1'
        ).save()
        body = {'name': 'n1', 'classes': 'c1', 'metadata': 'm1', 'configuration': 'conf1'}
        mock_request.assert_called_once_with('patch', '/estimators/u1/', body)
        self.assertEqual(rv.uuid, 'u1')
        self.assertEqual(rv.name, 'n1')

    @patch("dymaxionlabs.models.request")
    def test_delete(self, mock_request):
        mock_request.return_value = True
        rv = Estimator(
            uuid='u1',
            name='n1',
            classes='c1',
            estimator_type='object_detection',
            metadata='m1',
            image_files=['f1','f2'],
            configuration='conf1'
        ).delete()
        mock_request.assert_called_once_with('delete', '/estimators/u1')
        self.assertTrue(rv)
