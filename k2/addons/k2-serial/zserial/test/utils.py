from zaf.application import APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.sut import SUT

from .. import SERIAL_BAUDRATE, SERIAL_DEVICE, SERIAL_ENABLED, SERIAL_FILTERS, SERIAL_PROMPT, \
    SERIAL_TIMEOUT
from ..serial import SerialExtension


def create_harness(
        enabled=True,
        sut=['entity'],
        device='device',
        filters=[],
        prompt=' #',
        baudrate=115200,
        timeout=10):

    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(SERIAL_ENABLED, enabled, entity=entity)
    config.set(SERIAL_DEVICE, device, entity=entity)
    config.set(SERIAL_FILTERS, filters, entity=entity)
    config.set(SERIAL_PROMPT, prompt, entity=entity)
    config.set(SERIAL_BAUDRATE, baudrate, entity=entity)
    config.set(SERIAL_TIMEOUT, timeout, entity=entity)

    return ExtensionTestHarness(
        SerialExtension,
        endpoints_and_messages={APPLICATION_ENDPOINT: [BEFORE_COMMAND]},
        config=config)
