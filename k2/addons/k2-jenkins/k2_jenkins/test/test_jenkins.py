import unittest
from unittest.mock import Mock, patch

import requests

from ..jenkins import JenkinsComponent, JenkinsException


class TestJenkins(unittest.TestCase):

    def test_jenkins_component_enter_connects_to_jenkins_and_waits_for_http_status_200(self):
        _503 = Mock()
        _503.status_code = 503
        _404 = Mock()
        _404.status_code = 404
        _200 = Mock()
        _200.status_code = 200
        mock_responses = [requests.exceptions.ConnectionError, _503, _404, _200]

        jenkins_node = Mock()
        jenkins_node.ip = '1.2.3.4'
        jenkins_component = JenkinsComponent(jenkins_node=jenkins_node)

        with patch('requests.get', side_effect=mock_responses) as requests_mock, \
                patch('jenkins.Jenkins', return_value=create_jenkins_mock()), \
                patch('time.sleep'):

            self.assertEqual(jenkins_component.__enter__(), jenkins_component)
            requests_mock.assert_called_with('http://1.2.3.4:8080')

    def test_jenkins_component_enter_times_out(self):
        _503 = Mock()
        _503.status_code = 503
        jenkins_node = Mock()
        jenkins_node.ip = '1.2.3.4'
        jenkins_component = JenkinsComponent(start_timeout=0, jenkins_node=jenkins_node)

        with patch('requests.get', return_value=_503), \
                patch('jenkins.Jenkins', return_value=create_jenkins_mock()), \
                patch('time.sleep'):
            with self.assertRaises(TimeoutError):
                jenkins_component.__enter__()

    def test_jenkins_component_enter_wait_for_normal_op_returns_false_raises_exception(self):
        _200 = Mock()
        _200.status_code = 200
        jenkins_node = Mock()
        jenkins_node.ip = '1.2.3.4'
        jenkins_component = JenkinsComponent(jenkins_node=jenkins_node)

        with patch('requests.get', return_value=_200), \
                patch('jenkins.Jenkins', return_value=create_jenkins_mock(normal_op=False)), \
                patch('time.sleep'):
            with self.assertRaises(JenkinsException):
                jenkins_component.__enter__()

    def test_jenkins_component_build_job_returns_build_info_object_with_result(self):
        with patch('time.sleep'):
            jenkins_component = JenkinsComponent()
            jenkins_component._server = create_jenkins_mock()

            self.assertEqual(jenkins_component.build_job('name').result, 'SUCCESS')

    def test_jenkins_component_build_job_polls_queue_item_until_job_started(self):
        with patch('time.sleep'):
            jenkins_component = JenkinsComponent()
            jenkins_mock = create_jenkins_mock(polls_before_job_started=3)
            jenkins_component._server = jenkins_mock

            self.assertEqual(jenkins_component.build_job('name').result, 'SUCCESS')
            self.assertEqual(jenkins_mock.get_queue_item.call_count, 4)

    def test_jenkins_component_build_job_polls_build_info_until_job_done(self):
        with patch('time.sleep'):
            jenkins_component = JenkinsComponent()
            jenkins_mock = create_jenkins_mock(polls_before_job_done=7)
            jenkins_component._server = jenkins_mock

            self.assertEqual(jenkins_component.build_job('name').result, 'SUCCESS')
            # Polls 8 times and then calls get_build_info one more time to
            # get the complete build info including all artifacts
            self.assertEqual(jenkins_mock.get_build_info.call_count, 9)

    def test_jenkins_component_build_job_times_out_before_done(self):
        with patch('time.sleep'):
            jenkins_component = JenkinsComponent()
            jenkins_mock = create_jenkins_mock(polls_before_job_done=7)
            jenkins_component._server = jenkins_mock

            with self.assertRaises(TimeoutError):
                jenkins_component.build_job('name', build_timeout=0)

    def test_jenkins_component_build_info_contains_build_information(self):
        with patch('time.sleep'):
            jenkins_component = JenkinsComponent()
            jenkins_mock = create_jenkins_mock()
            jenkins_component._server = jenkins_mock

            self.assertEqual(jenkins_component.build_job('name').number, 7)
            self.assertEqual(
                jenkins_component.build_job('name').artifacts, ['artifact1', 'dir/artifact2'])
            self.assertEqual(
                jenkins_component.build_job('name').console_log, 'console log\nFinished: SUCCESS')


def create_jenkins_mock(normal_op=True, polls_before_job_started=0, polls_before_job_done=0):
    jenkins_mock = Mock()
    jenkins_mock.wait_for_normal_op.return_value = normal_op
    jenkins_mock.build_job.return_value = normal_op
    jenkins_mock.get_build_console_output.return_value = 'console log\nFinished: SUCCESS'

    job_started_polls = 0

    def get_queue_item(id):
        nonlocal job_started_polls
        job_started_polls += 1
        if polls_before_job_started < job_started_polls:
            return {'executable': {'number': 7}}
        else:
            return {}

    jenkins_mock.get_queue_item.side_effect = get_queue_item

    job_done_polls = 0

    def get_build_info(name, build_number):
        nonlocal job_done_polls
        job_done_polls += 1
        if polls_before_job_done < job_done_polls:
            return {
                'result':
                'SUCCESS',
                'artifacts': [
                    {
                        'relativePath': 'artifact1',
                        'some_key': 'some_value',
                    },
                    {
                        'relativePath': 'dir/artifact2',
                        'some_key': 'some_value',
                    },
                ],
            }
        else:
            return {'result': None}

    jenkins_mock.get_build_info.side_effect = get_build_info
    return jenkins_mock
