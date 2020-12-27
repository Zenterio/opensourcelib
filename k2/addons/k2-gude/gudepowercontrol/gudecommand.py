import json
import logging
from collections import OrderedDict

from zaf.commands import JSON_OUTPUT
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Choice
from zaf.extensions.extension import ExtensionConfig, FrameworkExtension, get_logger_name

from powermeter import AVAILABLE_POWER_METERS
from powerswitch import AVAILABLE_POWER_SWITCHES

from .gudepowermeter import GudePowerMeter
from .gudepowerswitch import GudePowerSwitch, power_states

logger = logging.getLogger(get_logger_name('k2', 'gude'))


def gude(core):
    """
    Measure power consumption and print or change state of a gude power switch.

    Given an IP adress of a gude switch, this command allows for printing or
    changing the state of ports. Additionally, if the gude switch supports it,
    the power consumption of a port can be measured.

    Example to get the state of one port::

        zk2 gude --ip a.b.c.d --port 4 state

    Example to power on multiple ports::

        zk2 gude --ip a.b.c.d --port 4 --port 6 on

    Example to power off all ports::

        zk2 gude --ip a.b.c.d off

    Example to get power consumption of one port::

        zk2 gude --ip a.b.c.d power
    """
    subcommand = core.config.get(GUDE_SUBCOMMAND)
    ip = core.config.get(GUDE_IP)
    ports = [str(port) for port in core.config.get(GUDE_PORTS)]

    result = OrderedDict()

    try:
        powercommand = True if subcommand == 'power' else False
        states_per_port = power_states(ip)

        for port in ports if ports else states_per_port.keys():
            if powercommand:
                gude = GudePowerMeter(ip, port)
                result[port] = {'power': gude.get_power_consumption()}
            else:
                gude = GudePowerSwitch(ip, port)
                initial_state = states_per_port[port]

                if subcommand == 'state':
                    result[port] = {'state': 'ON' if initial_state else 'OFF', 'changed': False}
                elif subcommand == 'on':
                    gude.on()
                    result[port] = {'state': 'ON', 'changed': not initial_state}
                elif subcommand == 'off':
                    gude.off()
                    result[port] = {'state': 'OFF', 'changed': initial_state}

        if core.config.get(JSON_OUTPUT, False):
            print(to_json(result))
        else:
            print(to_text(result, subcommand))

    except Exception:
        msg = 'Error communicating with Gude port for {ip}'.format(ip=ip)
        logger.debug(msg, exc_info=True)
        print(msg)
        return 1
    return 0


def to_json(result):
    return json.dumps(result, indent=4)


def to_text(result, subcommand):
    text = ''
    for port, port_result in sorted(result.items(), key=lambda result: int(result[0])):
        if subcommand == 'state':
            text += 'The power state of port {port} is {state}\n'.format(
                port=port, state=port_result['state'])
        elif subcommand == 'power':
            text += 'The power consumption of port {port} is {power} W\n'.format(
                port=port, power=port_result['power'])
        else:
            if port_result['changed']:
                text += 'The power state of port {port} changed to {state}\n'.format(
                    port=port, state=port_result['state'])
            else:
                text += 'The power state of port {port} was already {state}\n'.format(
                    port=port, state=port_result['state'])
    return text


GUDE_SUBCOMMAND = ConfigOptionId(
    'subcommand',
    'The subcommand to gude',
    option_type=Choice(['state', 'on', 'off', 'power']),
    argument=True)

GUDE_IP = ConfigOptionId('ip', 'The gude IP')

GUDE_PORTS = ConfigOptionId(
    'port',
    'The gude port number. Can be given multiple times to specify multiple ports. ',
    option_type=int,
    multiple=True)

GUDE_COMMAND = CommandId(
    'gude',
    gude.__doc__,
    gude,
    config_options=[
        ConfigOption(GUDE_SUBCOMMAND, required=True),
        ConfigOption(GUDE_IP, required=True),
        ConfigOption(GUDE_PORTS, required=False),
        ConfigOption(JSON_OUTPUT, required=False),
    ])


@FrameworkExtension('gude', commands=[GUDE_COMMAND], groups=['powerswitch', 'powermeter'])
class GudeFrameworkExtension(object):
    """Provides the gude command."""

    def __init__(self, config, instances):
        pass

    def get_config(self, config, requested_config_options, requested_command_config_options):
        return ExtensionConfig(
            {
                AVAILABLE_POWER_SWITCHES.name: ['gude'],
                AVAILABLE_POWER_METERS.name: ['gude']
            }, 1, 'gude')
