from zaf.config.options import ConfigOptionId

from k2.sut import SUT

from . import SERIAL_BAUDRATE, SERIAL_CONNECTION_CHECK_ENABLED, SERIAL_CONNECTION_CHECK_REQUIRED, \
    SERIAL_DEVICE, SERIAL_ENABLED, SERIAL_FILTERS, SERIAL_LOG_ENABLED, SERIAL_PORT_IDS, \
    SERIAL_PROMPT, SERIAL_TIMEOUT, SUT_SERIAL_PORTS

SUT_SERIAL_ENABLED = ConfigOptionId(
    'serial.enabled', 'Should serial port be enabled', at=SUT, option_type=bool, default=False)

SUT_SERIAL_LOG_ENABLED = ConfigOptionId(
    'serial.log',
    """\
    Should serial trigger LOG_LINE_RECEIVED events.

    LOG_LINE_RECEIVED events are used by other extensions (e.g. SutEvents) to provide additional
    functionality and components.""",
    at=SUT,
    option_type=bool,
    default=True)

SUT_SERIAL_CONNECTION_CHECK_ENABLED = ConfigOptionId(
    'serialcc.enabled',
    'Should serial connection check be enabled',
    at=SUT,
    option_type=bool,
    default=True)

SUT_SERIAL_CONNECTION_CHECK_REQUIRED = ConfigOptionId(
    'serialcc.required',
    'Require serial connection to be working',
    at=SUT,
    option_type=bool,
    default=True)

SUT_SERIAL_BAUDRATE = ConfigOptionId(
    'serial.baudrate', 'The baudrate of the serial port.', at=SUT, option_type=int, default=115200)

SUT_SERIAL_DEVICE = ConfigOptionId(
    'serial.device',
    'The serial device. Multiple formats supported e.g [ttyXXX, /dev/ttyXXX, 3-10.5.1, socket://127.0.0.1:2012, guess]',
    at=SUT)

SUT_SERIAL_TIMEOUT = ConfigOptionId(
    'serial.timeout',
    'Default timeout connecting to serial port',
    at=SUT,
    default=10,
    option_type=float)

SUT_SERIAL_PROMPT = ConfigOptionId(
    'serial.prompt', 'Regular expression matching the prompt of the SUT', at=SUT, default=r' # ')

SUT_SERIAL_FILTERS = ConfigOptionId(
    'serial.filters',
    'Regex matches that are used to filter out higher priority content from serial log lines',
    at=SUT,
    multiple=True,
    default=[r'###\ Error\ .*$', r'!!!Error\ .*$'])


def add_sut_options_to_extension_config(sut, extension_config, config_manager):
    option_map = {
        SUT_SERIAL_ENABLED: SERIAL_ENABLED,
        SUT_SERIAL_LOG_ENABLED: SERIAL_LOG_ENABLED,
        SUT_SERIAL_CONNECTION_CHECK_ENABLED: SERIAL_CONNECTION_CHECK_ENABLED,
        SUT_SERIAL_CONNECTION_CHECK_REQUIRED: SERIAL_CONNECTION_CHECK_REQUIRED,
        SUT_SERIAL_BAUDRATE: SERIAL_BAUDRATE,
        SUT_SERIAL_DEVICE: SERIAL_DEVICE,
        SUT_SERIAL_TIMEOUT: SERIAL_TIMEOUT,
        SUT_SERIAL_PROMPT: SERIAL_PROMPT,
        SUT_SERIAL_FILTERS: SERIAL_FILTERS,
    }

    try:
        extension_config[SERIAL_PORT_IDS.key].append(sut)
    except KeyError:
        extension_config[SERIAL_PORT_IDS.key] = [sut]
    # sut.<sut>.serial.ports: (sut)
    extension_config['.'.join([SUT_SERIAL_PORTS.namespace, sut, SUT_SERIAL_PORTS.name])] = [sut]

    for old, new in option_map.items():
        new_option_key = '.'.join([SERIAL_PORT_IDS.namespace, sut, new.name])
        extension_config[new_option_key] = config_manager.get(old, entity=sut)
