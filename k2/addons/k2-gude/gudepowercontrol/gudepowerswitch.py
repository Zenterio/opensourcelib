"""
Provides Gude power switch functionality to K2.

It is implememented using the gude rest interface and can retrieve the state of the
gude powerswitch and set the power to on and off.

This extension implements the interface from :ref:`extension-powerswitch` and responds to the
powerswitch messages POWER_SWITCH_POWERON, POWER_SWITCH_POWEROFF and POWER_SWITCH_POWER_STATE.

It also provides a gude command that can be used to communicate with the powerswitch from the command line.
"""

import logging

from zaf.component.decorator import component, requires
from zaf.component.util import add_cans
from zaf.config import MissingConditionalConfigOption
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.dispatchers import SequentialDispatcher

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from powerswitch import K2_POWER_COMPONENT, POWER_SWITCH, POWER_SWITCH_POWER_STATE, \
    POWER_SWITCH_POWEROFF, POWER_SWITCH_POWERON
from powerswitch.powercommand import POWER_COMMAND
from powerswitch.powerswitch import PowerSwitch

from . import GUDE_IP, GUDE_PORT, GUDE_POWER_SWITCH_ENDPOINT, GudePowerState

logger = logging.getLogger(get_logger_name('k2', 'gude'))


@CommandExtension(
    name='gude',
    extends=[RUN_COMMAND, POWER_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(POWER_SWITCH, required=False),
        ConfigOption(GUDE_IP, required=False),
        ConfigOption(GUDE_PORT, required=False),
    ],
    endpoints_and_messages={
        GUDE_POWER_SWITCH_ENDPOINT:
        [POWER_SWITCH_POWERON, POWER_SWITCH_POWEROFF, POWER_SWITCH_POWER_STATE]
    },
    groups=['powerswitch'],
)
class GudePowerSwitchExtension(AbstractExtension):
    """Implementation of the gude functionality."""

    def __init__(self, config, instances):
        self.is_active = False
        if config.get(POWER_SWITCH) == 'gude':
            self.gude_ip = config.get(GUDE_IP)
            self.gude_port = config.get(GUDE_PORT)

            if not self.configured():
                msg = "Error: Powerswitch type is 'gude' but no 'gude.ip' and/or 'gude.port' is specified"
                raise (MissingConditionalConfigOption(msg))

            self.is_active = True
            self.entity = instances[SUT]
            self.gude = GudePowerSwitch(self.gude_ip, self.gude_port)

    def register_components(self, component_manager):
        if self.is_active:
            sut = component_manager.get_unique_class_for_entity(self.entity)
            add_cans(sut, ['power', 'gude'])

            @requires(sut='Sut', can=['gude', 'power'])
            @requires(messagebus='MessageBus')
            @component(name=K2_POWER_COMPONENT, can=['gude', 'power'])
            def Gude(sut, messagebus):
                return PowerSwitch(messagebus, sut.entity, GUDE_POWER_SWITCH_ENDPOINT)

    def register_dispatchers(self, messagebus):
        if self.is_active:
            self.dispatcher = SequentialDispatcher(messagebus, self.handle_message)
            self.dispatcher.register(
                [POWER_SWITCH_POWERON, POWER_SWITCH_POWEROFF, POWER_SWITCH_POWER_STATE],
                [GUDE_POWER_SWITCH_ENDPOINT],
                entities=[self.entity])

    def configured(self):
        """Check if the Gude switch is configured."""
        return self.gude_ip is not None and self.gude_port is not None

    def destroy(self):
        if self.is_active:
            self.dispatcher.destroy()

    def handle_message(self, message):
        return {
            POWER_SWITCH_POWERON: self.gude.on,
            POWER_SWITCH_POWEROFF: self.gude.off,
            POWER_SWITCH_POWER_STATE: self.gude.power_state,
        }[message.message_id]()


class GudePowerSwitch(object):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def on(self):
        """Turn on Gude port."""
        self._set_power_state(GudePowerState.ON)

    def off(self):
        """Turn off Gude port."""
        self._set_power_state(GudePowerState.OFF)

    def power_state(self):
        """Check the power state of this instance of the gude switch."""

        on = power_states(self.ip)[str(self.port)]
        if on:
            logger.info('Power is on for Gude port {ip}:{port}'.format(ip=self.ip, port=self.port))
        else:
            logger.info('Power is off for Gude port {ip}:{port}'.format(ip=self.ip, port=self.port))

        return on

    def _set_power_state(self, wanted_state):
        import requests
        """Private method uses http request to control Gude."""
        logger.info(
            'Setting state of Gude {ip}:{port} to {state}'.format(
                ip=self.ip, port=self.port, state=wanted_state))

        url = 'http://{ip}/?cmd=1&p={port}&s={state}'.format(
            ip=self.ip, port=self.port, state=wanted_state.value)

        try:
            response = requests.get(url)
        except Exception:
            response = requests.get(url)

        response.raise_for_status()
        logger.info(
            'Setting state of Gude {ip}:{port} to {state} was successful'.format(
                ip=self.ip, port=self.port, state=wanted_state))


def power_states(ip):
    import requests

    logger.info('Checking the power state of the Gude ports at {ip}'.format(ip=ip))

    url = 'http://{ip}/statusjsn.js?components=1'.format(ip=ip)
    try:
        response = requests.get(url)
    except Exception:
        response = requests.get(url)

    response.raise_for_status()

    state_per_port = {}
    for port, port_data in enumerate(response.json()['outputs'], start=1):
        state_per_port[str(port)] = port_data['state'] == 1

    return state_per_port
