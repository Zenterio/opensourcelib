import queue
from unittest import TestCase
from unittest.mock import MagicMock, patch

from zaf.application import APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.component.manager import ComponentManager
from zaf.config import MissingConditionalConfigOption
from zaf.messages.dispatchers import LocalMessageQueue

from k2 import CRITICAL_EXTENSION_ERROR
from zserial import SERIAL_RECONNECT

from .. import SERIAL_CONNECTION_LOST, SERIAL_ENDPOINT, SERIAL_SEND_COMMAND
from ..connection import SerialConnectionError
from ..serial import SerialException
from .utils import create_harness


class TestSerialExtension(TestCase):

    def setUp(self):
        ComponentManager().clear_component_registry()

    def test_extension_is_enabled(self):
        with patch('zserial.serial.find_serial_port', return_value=('device', False)):
            with create_harness() as harness:
                assert harness.extension._enabled

    def test_extension_is_enabled_but_device_is_not_specified(self):
        with self.assertRaises(MissingConditionalConfigOption):
            create_harness(device=None).__enter__()

    def test_extension_is_not_connected_until_inialize_sut_is_received(self):
        with patch('zserial.serial.find_serial_port', return_value=('device', False)), \
                patch('zserial.serial.start_serial_connection', return_value=MagicMock()):
            with create_harness() as harness:
                self.assertIsNone(harness.extension._serial_connection)
                harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                self.assertIsNotNone(harness.extension._serial_connection)

    def test_raises_exception_if_send_serial_command_called_after_closing_connection(self):
        with patch('zserial.serial.find_serial_port', return_value=('device', False)), \
                patch('zserial.serial.start_serial_connection', return_value=MagicMock()):
            with create_harness() as harness:
                harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                self.assertIsNotNone(harness.extension._serial_connection)
                harness.extension.destroy()
                self.assertIsNone(harness.extension._serial_connection)
                with self.assertRaises(SerialException):
                    harness.extension.send_serial_command(MagicMock())

    def test_send_serial_command_message_write_line_to_connection(self):
        connection = MagicMock()
        written_lines = queue.Queue()
        connection.write_line.side_effect = lambda line: written_lines.put(line)

        with patch('zserial.serial.find_serial_port', return_value=('device', False)):
            with create_harness() as harness:
                with patch('zserial.serial.start_serial_connection', return_value=connection):
                    harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                    harness.send_request(
                        SERIAL_SEND_COMMAND, SERIAL_ENDPOINT, 'entity', 'command to write')

                    self.assertEqual(written_lines.get(timeout=1), 'command to write')

    def test_send_serial_command_message_write_line_to_connection_only_if_entity_matches(self):
        connection = MagicMock()
        written_lines = queue.Queue()
        connection.write_line.side_effect = lambda line: written_lines.put(line)

        with patch('zserial.serial.find_serial_port', return_value=('device', False)):
            with create_harness() as harness:
                with patch('zserial.serial.start_serial_connection', return_value=connection):
                    harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                    harness.send_request(SERIAL_SEND_COMMAND, SERIAL_ENDPOINT, 'entity2', 'entity2')
                    harness.send_request(SERIAL_SEND_COMMAND, SERIAL_ENDPOINT, 'entity', 'entity')

                    self.assertEqual(written_lines.get(timeout=1), 'entity')

    def test_serial_connection_is_reconnected_when_connection_is_lost(self):
        with patch('zserial.serial.find_serial_port', return_value=('device', False)):
            with create_harness() as harness:
                with harness.patch(
                        'zserial.serial.start_serial_connection') as start_serial_connection:
                    harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                    start_serial_connection.wait_for_call(timeout=1)
                    harness.trigger_event(SERIAL_CONNECTION_LOST, SERIAL_ENDPOINT, 'entity')
                    start_serial_connection.wait_for_call(timeout=1)

    def test_serial_connection_is_reconnected_when_serial_reconnect_is_received(self):
        with patch('zserial.serial.find_serial_port', return_value=('device', False)):
            with create_harness() as harness:
                with harness.patch(
                        'zserial.serial.start_serial_connection') as start_serial_connection:
                    harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                    start_serial_connection.wait_for_call(timeout=1)
                    harness.trigger_event(SERIAL_RECONNECT, SERIAL_ENDPOINT, 'entity')
                    start_serial_connection.wait_for_call(timeout=1)

    def test_critical_extension_exception_sent_if_serial_connection_cant_be_established(self):
        with patch('zserial.serial.find_serial_port', return_value=('device', False)):
            with create_harness() as harness:
                with LocalMessageQueue(harness.messagebus,
                                       [CRITICAL_EXTENSION_ERROR]) as error_queue:
                    with patch('zserial.serial.start_serial_connection', side_effect=SerialConnectionError),\
                            patch('time.sleep'):
                        harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                        assert error_queue.get(timeout=1).message_id == CRITICAL_EXTENSION_ERROR
