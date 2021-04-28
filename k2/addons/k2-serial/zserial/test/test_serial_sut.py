from unittest import TestCase
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.component.manager import ComponentManager
from zaf.config import MissingConditionalConfigOption
from zaf.config.manager import ConfigManager

from k2.sut import SUT
from k2.sut.log import SUT_LOG_SOURCES

from .. import SERIAL_DEVICE, SERIAL_ENABLED, SERIAL_PORT_IDS, SUT_SERIAL_PORTS
from ..serial import SerialFrameworkExtension
from ..sut import SUT_SERIAL_DEVICE, SUT_SERIAL_ENABLED, SUT_SERIAL_LOG_ENABLED


def config_key(config_id, entity):
    return '.'.join([config_id.namespace, entity, config_id.name])


class TestSerialSutOptions(TestCase):

    def setUp(self):
        ComponentManager().clear_component_registry()

    def test_sut_serial_enabled_adds_serial_port(self):
        sut = 'sut'
        device = '/dev/null'
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_ENABLED, True, entity=sut)
        config.set(SUT_SERIAL_DEVICE, device, entity=sut)

        with ExtensionTestHarness(SerialFrameworkExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertNotEqual(len(ext_config.config), 0)
            self.assertEqual(ext_config.config[SERIAL_PORT_IDS.key], [sut])
            self.assertEqual(ext_config.config[config_key(SERIAL_ENABLED, sut)], True)
            self.assertEqual(ext_config.config[config_key(SERIAL_DEVICE, sut)], device)

    def test_sut_serial_log_enabled_adds_log_source(self):
        sut = 'sut'
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_ENABLED, True, entity=sut)
        config.set(SUT_SERIAL_DEVICE, '/dev/null', entity=sut)
        config.set(SUT_SERIAL_LOG_ENABLED, True, entity=sut)

        with ExtensionTestHarness(SerialFrameworkExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertGreater(len(ext_config.config), 0)
            self.assertEqual(ext_config.config[SERIAL_PORT_IDS.key], [sut])
            self.assertEqual(ext_config.config[config_key(SUT_LOG_SOURCES, sut)], ['serial-sut'])

    def test_mix_sut_and_port_id_options_raises_exception(self):
        sut = 'sut'
        port = 'port'
        config = ConfigManager()
        config.set(SUT, [sut])
        config.set(SUT_SERIAL_ENABLED, True, entity=sut)
        config.set(SUT_SERIAL_DEVICE, '/dev/null', entity=sut)
        config.set(SUT_SERIAL_PORTS, [port], entity=sut)
        config.set(SERIAL_ENABLED, True, entity=port)

        with ExtensionTestHarness(SerialFrameworkExtension, config=config) as harness, \
                self.assertRaises(MissingConditionalConfigOption):
            harness.extension.get_config(config, Mock(), Mock())

    def test_multiple_suts_adds_multiple_serial_ports(self):
        suts = ['sut1', 'sut2']
        devices = ['/dev/device1', '/dev/device2']
        config = ConfigManager()
        config.set(SUT, suts)
        config.set(SUT_SERIAL_ENABLED, True, entity=suts[0])
        config.set(SUT_SERIAL_DEVICE, devices[0], entity=suts[0])
        config.set(SUT_SERIAL_ENABLED, True, entity=suts[1])
        config.set(SUT_SERIAL_DEVICE, devices[1], entity=suts[1])

        with ExtensionTestHarness(SerialFrameworkExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertNotEqual(len(ext_config.config), 0)
            self.assertEqual(ext_config.config[SERIAL_PORT_IDS.key], suts)
            self.assertEqual(ext_config.config[config_key(SERIAL_ENABLED, suts[0])], True)
            self.assertEqual(ext_config.config[config_key(SERIAL_ENABLED, suts[1])], True)
            self.assertEqual(ext_config.config[config_key(SERIAL_DEVICE, suts[0])], devices[0])
            self.assertEqual(ext_config.config[config_key(SERIAL_DEVICE, suts[1])], devices[1])

    def test_multiple_suts_only_adds_enabled_serial_ports(self):
        suts = ['sut1', 'sut2', 'sut3']
        devices = ['/dev/device1', '/dev/device3']
        config = ConfigManager()
        config.set(SUT, suts)
        config.set(SUT_SERIAL_ENABLED, True, entity=suts[0])
        config.set(SUT_SERIAL_ENABLED, False, entity=suts[1])
        config.set(SUT_SERIAL_ENABLED, True, entity=suts[2])
        config.set(SUT_SERIAL_DEVICE, devices[0], entity=suts[0])
        config.set(SUT_SERIAL_DEVICE, devices[1], entity=suts[2])

        with ExtensionTestHarness(SerialFrameworkExtension, config=config) as harness:
            ext_config = harness.extension.get_config(config, Mock(), Mock())
            self.assertNotEqual(len(ext_config.config), 0)
            self.assertEqual(ext_config.config[SERIAL_PORT_IDS.key], ['sut1', 'sut3'])
            self.assertEqual(ext_config.config[config_key(SERIAL_ENABLED, suts[0])], True)
            self.assertEqual(ext_config.config[config_key(SERIAL_ENABLED, suts[2])], True)
            self.assertEqual(ext_config.config[config_key(SERIAL_DEVICE, suts[0])], devices[0])
            self.assertEqual(ext_config.config[config_key(SERIAL_DEVICE, suts[2])], devices[1])
            with self.assertRaises(KeyError):
                ext_config.config[config_key(SERIAL_ENABLED, suts[1])]
