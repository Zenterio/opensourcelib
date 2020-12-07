import logging
import subprocess
from tempfile import mktemp

from serial import Serial
from zaf.component.decorator import component
from zaf.extensions.extension import CommandExtension, get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'serialmock'))
logger.addHandler(logging.NullHandler())


@CommandExtension('serialmock')
class SerialMockExtension(object):
    pass


@component(name='VirtualSerialConnection')
class VirtualSerialConnection(object):

    def __init__(self):
        self._local_device = mktemp('virtual_serial_connection')
        self._device = mktemp('virtual_serial_connection')

        self._local_device_options = [
            'pty', 'raw', 'echo=0', 'link={link}'.format(link=self._local_device)
        ]
        self._device_options = ['pty', 'raw', 'echo=0', 'link={link}'.format(link=self._device)]

    @property
    def device(self):
        return self._device

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def disconnect(self):
        self.process.kill()
        self.serial.close()

    def connect(self):
        self.process = subprocess.Popen(
            [
                'socat', '-d', '-d', ','.join(self._local_device_options), ','.join(
                    self._device_options)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)
        # Read three lines to wait for connection to be open before connecting serial
        self.process.stderr.readline()
        self.process.stderr.readline()
        self.process.stderr.readline()
        self.serial = Serial(self._local_device, 9600, timeout=2)

    def readline(self):
        line = self.serial.readline().decode('utf-8').strip()
        logger.info('Line read: {line}'.format(line=line))
        return line

    def writeline(self, line):
        logger.info('Writing line: {line}'.format(line=line))
        self.serial.write('{line}\r\n'.format(line=line).encode('utf-8'))
