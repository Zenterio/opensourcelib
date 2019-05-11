"""Dummy power meter that will always return 4.2 W."""

import logging

from zaf.component.decorator import component, requires
from zaf.component.util import add_cans
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, ExtensionConfig, \
    FrameworkExtension, get_logger_name
from zaf.messages.dispatchers import SequentialDispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from powermeter import AVAILABLE_POWER_METERS, K2_POWER_METER_COMPONENT, POWER_METER, \
    POWER_METER_POWER
from powermeter.powermeter import PowerMeter
from powermeter.powermetercommand import POWER_METER_COMMAND

from . import DUMMY_POWER_METER_ENDPOINT, DUMMY_POWER_METER_VALUE

logger = logging.getLogger(get_logger_name('k2', 'dummypowermeter'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='dummypowermeter',
    extends=[RUN_COMMAND, POWER_METER_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(POWER_METER, required=False),
        ConfigOption(DUMMY_POWER_METER_VALUE, required=False)
    ],
    endpoints_and_messages={DUMMY_POWER_METER_ENDPOINT: [POWER_METER_POWER]},
    groups=['powermeter'],
)
class DummyPowerMeter(AbstractExtension):
    """Dummy power meter."""

    def __init__(self, config, instances):
        self.is_active = False
        if config.get(POWER_METER) == 'dummy':
            self.is_active = True
            self.entity = instances[SUT]
            self.value = config.get(DUMMY_POWER_METER_VALUE)

    def register_components(self, component_manager):
        if self.is_active:
            sut = component_manager.get_unique_class_for_entity(self.entity)
            add_cans(sut, ['power_meter'])

            @requires(sut='Sut', can=['power_meter'])
            @requires(messagebus='MessageBus')
            @component(name=K2_POWER_METER_COMPONENT, can=['power_meter'])
            def Dummy(sut, messagebus):
                return PowerMeter(messagebus, sut.entity, DUMMY_POWER_METER_ENDPOINT)

    def register_dispatchers(self, messagebus):
        if self.is_active:
            self.dispatcher = SequentialDispatcher(messagebus, self.handle_message)
            self.dispatcher.register(
                [POWER_METER_POWER], [DUMMY_POWER_METER_ENDPOINT], entities=[self.entity])

    def destroy(self):
        if self.is_active:
            self.dispatcher.destroy()

    def handle_message(self, message):
        return {POWER_METER_POWER: self.get_power_consumption}[message.message_id]()

    def get_power_consumption(self):
        """Return dummy value."""
        return self.value


@FrameworkExtension(name='dummypowermeter', groups=['powermeter'])
class DummyPowerMeterFrameworkExtension(object):
    """Provides the dummypowermeter command."""

    def __init__(self, config, instances):
        pass

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig({AVAILABLE_POWER_METERS.name: ['dummy']}, 1, 'dummypowermeter')
