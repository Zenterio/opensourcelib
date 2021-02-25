from unittest import TestCase
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from ..znail import SUT, ZNAIL_IP, ZNAIL_PORT, ZNAIL_TIMEOUT, Znail


class TestZnail(TestCase):

    @staticmethod
    def create_harness(extra_config=None):
        sut = Mock()
        sut.entity = 'mysut'
        config = ConfigManager()
        config.set(SUT, [sut.entity])
        config.set(ZNAIL_IP, '1.2.3.4', entity=sut.entity)

        for id, value in extra_config.items() if extra_config else []:
            config.set(id, value, entity=sut.entity, priority=2)

        harness = ExtensionTestHarness(
            Znail, config=config, components=[
                ComponentMock(name='Sut', mock=sut),
            ])
        return harness

    def test_extension_properties(self):
        with TestZnail.create_harness({
                ZNAIL_IP: '4.3.2.1',
                ZNAIL_PORT: 1234,
                ZNAIL_TIMEOUT: 20,
        }) as harness:
            assert harness.extension._entity == 'mysut'
            assert harness.extension.ip == '4.3.2.1'
            assert harness.extension.port == 1234
            assert harness.extension.timeout == 20

    def test_extension_registers_a_znail_instance_component(self):
        with TestZnail.create_harness() as harness:
            assert 'Znail' in harness.component_manager.COMPONENT_REGISTRY
            instance = harness.component_manager.COMPONENT_REGISTRY['Znail'][0]
            assert instance.ip == '1.2.3.4'
            assert instance.port == 80
            assert instance.timeout == 10

    def test_extension_does_not_register_a_znail_instance_component_if_no_ip_is_provided(self):
        with TestZnail.create_harness({ZNAIL_IP: None}) as harness:
            assert 'Znail' not in harness.component_manager.COMPONENT_REGISTRY
