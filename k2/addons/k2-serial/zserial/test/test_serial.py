import queue
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from zaf.application import APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.component.manager import ComponentManager
from zaf.config import MissingConditionalConfigOption
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from k2 import CRITICAL_EXTENSION_ERROR
from k2.sut import SUT
from zserial import SERIAL_RECONNECT

from .. import SERIAL_CONNECTION_LOST, SERIAL_ENABLED, SERIAL_ENDPOINT, SERIAL_LOG_ENABLED, \
    SERIAL_RESUME, SERIAL_SEND_COMMAND, SERIAL_SUSPEND, SUT_SERIAL_PORTS
from ..connection import SerialConnectionError
from ..serial import SerialException, SerialLogSourceExtension
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
        connection = MagicMock()
        connection.is_suspended = MagicMock(return_value=False)
        with patch('zserial.serial.find_serial_port', return_value=('device', False)), \
                patch('zserial.serial.start_serial_connection', return_value=connection):
            with create_harness() as harness:
                self.assertIsNone(harness.extension._serial_connection)
                harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                self.assertIsNotNone(harness.extension._serial_connection)

    def test_raises_exception_if_send_serial_command_called_after_closing_connection(self):
        connection = MagicMock()
        connection.is_suspended = MagicMock(return_value=False)
        with patch('zserial.serial.find_serial_port', return_value=('device', False)), \
                patch('zserial.serial.start_serial_connection', return_value=connection):
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
        connection.is_suspended = MagicMock(return_value=False)
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
        connection.is_suspended = MagicMock(return_value=False)
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

    def test_raises_exception_if_trying_to_suspend_when_already_suspended(self):
        connection = MagicMock()
        connection.is_suspended = MagicMock(return_value=True)
        with patch('zserial.serial.find_serial_port', return_value=('device', False)), \
                patch('zserial.serial.start_serial_connection', return_value=connection):
            with create_harness() as harness:
                harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                with self.assertRaises(SerialException):
                    serial = harness.send_request(SERIAL_SUSPEND, SERIAL_ENDPOINT,
                                                  'entity').wait()[0].result()
                    self.assertIsNone(serial)

    def test_raises_exception_if_trying_to_resume_and_active_connection(self):
        connection = MagicMock()
        connection.is_suspended = MagicMock(return_value=False)
        with patch('zserial.serial.find_serial_port', return_value=('device', False)), \
                patch('zserial.serial.start_serial_connection', return_value=connection):
            with create_harness() as harness:
                harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
                with self.assertRaises(SerialException):
                    harness.send_request(SERIAL_RESUME, SERIAL_ENDPOINT,
                                         'entity').wait()[0].result()


class TestSerialLogSources(TestCase):

    def test_no_suts(self):
        config = ConfigManager()
        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(ext_config.config, {})

    def test_no_ports(self):
        sut = 'sut'
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_PORTS, [], entity=sut)
        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(ext_config.config, {})

    def test_serial_not_enabled(self):
        sut = 'sut'
        port = 'port'
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_PORTS, [port], entity=sut)
        config.set(SERIAL_ENABLED, False, entity=port)
        config.set(SERIAL_LOG_ENABLED, True, entity=port)

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(ext_config.config, {})

    def test_serial_log_not_enabled(self):
        sut = 'sut'
        port = 'port'
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_PORTS, [port], entity=sut)
        config.set(SERIAL_ENABLED, True, entity=port)
        config.set(SERIAL_LOG_ENABLED, False, entity=port)

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(ext_config.config, {})

    def test_serial_log_enabled(self):
        sut = 'sut'
        port = 'port'
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_PORTS, [port], entity=sut)
        config.set(SERIAL_ENABLED, True, entity=port)
        config.set(SERIAL_LOG_ENABLED, True, entity=port)

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(len(ext_config.config), 1)
            self.assertEqual(list(ext_config.config.values())[0], ['serial-port'])

    def test_serial_log_enabled_on_multiple_suts(self):
        suts = ['sut1', 'sut2']
        ports = ['port1', 'port2']
        config = ConfigManager()
        config.set(SUT, suts)
        config.set(SUT_SERIAL_PORTS, ports[0:1], entity=suts[0])
        config.set(SUT_SERIAL_PORTS, ports[1:2], entity=suts[1])
        config.set(SERIAL_ENABLED, True, entity=ports[0])
        config.set(SERIAL_ENABLED, True, entity=ports[1])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[0])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[1])

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(len(ext_config.config), 2)
            self.assertEqual(list(ext_config.config.values())[0], ['serial-port1'])
            self.assertEqual(list(ext_config.config.values())[1], ['serial-port2'])

    def test_serial_log_enabled_only_on_second_sut(self):
        suts = ['sut1', 'sut2']
        ports = ['port1', 'port2']
        config = ConfigManager()
        config.set(SUT, suts)
        config.set(SUT_SERIAL_PORTS, ports[0:1], entity=suts[0])
        config.set(SUT_SERIAL_PORTS, ports[1:2], entity=suts[1])
        config.set(SERIAL_ENABLED, True, entity=ports[0])
        config.set(SERIAL_ENABLED, True, entity=ports[1])
        config.set(SERIAL_LOG_ENABLED, False, entity=ports[0])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[1])

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(len(ext_config.config), 1)
            self.assertEqual(list(ext_config.config.values())[0], ['serial-port2'])

    def test_serial_log_enabled_on_multiple_ports(self):
        sut = 'sut'
        ports = ['port1', 'port2']
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_PORTS, ports, entity=sut)
        config.set(SERIAL_ENABLED, True, entity=ports[0])
        config.set(SERIAL_ENABLED, True, entity=ports[1])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[0])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[1])

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(len(ext_config.config), 1)
            self.assertEqual(list(ext_config.config.values())[0], ['serial-port1', 'serial-port2'])

    def test_serial_log_enabled_only_on_second_port_for_single_sut(self):
        sut = 'sut'
        ports = ['port1', 'port2']
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_PORTS, ports, entity=sut)
        config.set(SERIAL_ENABLED, True, entity=ports[0])
        config.set(SERIAL_ENABLED, True, entity=ports[1])
        config.set(SERIAL_LOG_ENABLED, False, entity=ports[0])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[1])

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(len(ext_config.config), 1)
            self.assertEqual(list(ext_config.config.values())[0], ['serial-port2'])

    def test_serial_log_enabled_on_mix_of_ports_and_suts(self):
        suts = ['sut1', 'sut2']
        ports = ['port1', 'port2', 'port3', 'port4']
        config = ConfigManager()
        config.set(SUT, suts)
        config.set(SUT_SERIAL_PORTS, ports[0:2], entity=suts[0])
        config.set(SUT_SERIAL_PORTS, ports[2:4], entity=suts[1])
        config.set(SERIAL_ENABLED, True, entity=ports[0])
        config.set(SERIAL_ENABLED, True, entity=ports[1])
        config.set(SERIAL_ENABLED, True, entity=ports[2])
        config.set(SERIAL_ENABLED, True, entity=ports[3])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[0])
        config.set(SERIAL_LOG_ENABLED, False, entity=ports[1])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[2])
        config.set(SERIAL_LOG_ENABLED, True, entity=ports[3])

        with ExtensionTestHarness(SerialLogSourceExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertEqual(len(ext_config.config), 2)
            self.assertEqual(list(ext_config.config.values())[0], ['serial-port1'])
            self.assertEqual(list(ext_config.config.values())[1], ['serial-port3', 'serial-port4'])
