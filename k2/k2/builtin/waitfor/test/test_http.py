import unittest
from unittest.mock import Mock, patch

from k2.builtin.waitfor.http import WaitForHttp


class TestWaitForHttpMatch(unittest.TestCase):

    def test_wait_for_match_times_out(self):
        response_mock = Mock()
        response_mock.text = 'content'
        response_mock.ok = True
        with patch('requests.get', return_value=response_mock):
            wait_http = WaitForHttp()

            with self.assertRaises(TimeoutError):
                wait_http.wait_for_match_in_response('url1', 'pattern', timeout=0)

    def test_wait_for_match_returns_match_object(self):
        response_mock = Mock()
        response_mock.text = 'content'
        response_mock.ok = True

        with patch('requests.get', return_value=response_mock) as get_mock:
            wait_http = WaitForHttp()

            m = wait_http.wait_for_match_in_response('url1', r'con(\w+)', poll_interval=0)

            self.assertEqual(m.group(1), 'tent')
            get_mock.assert_called_once()

    def test_wait_for_match_polls_multiple_times(self):

        with patch('requests.get', side_effect=[response_mock('1'), response_mock('2'),
                                                response_mock('3')]) as get_mock:
            wait_http = WaitForHttp()

            m = wait_http.wait_for_match_in_response('url1', r'(3)', poll_interval=0)

            self.assertEqual(m.group(1), '3')
            self.assertEqual(get_mock.call_count, 3)

    def test_wait_for_match_not_ok_causes_retries(self):
        with patch('requests.get', side_effect=[response_mock('content', ok=False),
                                                response_mock('content')]) as get_mock:
            wait_http = WaitForHttp()

            m = wait_http.wait_for_match_in_response('url1', r'content', poll_interval=0)

            self.assertEqual(m.group(0), 'content')
            self.assertEqual(get_mock.call_count, 2)


class TestWaitForHttpStatusCode(unittest.TestCase):

    def test_wait_for_status_code_times_out(self):
        response_mock = Mock()
        response_mock.status_code = 300
        response_mock.ok = True

        with patch('requests.get', return_value=response_mock):
            wait_http = WaitForHttp()

            with self.assertRaises(TimeoutError):
                wait_http.wait_for_status_code('url1', 200, timeout=0)

    def test_wait_for_status_code_returns_response_object(self):
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.ok = True

        with patch('requests.get', return_value=response_mock) as get_mock:
            wait_http = WaitForHttp()

            r = wait_http.wait_for_status_code('url1', 200)

            self.assertEqual(r, response_mock)
            get_mock.assert_called_once()

    def test_wait_for_status_code_polls_multiple_times(self):
        ok_response = response_mock(status_code=200)
        with patch('requests.get',
                   side_effect=[response_mock(status_code=505), response_mock(status_code=302),
                                ok_response]) as get_mock:
            wait_http = WaitForHttp()

            r = wait_http.wait_for_status_code('url1', 200, poll_interval=0)

            self.assertEqual(r, ok_response)
            self.assertEqual(get_mock.call_count, 3)

    def test_wait_for_status_code_works_with_falsy_request_object(self):
        response_mock = Mock()
        response_mock.status_code = 401
        response_mock.ok = False
        response_mock.__nonzero__ = 0

        with patch('requests.get', return_value=response_mock) as get_mock:
            wait_http = WaitForHttp()
            r = wait_http.wait_for_status_code('url1', 401)
            self.assertEqual(r, response_mock)
            get_mock.assert_called_once()


class TestWaitForHttpOk(unittest.TestCase):

    def test_wait_for_ok_times_out(self):
        response_mock = Mock()
        response_mock.ok = False

        with patch('requests.get', return_value=response_mock):
            wait_http = WaitForHttp()

            with self.assertRaises(TimeoutError):
                wait_http.wait_for_ok('url1', timeout=0)

    def test_wait_for_ok_returns_response_object(self):
        response_mock = Mock()
        response_mock.ok = True

        with patch('requests.get', return_value=response_mock) as get_mock:
            wait_http = WaitForHttp()

            r = wait_http.wait_for_ok('url1')

            self.assertEqual(r, response_mock)
            get_mock.assert_called_once()

    def test_wait_for_ok_polls_multiple_times(self):
        ok_response = response_mock(ok=True)
        with patch('requests.get', side_effect=[response_mock(ok=False), response_mock(ok=False),
                                                ok_response]) as get_mock:
            wait_http = WaitForHttp()

            r = wait_http.wait_for_ok('url1', poll_interval=0)

            self.assertEqual(r, ok_response)
            self.assertEqual(get_mock.call_count, 3)


def response_mock(text='text', ok=True, status_code=200):
    response_mock = Mock()
    response_mock.text = text
    response_mock.ok = ok
    if not ok:
        response_mock.raise_for_status.side_effect = Exception
    else:
        response_mock.raise_for_status.return_value = None
    response_mock.status_code = status_code
    return response_mock
