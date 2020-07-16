import unittest
from requests.utils import quote
from unittest.mock import patch
from dymaxionlabs.tasks import Task

import dymaxionlabs

__author__ = "Dymaxion Labs"
__copyright__ = "Dymaxion Labs"
__license__ = "apache-2.0"

class TasksTest(unittest.TestCase):

    def setUp(self):
        self.task = Task(
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

    @patch("dymaxionlabs.tasks.Task.refresh")
    def test_is_not_running(self, mock_refresh):
        self.task.state = "FINISHED"
        rv = self.task.is_running()
        self.assertEqual(rv, False)
        self.task.state = "FAILED"
        rv = self.task.is_running()
        self.assertEqual(rv, False)
        mock_refresh.assert_not_called()

    @patch("dymaxionlabs.tasks.Task.refresh")
    def test_is_running(self, mock_refresh):
        self.task.state = "RUNNING"
        rv = self.task.is_running()
        mock_refresh.assert_called_once()
        self.assertEqual(rv, True)

    @patch("dymaxionlabs.tasks.request")
    def test_refresh(self, mock_request):
        self.task.state = "FINISHED"
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
        rv = self.task.refresh()
        mock_request.assert_called_once_with('get', '/tasks/t1')
        self.assertEqual(rv.state, "RUNNING")
