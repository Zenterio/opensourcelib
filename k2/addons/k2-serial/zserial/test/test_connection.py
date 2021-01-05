import fcntl
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

from sutevents import LOG_LINE_RECEIVED
from zserial import SERIAL_RAW_LINE
from zserial.connection import SerialConnectionError

from .. import SERIAL_CONNECTION_LOST, SERIAL_ENDPOINT
from ..connection import PortNotFound, _lock_serial_port, _serial_connection, find_serial_port


class TestSerialConnection(TestCase):

    def test_line_is_sent_as_message(self):
        messagebus = MagicMock()
        connection = _serial_connection(messagebus, 'entity')()

        connection.handle_line('line')
        messagebus.trigger_event.assert_called_with(
            SERIAL_RAW_LINE, SERIAL_ENDPOINT, 'entity', 'line')

    def test_message_sent_for_each_line(self):
        messagebus = MagicMock()
        connection = _serial_connection(messagebus, 'entity')()

        connection.handle_line('line1')
        connection.handle_line('line2')
        connection.handle_line('line3')

        messagebus.trigger_event.assert_has_calls(
            [
                call(SERIAL_RAW_LINE, SERIAL_ENDPOINT, 'entity', 'line1'),
                call(SERIAL_RAW_LINE, SERIAL_ENDPOINT, 'entity', 'line2'),
                call(SERIAL_RAW_LINE, SERIAL_ENDPOINT, 'entity', 'line3'),
            ])

    def test_parse_raw_line_with_filter_with_end_of_line_pattern(self):
        messagebus = MagicMock()
        connection = _serial_connection(messagebus, 'entity', ['### error.*'])()

        connection.parse_raw_line('li### error')
        connection.parse_raw_line('ne')

        messagebus.trigger_event.assert_has_calls(
            [
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', '### error'),
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', 'line'),
            ])

    def test_parse_raw_line_with_filter_with_multiple_end_of_line_patterns(self):
        messagebus = MagicMock()
        connection = _serial_connection(messagebus, 'entity', ['!!! warning.*$', '### error.*$'])()

        connection.parse_raw_line('li!!! warning')
        connection.parse_raw_line('n### error')
        connection.parse_raw_line('e')

        messagebus.trigger_event.assert_has_calls(
            [
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', '!!! warning'),
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', '### error'),
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', 'line'),
            ])

    def test_parse_raw_line_with_filter_with_multiple_in_line_patterns(self):
        messagebus = MagicMock()
        connection = _serial_connection(messagebus, 'entity', ['!!! warning', '### error'])()

        connection.parse_raw_line('li### errorn!!! warninge')

        messagebus.trigger_event.assert_has_calls(
            [
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', '!!! warning'),
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', '### error'),
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', 'line'),
            ])

    def test_parse_raw_line_with_filter_matches_full_line(self):
        messagebus = MagicMock()
        connection = _serial_connection(messagebus, 'entity', ['### error'])()

        connection.parse_raw_line('### error')

        messagebus.trigger_event.assert_has_calls(
            [
                call(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, 'entity', '### error'),
            ])

    def test_trigger_connection_lost_message_on_connection_lost(self):
        messagebus = MagicMock()
        connection = _serial_connection(messagebus, 'entity')()
        exception = Exception()
        try:
            # python 3.4 requires a raised exception for log with exc_info to work
            raise exception
        except Exception as e:
            connection.connection_lost(e)
        messagebus.trigger_event.assert_called_with(
            SERIAL_CONNECTION_LOST, SERIAL_ENDPOINT, 'entity', exception)


class TestLockSerialPort(TestCase):

    def test_does_not_raise_serial_connection_error_if_lock_can_be_acquired(self):
        serial = Mock()
        with patch('fcntl.flock') as flock:
            _lock_serial_port(serial)
            flock.assert_called_once_with(serial.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def test_does_raise_serial_connection_error_if_lock_can_not_be_acquired(self):
        serial = Mock()
        with patch('fcntl.flock', new=Mock(side_effect=OSError('hoppsan'))) as flock:
            with self.assertRaisesRegex(
                    SerialConnectionError,
                    'Serial port .* could not be locked. Is it already in use?'):
                _lock_serial_port(serial)
                flock.assert_called_once_with(serial.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


class TestFindSerialPort(TestCase):

    def devices(self):
        devices = []
        device1 = Mock()
        device1.device = '/dev/ttyUSB1'
        device1.name = 'ttyUSB1'
        device1.location = '3-10.5.1'
        devices.append(device1)

        device2 = Mock()
        device2.device = '/dev/ttyUSB2'
        device2.name = 'ttyUSB2'
        device2.location = '3-10.5.2'
        devices.append(device2)
        return devices

    def test_port_can_not_be_found_and_but_device_found_in_file_system_returns_device_as_virtual(
            self):
        with patch('zserial.connection.comports', return_value=self.devices()), \
                patch('os.path.exists', return_value=True):
            self.assertEqual(find_serial_port('/dev/ttyUSB123'), ('/dev/ttyUSB123', True))

    def test_port_can_be_found_using_name(self):
        with patch('zserial.connection.comports', return_value=self.devices()):
            self.assertEqual(find_serial_port('ttyUSB1'), ('/dev/ttyUSB1', False))
            self.assertEqual(find_serial_port('ttyUSB2'), ('/dev/ttyUSB2', False))

    def test_port_can_be_found_using_location(self):
        with patch('zserial.connection.comports', return_value=self.devices()):
            self.assertEqual(find_serial_port('3-10.5.1'), ('/dev/ttyUSB1', False))
            self.assertEqual(find_serial_port('3-10.5.2'), ('/dev/ttyUSB2', False))

    def test_port_can_be_found_using_device(self):
        with patch('zserial.connection.comports', return_value=self.devices()):
            self.assertEqual(find_serial_port('/dev/ttyUSB1'), ('/dev/ttyUSB1', False))
            self.assertEqual(find_serial_port('/dev/ttyUSB2'), ('/dev/ttyUSB2', False))

    def test_port_not_found_raises_exception(self):
        with patch('zserial.connection.comports', return_value=self.devices()), \
                patch('os.path.exists', return_value=False):
            self.assertRaises(PortNotFound, find_serial_port, 'not a port')

    def test_invalid_url_raises_exception(self):
        with patch('zserial.connection.serial_for_url', side_effect=Exception('Boom!')):
            self.assertRaises(PortNotFound, find_serial_port, 'invalid://url')

    def test_port_can_be_found_using_url(self):
        url = 'valid://url'
        with patch('zserial.connection.serial_for_url', return_value=MagicMock()):
            self.assertEqual(find_serial_port(url), (url, True))
