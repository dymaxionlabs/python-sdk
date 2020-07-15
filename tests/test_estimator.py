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

    @patch("dymaxionlabs.models.request")
    def test_add_image(self, mock_request):
        class TestFile:
            path = ''

            def __init__(self, path):
                self.path = path

        est = Estimator(
            uuid='u1',
            name='n1',
            classes='c1',
            estimator_type='object_detection',
            metadata='m1',
            image_files=[TestFile('f1'), TestFile('f2')],
            configuration='conf1'
        )
        rv = est.add_image(TestFile('f3'))
        body = dict(image_files=[img.path for img in est.image_files])
        mock_request.assert_called_once_with('patch', '/estimators/u1/', body)
        self.assertIs(type(est), Estimator)

    @patch("dymaxionlabs.models.request")
    def test_add_labels_for(self, mock_request):
        class TestFile:
            path = ''

            def __init__(self, path):
                self.path = path

        est = Estimator(
            uuid='u1',
            name='n1',
            classes='c1',
            estimator_type='object_detection',
            metadata='m1',
            image_files=[TestFile('f1'), TestFile('f2')],
            configuration='conf1'
        )
        vector_file = TestFile('t1')
        image_file = TestFile('i1')
        label = 'c1'
        est.add_labels_for(vector_file, image_file, label)
        body = dict(vector_file=vector_file.path,
            related_file=image_file.path,
            label=label)
        mock_request.assert_called_once_with('post', '/estimators/u1/load_labels', body)
        self.assertIs(type(est), Estimator)

    @patch("dymaxionlabs.models.request")
    def test_train(self, mock_request):
        task_params = dict(
            id='task1', 
            name='task1', 
            updated_at=None, 
            created_at=None, 
            finished_at=None, 
            state=None,
            metadata=None, 
            args=None, 
            kwargs=None
        )
        mock_request.return_value = {'detail':task_params}
        est = Estimator(
            uuid='u1',
            name='n1',
            classes='c1',
            estimator_type='object_detection',
            metadata='m1',
            image_files=['f1', 'f2'],
            configuration='conf1'
        )
        rv = est.train()
        mock_request.assert_called_once_with('post', '/estimators/u1/train')
        self.assertEqual(rv.id, 'task1')

    @patch("dymaxionlabs.models.request")
    def test_predict_files(self, mock_request):
        task_params = dict(
            id='task1', 
            name='task1', 
            updated_at=None, 
            created_at=None, 
            finished_at=None, 
            state=None,
            metadata=None, 
            args=None, 
            kwargs=None
        )
        mock_request.return_value = {'detail':task_params}
        est = Estimator(
            uuid='u1',
            name='n1',
            classes='c1',
            estimator_type='object_detection',
            metadata='m1',
            image_files=['f1', 'f2'],
            configuration='conf1'
        )
        rv = est.predict_files(file_folders='file_folders/', output_path='output_path/')
        body = dict(
            files='file_folders/',
            output_path='output_path/',
            confidence=0.2
        )
        mock_request.assert_called_once_with('post', '/estimators/u1/predict/', body=body)
        self.assertEqual(rv.id, 'task1')
