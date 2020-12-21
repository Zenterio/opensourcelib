"""
SiS-PM (Silver Shield PM) Control for K2.

This component simply wraps the sispmctl command with the proper switches for controlling a power outlet.
"""

import logging
import subprocess

from zaf.component.decorator import component, requires
from zaf.component.util import add_cans
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, ExtensionConfig, \
    FrameworkExtension, get_logger_name
from zaf.messages.dispatchers import SequentialDispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from powerswitch import AVAILABLE_POWER_SWITCHES, K2_POWER_COMPONENT, POWER_SWITCH, \
    POWER_SWITCH_POWER_STATE, POWER_SWITCH_POWEROFF, POWER_SWITCH_POWERON
from powerswitch.powercommand import POWER_COMMAND
from powerswitch.powerswitch import PowerSwitch

from . import SISPM_DEVICE, SISPM_OUTLET, SISPM_POWER_SWITCH_ENDPOINT

logger = logging.getLogger(get_logger_name('k2', 'sispmpowerswitch'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='sispmpowerswitch',
    extends=[RUN_COMMAND, POWER_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(POWER_SWITCH, required=False),
        ConfigOption(SISPM_DEVICE, required=False),
        ConfigOption(SISPM_OUTLET, required=False),
    ],
    endpoints_and_messages={
        SISPM_POWER_SWITCH_ENDPOINT:
        [POWER_SWITCH_POWER_STATE, POWER_SWITCH_POWERON, POWER_SWITCH_POWEROFF]
    },
    groups=['powerswitch'],
)
class SispmPowerSwitch(AbstractExtension):
    """SiS-PM power switch."""

    def __init__(self, config, instances):
        self.is_active = False
        if config.get(POWER_SWITCH) == 'sispm':
            self.is_active = True
            self.entity = instances[SUT]
            self.device = config.get(SISPM_DEVICE)
            self.outlet = config.get(SISPM_OUTLET)
            self.dispatcher = None

    def register_components(self, component_manager):
        if self.is_active:
            sut = component_manager.get_unique_class_for_entity(self.entity)
            add_cans(sut, ['power_switch'])

            @requires(sut='Sut', can=['power_switch'])
            @requires(messagebus='MessageBus')
            @component(name=K2_POWER_COMPONENT, can=['power_switch'])
            def Sispm(sut, messagebus):
                return PowerSwitch(messagebus, sut.entity, SISPM_POWER_SWITCH_ENDPOINT)

    def register_dispatchers(self, messagebus):
        if self.is_active:
            self.dispatcher = SequentialDispatcher(messagebus, self.handle_message)
            self.dispatcher.register(
                [POWER_SWITCH_POWER_STATE, POWER_SWITCH_POWERON, POWER_SWITCH_POWEROFF],
                [SISPM_POWER_SWITCH_ENDPOINT],
                entities=[self.entity])

    def destroy(self):
        if self.is_active and self.dispatcher is not None:
            self.dispatcher.destroy()
            self.dispatcher = None

    def handle_message(self, message):
        return {
            POWER_SWITCH_POWER_STATE: self.get_state,
            POWER_SWITCH_POWEROFF: self.turn_off,
            POWER_SWITCH_POWERON: self.turn_on
        }[message.message_id]()

    def get_state(self):
        """Return current relay state."""
        return self._run_sispmctl(switch='-g')

    def turn_on(self):
        """Turn on relay."""
        self._run_sispmctl(switch='-o')

    def turn_off(self):
        """Turn off relay."""
        self._run_sispmctl(switch='-f')

    def _run_sispmctl(self, switch):
        command = [
            'sispmctl', '-q', '-n', '-d', '{device}'.format(device=self.device), switch,
            '{outlet}'.format(outlet=self.outlet)
        ]
        stdout = subprocess.check_output(command)
        return True if b'1' in stdout else False if b'0' in stdout else None


@FrameworkExtension(name='sispmpowerswitch', groups=['powerswitch'])
class SispmPowerSwitchFrameworkExtension(object):
    """Provides the sispmpowerswitch command."""

    def __init__(self, config, instances):
        pass

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig({AVAILABLE_POWER_SWITCHES.name: ['sispm']}, 1, 'sispmpowerswitch')
