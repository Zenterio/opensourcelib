import os

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption
from zaf.extensions.extension import FrameworkExtension

from k2.sut import SUT

from . import SERIAL_BAUDRATE, SERIAL_DEVICE
from .connection import find_serial_port


def serial(core):
    """Start a serial connection using picocom."""
    entity = core.config.get(SUT)[0]
    device = core.config.get(SERIAL_DEVICE, entity=entity)
    baudrate = core.config.get(SERIAL_BAUDRATE, entity=entity)

    port, _ = find_serial_port(device)

    os.system('picocom -b {baudrate} {port}'.format(baudrate=baudrate, port=port))


SERIAL_COMMAND = CommandId(
    'serial',
    serial.__doc__,
    serial,
    config_options=[
        ConfigOption(SUT, required=True),
        ConfigOption(SERIAL_DEVICE, required=True),
        ConfigOption(SERIAL_BAUDRATE, required=True),
    ])


@FrameworkExtension('zserial', commands=[SERIAL_COMMAND])
class SerialFrameworkExtension(object):
    """Provides the serial command."""

    def __init__(self, config, instances):
        pass
