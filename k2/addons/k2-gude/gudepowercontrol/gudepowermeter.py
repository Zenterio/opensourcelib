"""
Provides Gude power meter functionality to K2.

It is implememented using the gude rest interface and can retrieve the power consumption
of the gude power switch, on individual power ports.

This extension implements the interface from :ref:`extension-powermeter` and responds to the
powermeter message POWER_METER_POWER.

It also provides a gude command that can be used to communicate with the power switch from the command line.
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
from powermeter import K2_POWER_METER_COMPONENT, POWER_METER, POWER_METER_POWER
from powermeter.powermeter import PowerMeter
from powermeter.powermetercommand import POWER_METER_COMMAND

from . import GUDE_IP, GUDE_PORT, GUDE_POWER_METER_ENDPOINT

logger = logging.getLogger(get_logger_name('k2', 'gude'))

GUDE_INDIVIDUAL_PORT_MEASUREMENTS = 8


class GudePowerMeterError(Exception):
    pass


@CommandExtension(
    name='gude',
    extends=[RUN_COMMAND, POWER_METER_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(POWER_METER, required=False),
        ConfigOption(GUDE_IP, required=False),
        ConfigOption(GUDE_PORT, required=False),
    ],
    endpoints_and_messages={GUDE_POWER_METER_ENDPOINT: [POWER_METER_POWER]},
    groups=['powermeter'],
)
class GudePowerMeterExtension(AbstractExtension):
    """Implementation of the gude functionality."""

    def __init__(self, config, instances):
        self.is_active = False
        if config.get(POWER_METER) == 'gude':
            self.gude_ip = config.get(GUDE_IP)
            self.gude_port = config.get(GUDE_PORT)

            if not self.configured():
                msg = "Error: Powermeter type is 'gude' but no 'gude.ip' and/or 'gude.port' is specified"
                raise (MissingConditionalConfigOption(msg))

            self.is_active = True
            self.entity = instances[SUT]
            self.gude = GudePowerMeter(self.gude_ip, self.gude_port)

    def register_components(self, component_manager):
        if self.is_active:
            sut = component_manager.get_unique_class_for_entity(self.entity)
            add_cans(sut, ['power_meter', 'gude'])

            @requires(sut='Sut', can=['gude', 'power_meter'])
            @requires(messagebus='MessageBus')
            @component(name=K2_POWER_METER_COMPONENT, can=['gude', 'power_meter'])
            def Gude(sut, messagebus):
                return PowerMeter(messagebus, sut.entity, GUDE_POWER_METER_ENDPOINT)

    def register_dispatchers(self, messagebus):
        if self.is_active:
            self.dispatcher = SequentialDispatcher(messagebus, self.handle_message)
            self.dispatcher.register(
                [POWER_METER_POWER], [GUDE_POWER_METER_ENDPOINT], entities=[self.entity])

    def configured(self):
        """Check if the Gude switch is configured."""
        return self.gude_ip is not None and self.gude_port is not None

    def destroy(self):
        if self.is_active:
            self.dispatcher.destroy()

    def handle_message(self, message):
        return {POWER_METER_POWER: self.gude.get_power_consumption}[message.message_id]()


class GudePowerMeter(object):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_power_consumption(self):
        """Check the power consumption of this instance of the gude power meter."""
        try:
            values = get_port_measurements(self.ip)[str(self.port)]
            return values['ActivePower']['value']
        except Exception:
            msg = 'Failed to get power consumption for port {port}'.format(port=self.port)
            logger.error(msg)
            raise GudePowerMeterError(msg)


def get_sensor_info(ip):
    import requests

    url = 'http://{ip}/statusjsn.js?components=81920'.format(ip=ip)
    try:
        try:
            response = requests.get(url)
        except Exception:
            response = requests.get(url)

        response.raise_for_status()
        return response.json()
    except Exception as e:
        msg = 'Gude http request failed'
        logger.debug(msg, exc_info=True)
        logger.error(msg)
        raise GudePowerMeterError(msg) from e


def get_sensor_descriptions(json):
    for desc in json['sensor_descr']:
        if desc['type'] == GUDE_INDIVIDUAL_PORT_MEASUREMENTS:
            return desc['fields']
    msg = 'No port sensor descriptions found'
    logger.warning(msg)
    raise GudePowerMeterError(msg)


def get_sensor_values(json):
    for value_data in json['sensor_values']:
        if value_data['type'] == GUDE_INDIVIDUAL_PORT_MEASUREMENTS:
            return value_data['values']
    msg = 'No port sensor values found'
    logger.warning(msg)
    raise GudePowerMeterError(msg)


def merge_sensor_descriptions_and_values(descriptions, values):
    state_per_port = {}
    for port, port_values in enumerate(values, start=1):
        state = {}
        for sensor, sensor_data in enumerate(descriptions):
            state[sensor_data['name']] = {
                'unit': sensor_data['unit'],
                'value': port_values[sensor]['v']
            }
        state_per_port[str(port)] = state
    return state_per_port


def get_port_measurements(ip):
    logger.info('Checking the power consumption of the Gude ports at {ip}'.format(ip=ip))

    sensor_info = get_sensor_info(ip)
    sensor_descriptions = get_sensor_descriptions(sensor_info)
    sensor_values = get_sensor_values(sensor_info)
    if not len(sensor_descriptions) == len(sensor_values[0]):
        msg = 'Mismatched number of sensor descriptions'
        logger.warning(msg)
        raise GudePowerMeterError(msg)

    logger.debug(
        'Got {num_descriptions} sensor descriptions for each of {num_ports} ports'.format(
            num_descriptions=len(sensor_descriptions), num_ports=len(sensor_values)))

    return merge_sensor_descriptions_and_values(sensor_descriptions, sensor_values)
