r"""
Provides a common interface to access different types of power switches as well as the *powerswitch* command.

This extension doesn't really do anything itself but instead delegates to the actual power switch types.
Configuring power switch type is done with the :ref:`suts.\<ids\>.powerswitch <option-suts.\<ids\>.powerswitch>`
config option and the default value *none* means that there is no power switch for this sut.
"""

import json
import logging

from collections import OrderedDict
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Choice
from zaf.commands import JSON_OUTPUT
from zaf.commands.command import CommandId
from zaf.extensions.extension import FrameworkExtension, get_logger_name
from k2.sut import SUT

from powerswitch.powerswitch import PowerSwitch

logger = logging.getLogger(get_logger_name('k2', 'powerswitch'))


def power(core):
    """Execute commands to print or change state of a power switch for a sut."""
    subcommand = core.config.get(POWER_SUBCOMMAND)
    suts = core.config.get(SUT)
    result = OrderedDict()

    error_occurred = False
    for sut in suts:
        try:
            powerswitch = PowerSwitch(core.messagebus, sut, None)

            initial_state = powerswitch.state()

            if subcommand == 'state':
                result[sut] = {'state': 'ON' if initial_state else 'OFF', 'changed': False}
            elif subcommand == 'on':
                powerswitch.on()
                result[sut] = {'state': 'ON', 'changed': not initial_state}
            elif subcommand == 'off':
                powerswitch.off()
                result[sut] = {'state': 'OFF', 'changed': initial_state}
        except Exception:
            result[sut] = None
            logger.debug(
                'Error communicating with power switch for sut {sut}'.format(sut=sut),
                exc_info=True)
            error_occurred = True

    if core.config.get(JSON_OUTPUT, False):
        print(to_json(result))
    else:
        print(to_text(result, subcommand))

    return 1 if error_occurred else 0


def to_json(result):
    return json.dumps(result, indent=4)


def to_text(result, subcommand):
    text = ''
    for sut, sut_result in sorted(result.items()):
        if sut_result is None:
            text += 'ERROR: Could not get power state for sut {sut}\n'.format(sut=sut)

        elif subcommand == 'state':
            text += 'The power state of sut {sut} is {state}\n'.format(
                sut=sut, state=sut_result['state'])
        else:
            if sut_result['changed']:
                text += 'The power state of sut {sut} changed to {state}\n'.format(
                    sut=sut, state=sut_result['state'])
            else:
                text += 'The power state of sut {sut} was already {state}\n'.format(
                    sut=sut, state=sut_result['state'])
    return text


POWER_SUBCOMMAND = ConfigOptionId(
    'powerswitch.subcommand',
    'The subcommand to powerswitch',
    option_type=Choice(['state', 'on', 'off']),
    argument=True)

POWER_COMMAND = CommandId(
    'powerswitch',
    power.__doc__,
    power,
    config_options=[
        ConfigOption(POWER_SUBCOMMAND, required=True),
        ConfigOption(JSON_OUTPUT, required=False),
        ConfigOption(SUT, required=True)
    ])


@FrameworkExtension(
    'powerswitch',
    commands=[POWER_COMMAND],
    groups=['powerswitch'],
)
class PowerSwitchExtension(object):
    """Provides the power command."""

    def __init__(self, config, instances):
        pass
