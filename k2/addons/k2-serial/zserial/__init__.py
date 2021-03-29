from zaf.config.options import ConfigOptionId
from zaf.config.types import Entity
from zaf.messages.message import EndpointId, MessageId

from k2.sut import SUT

SERIAL_ENDPOINT = EndpointId('zserial', 'Endpoint for the serial port messages')

SERIAL_CONNECTION_CHECK_ENDPOINT = EndpointId(
    'zserialcc', 'Endpoint for each serial port connection check')

SERIAL_SEND_COMMAND = MessageId(
    'SERIAL_SEND_COMMAND', """\
    Sends a command on the serial port
    """)

SERIAL_CONNECTED = MessageId(
    'SERIAL_CONNECTED', """\
    An event that is sent when a serial port is connected
    """)

SERIAL_CONNECTION_LOST = MessageId(
    'SERIAL_CONNECTION_LOST', """\
    An event that is sent when the serial connection is lost
    """)

SERIAL_RECONNECT = MessageId(
    'SERIAL_RECONNECT', """\
    Trigger a reconnect of the serial connection
    """)

SERIAL_SUSPEND = MessageId(
    'SERIAL_SUSPEND', """\
    Suspends log line handling and returns a reference to the serial port. This
    can be used when raw byte access is temporarily needed. The log line
    handling is resumed with SERIAL_RESUME.

    NOTE: This behavior is not thread safe. If multiple components try to
          suspend the same serial connection at the same time, an exception
          will be raised.
    """)

SERIAL_RESUME = MessageId(
    'SERIAL_RESUME', """\
    Resumes line handling of the serial port. Counterpart of SERIAL_SUSPEND.
    An exception will be raised if the serial port was not already suspended.
    """)

SERIAL_RAW_LINE = MessageId(
    'SERIAL_RAW_LINE', """\
    An event with a raw line that is read directly from the serial connection
    """)

SERIAL_PORT_IDS = ConfigOptionId(
    'ids',
    'Identifies a serial port',
    namespace='serial.port',
    entity=True,
    multiple=True,
    option_type=Entity())

SERIAL_ENABLED = ConfigOptionId(
    'enabled', 'Should serial port be enabled', at=SERIAL_PORT_IDS, option_type=bool, default=False)

SERIAL_LOG_ENABLED = ConfigOptionId(
    'log',
    """\
    Should serial trigger LOG_LINE_RECEIVED events.

    LOG_LINE_RECEIVED events are used by other extensions (e.g. SutEvents) to provide additional
    functionality and components.""",
    at=SERIAL_PORT_IDS,
    option_type=bool,
    default=True)

SERIAL_CONNECTION_CHECK_ENABLED = ConfigOptionId(
    'cc.enabled',
    'Should serial port connection check be enabled',
    at=SERIAL_PORT_IDS,
    option_type=bool,
    default=True)

SERIAL_CONNECTION_CHECK_REQUIRED = ConfigOptionId(
    'cc.required',
    'Require serial port to be working',
    at=SERIAL_PORT_IDS,
    option_type=bool,
    default=True)

SERIAL_BAUDRATE = ConfigOptionId(
    'baudrate',
    'The baudrate of the serial port.',
    at=SERIAL_PORT_IDS,
    option_type=int,
    default=115200)

SERIAL_DEVICE = ConfigOptionId(
    'device',
    """\
    The physical device for the serial port.
    Multiple formats are supported e.g.:
    * ttyXXX,
    * /dev/ttyXXX,
    * 3-10.5.1,
    * socket://127.0.0.1:2012,
    * guess
    """,
    at=SERIAL_PORT_IDS)

SERIAL_TIMEOUT = ConfigOptionId(
    'timeout',
    'Default timeout connecting to serial port',
    at=SERIAL_PORT_IDS,
    default=10,
    option_type=float)

SERIAL_PROMPT = ConfigOptionId(
    'prompt',
    'Regular expression matching the prompt of the serial port',
    at=SERIAL_PORT_IDS,
    default=r' # ')

SERIAL_FILTERS = ConfigOptionId(
    'filters',
    'Regex matches that are used to filter out higher priority content from serial log lines',
    at=SERIAL_PORT_IDS,
    multiple=True,
    default=[r'###\ Error\ .*$', r'!!!Error\ .*$'])

SUT_SERIAL_PORTS = ConfigOptionId(
    'serial.ports',
    'Serial ports available for this sut',
    at=SUT,
    multiple=True,
    option_type=Entity())
