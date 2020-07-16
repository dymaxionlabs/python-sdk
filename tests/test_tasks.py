import unittest
from requests.utils import quote
from unittest.mock import patch
from dymaxionlabs.tasks import Task

import dymaxionlabs

__author__ = "Dymaxion Labs"
__copyright__ = "Dymaxion Labs"
__license__ = "apache-2.0"

class TasksTest(unittest.TestCase):

    @patch("dymaxionlabs.tasks.request")
    def test_is_running(self, mock_request):
        task = Task(
            id="t1", 
            name="t1", 
            updated_at=None, 
            created_at=None, 
            finished_at=None, 
            state="FINISHED",
            metadata=None, 
            args=None, 
            kwargs=None
        )
        rv = task.is_running()
        self.assertEqual(rv, False)
        mock_request.assert_not_called()
        task.state = "RUNNING"
        mock_request.return_value = dict(
            id="t1", 
            name="t1", 
            updated_at=None, 
            created_at=None, 
            finished_at=None, 
            state="RUNNING",
            metadata=None, 
            args=None, 
            kwargs=None
        )
        rv = task.is_running()
        mock_request.assert_called_once_with('get', '/tasks/t1')
        self.assertEqual(rv, True)

    @patch("dymaxionlabs.tasks.request")
    def test_refresh(self, mock_request):
        task = Task(
            id="t1", 
            name="t1", 
            updated_at=None, 
            created_at=None, 
            finished_at=None, 
            state="FINISHED",
            metadata=None, 
            args=None, 
            kwargs=None
        )
        mock_request.return_value = dict(
            id="t1", 
            name="t1", 
            updated_at=None, 
            created_at=None, 
            finished_at=None, 
            state="RUNNING",
            metadata=None, 
            args=None, 
            kwargs=None
        )
        rv = task.refresh()
        mock_request.assert_called_once_with('get', '/tasks/t1')
        self.assertEqual(rv.state, "RUNNING")
