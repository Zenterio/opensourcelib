import queue
from unittest import TestCase
from unittest.mock import MagicMock, patch

from zaf.application import APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.component.factory import Factory
from zaf.component.manager import COMPONENT_REGISTRY, ComponentManager
from zaf.messages.messagebus import MessageBus

from sutevents import LOG_LINE_RECEIVED

from .. import SERIAL_ENDPOINT
from ..client import SerialClient, SerialError
from .utils import create_harness


class TestSerialClient(TestCase):

    def setUp(self):
        ComponentManager().clear_component_registry()

    def test_send_line_no_wait_writes_to_serial_connection(self):

        def run(client):
            client.send_line_nowait('line')

        written_lines = run_with_client(run)
        assert written_lines.get(timeout=1) == 'line'

    def test_multiple_send_line_no_wait_writes_to_serial_connection(self):

        def run(client):
            client.send_line_nowait('line1')
            client.send_line_nowait('line2')

        written_lines = run_with_client(run)
        assert written_lines.get(timeout=1) == 'line1'
        assert written_lines.get(timeout=1) == 'line2'

    def test_send_line_without_prefix_writes_to_serial_connection(self):

        def run(client):
            assert client.send_line('line', prefix_output=False, timeout=1) == 'before'

        written_lines = run_with_client(run, responses={'line': ['before', ' # ', 'after']})
        assert written_lines.get(timeout=1) == 'line'

    def test_multiple_send_line_without_prefix_writes_to_serial_connection(self):

        def run(client):
            assert client.send_line('line1', prefix_output=False, timeout=1) == 'before1'
            assert client.send_line('line2', prefix_output=False, timeout=1) == 'before2'

        written_lines = run_with_client(
            run,
            responses={
                'line1': ['before1', ' # ', 'after1'],
                'line2': ['before2', ' # ', 'after2']
            })
        assert written_lines.get(timeout=1) == 'line1'

    def test_send_line_with_custom_endmark(self):

        def run(client):
            assert client.send_line(
                'line', prefix_output=False, endmark='end', timeout=1) == 'before\n # '

        written_lines = run_with_client(run, responses={'line': ['before', ' # ', 'end', 'after']})
        assert written_lines.get(timeout=1) == 'line'

    def test_send_line_with_automatic_prefixing(self):

        def run(client):
            self.assertEqual(client.send_line('line', timeout=1), 'before\n # ')

        line = "{ line ; echo exit_code=$?; } 2>&1 | sed -e 's/^/cmd:1: /' && PREFIX='cmd:1:' && echo end_$PREFIX"
        written_lines = run_with_client(
            run,
            responses={
                line: ['cmd:1: before', 'cmd:1:  # ', 'cmd:1: exit_code=0', 'end_cmd:1:', 'after']
            })
        assert written_lines.get(timeout=1) == line

    def test_filter_out_non_command_response_lines(self):

        def run(client):
            self.assertEqual(client.send_line('line', timeout=1), 'b\nd')

        line = "{ line ; echo exit_code=$?; } 2>&1 | sed -e 's/^/cmd:1: /' && PREFIX='cmd:1:' && echo end_$PREFIX"
        written_lines = run_with_client(
            run,
            responses={
                line: [
                    'a', 'cmd:1: b', 'cmd:2: c', 'cmd:1: d', 'cmd:1: exit_code=0', 'end_cmd:1:',
                    'after'
                ]
            })
        assert written_lines.get(timeout=1) == line

    def test_parse_exit_code(self):

        def run(client):
            self.assertEqual(client.send_line('line', timeout=1, expected_exit_code=2), 'b\nd')

        line = "{ line ; echo exit_code=$?; } 2>&1 | sed -e 's/^/cmd:1: /' && PREFIX='cmd:1:' && echo end_$PREFIX"
        written_lines = run_with_client(
            run,
            responses={
                line: [
                    'a', 'cmd:1: b', 'cmd:2: c', 'cmd:1: d', 'cmd:1: exit_code=2', 'end_cmd:1:',
                    'after'
                ]
            },
        )
        assert written_lines.get(timeout=1) == line

    def test_fail_when_exit_code_is_not_expected(self):

        def run(client):
            with self.assertRaises(SerialError):
                client.send_line('line', timeout=1, expected_exit_code=1)

        line = "{ line ; echo exit_code=$?; } 2>&1 | sed -e 's/^/cmd:1: /' && PREFIX='cmd:1:' && echo end_$PREFIX"
        written_lines = run_with_client(
            run,
            responses={
                line: [
                    'a', 'cmd:1: b', 'cmd:2: c', 'cmd:1: d', 'cmd:1: exit_code=2', 'end_cmd:1:',
                    'after'
                ]
            },
        )
        assert written_lines.get(timeout=1) == line

    def test_fail_when_no_serial_connection_is_registered_to_send_command(self):
        messagebus = MessageBus(Factory(ComponentManager(COMPONENT_REGISTRY)))
        messagebus.define_endpoints_and_messages({SERIAL_ENDPOINT: [LOG_LINE_RECEIVED]})
        client = SerialClient(messagebus, 'entity')
        with self.assertRaises(SerialError) as error:
            client.send_line('line', timeout=1)
            assert 'No serial connection' in error.msg

    def test_extended_process_information(self):

        def run(client):
            self.assertEqual(
                client.send_line(
                    'line', timeout=1, expected_exit_code=2, extended_process_information=True),
                ('b\nd', '', 2))

        line = "{ line ; echo exit_code=$?; } 2>&1 | sed -e 's/^/cmd:1: /' && PREFIX='cmd:1:' && echo end_$PREFIX"
        written_lines = run_with_client(
            run,
            responses={
                line: [
                    'a', 'cmd:1: b', 'cmd:2: c', 'cmd:1: d', 'cmd:1: exit_code=2', 'end_cmd:1:',
                    'after'
                ]
            },
        )
        assert written_lines.get(timeout=1) == line


def run_with_client(run, responses={}, expected_exit_code=None):
    """
    Run the run function with a mocked serial connection.

    :param run: will be called as run(client) after setting up harness
    :param responses: dict from line to list of response lines
    :return: queue with the written lines
    """
    connection = MagicMock()
    connection.is_suspended = MagicMock(return_value=False)
    written_lines = queue.Queue()

    with patch('zserial.serial.find_serial_port', return_value=('device', False)), \
            patch('zserial.serial.start_serial_connection', return_value=connection), \
            create_harness() as harness:

        def write_line(line):
            written_lines.put(line)

            for response_line in responses.get(line, []):
                harness.messagebus.trigger_event(
                    LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', response_line)

        connection.write_line.side_effect = write_line

        harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
        client = SerialClient(harness.messagebus, 'entity')
        SerialClient.command_id = 0
        run(client)
        harness.messagebus.wait_for_not_active(timeout=1)

    return written_lines
