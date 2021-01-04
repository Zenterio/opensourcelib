from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

from k2.sut import SUT

SERIAL_ENDPOINT = EndpointId('zserial', 'Endpoint for the serial port messages')

SERIAL_CONNECTION_CHECK_ENDPOINT = EndpointId(
    'zserialcc', 'Endpoint for the serial connection check')

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

SERIAL_ENABLED = ConfigOptionId(
    'serial.enabled', 'Should serial be enabled', at=SUT, option_type=bool, default=False)

SERIAL_CONNECTION_CHECK_ENABLED = ConfigOptionId(
    'serialcc.enabled',
    'Should serial connection check be enabled',
    at=SUT,
    option_type=bool,
    default=True)

SERIAL_CONNECTION_CHECK_REQUIRED = ConfigOptionId(
    'serialcc.required',
    'Require serial connection to be working',
    at=SUT,
    option_type=bool,
    default=True)

SERIAL_BAUDRATE = ConfigOptionId(
    'serial.baudrate',
    'The baudrate of the serial connection',
    at=SUT,
    option_type=int,
    default=115200)

SERIAL_DEVICE = ConfigOptionId(
    'serial.device',
    'The serial device. Multiple formats supported e.g [ttyXXX, /dev/ttyXXX, 3-10.5.1, socket://127.0.0.1:2012, guess]',
    at=SUT)

SERIAL_TIMEOUT = ConfigOptionId(
    'serial.timeout',
    'Default timeout connecting to serial port',
    at=SUT,
    default=10,
    option_type=float)

SERIAL_PROMPT = ConfigOptionId(
    'serial.prompt', 'Regular expression matching the prompt of the SUT', at=SUT, default=r' # ')

SERIAL_FILTERS = ConfigOptionId(
    'serial.filters',
    'Regex matches that are used to filter out higher priority content from serial log lines',
    at=SUT,
    multiple=True,
    default=[r'###\ Error\ .*$', r'!!!Error\ .*$'])
