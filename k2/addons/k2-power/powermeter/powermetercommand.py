r"""
Provides a common interface to access different types of power meters as well as the *powermeter* command.

This extension doesn't really do anything itself but instead delegates to the actual power meter types.
Configuring power meter type is done with the :ref:`suts.\<ids\>.powermeter <option-suts.\<ids\>.powermeter>`
config option and the default value *none* means that there is no power meter for this sut.
"""

import json
import logging
from collections import OrderedDict

from zaf.commands import JSON_OUTPUT
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption
from zaf.extensions.extension import FrameworkExtension, get_logger_name

from k2.sut import SUT
from powermeter.powermeter import PowerMeter

logger = logging.getLogger(get_logger_name('k2', 'powermeter'))
logger.addHandler(logging.NullHandler())


def power_meter(core):
    """Execute commands to print power consumption for a sut."""
    suts = core.config.get(SUT)
    result = OrderedDict()

    error_occurred = False
    for sut in suts:
        try:
            powermeter = PowerMeter(core.messagebus, sut, None)
            result[sut] = {'power': powermeter.power()}

        except Exception:
            result[sut] = None
            logger.debug(
                'Error communicating with power meter for sut {sut}'.format(sut=sut), exc_info=True)
            error_occurred = True

    if core.config.get(JSON_OUTPUT, False):
        print(to_json(result))
    else:
        print(to_text(result))

    return 1 if error_occurred else 0


def to_json(result):
    return json.dumps(result, indent=4)


def to_text(result):
    text = ''
    for sut, sut_result in sorted(result.items()):
        if sut_result is None:
            text += 'ERROR: Could not get power consumption for sut {sut}\n'.format(sut=sut)

        else:
            text += 'The power consumption of sut {sut} is {power} W\n'.format(
                sut=sut, power=sut_result['power'])
    return text


POWER_METER_COMMAND = CommandId(
    'powermeter',
    power_meter.__doc__,
    power_meter,
    config_options=[ConfigOption(JSON_OUTPUT, required=False),
                    ConfigOption(SUT, required=True)])


@FrameworkExtension(name='powermeter', commands=[POWER_METER_COMMAND], groups=['powermeter'])
class PowerMeterExtension(object):
    """Provides the powermeter command."""

    def __init__(self, config, instances):
        pass
