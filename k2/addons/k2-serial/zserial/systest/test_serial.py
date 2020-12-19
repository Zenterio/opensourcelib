import subprocess
import time

from zaf.component.decorator import requires
from zaf.messages.message import EndpointId

from k2.sut import SUT_RECOVERY_PERFORM

SYSTEST = EndpointId('systest', 'systest endpoint')


@requires(zk2='Zk2')
def test_serial_filter_out_command_response(zk2, VirtualSerialConnection):

    with VirtualSerialConnection() as serial:
        process = zk2(
            [
                'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'textreport', 'zserial'
            ],
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@serial-enabled true '
            '--suts-box@serial-device {device} --suts-box@serial-baudrate 9600 '
            'zserial.systest.data.suites.test_serial:test_serial_can_filter_out_command_results'.
            format(device=serial.device),
            wait=False)
        try:
            command = None
            while not command:
                command = serial.readline()
            for line in subprocess.check_output(command, shell=True,
                                                universal_newlines=True).strip().split('\n'):
                serial.writeline('random stuff')
                serial.writeline(line)
        finally:
            process.wait(timeout=10)

        assert 'Passed:  1' in process.stdout


@requires(zk2='Zk2')
def test_serial_client_timeout_error(zk2, VirtualSerialConnection):

    with VirtualSerialConnection() as serial:
        process = zk2(
            [
                'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'textreport', 'zserial'
            ],
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@serial-enabled true '
            '--suts-box@serial-device {device} --suts-box@serial-baudrate 9600 '
            'zserial.systest.data.suites.test_serial:test_serial_timeout'.format(
                device=serial.device),
            wait=False)

        try:
            serial.readline()
            for i in range(0, 5):
                serial.writeline('random stuff')
                time.sleep(0.1)
        finally:
            process.wait(timeout=10)

        assert 'Passed:  1' in process.stdout


@requires(zk2='Zk2')
def test_serial_connection_reestablished(zk2, VirtualSerialConnection):
    with VirtualSerialConnection() as serial:
        process = zk2(
            [
                'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'textreport', 'zserial'
            ],
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@serial-enabled true '
            '--suts-box@serial-device {device} --suts-box@serial-baudrate 9600 '
            'zserial.systest.data.suites.test_serial:test_connection_reestablished'.format(
                device=serial.device),
            wait=False)

        try:
            # waiting for k2 to enter the testcase
            command = None
            while not command:
                command = serial.readline()
            assert command == 'disconnect'

            serial.disconnect()
            serial.connect()

        finally:
            process.wait(timeout=10)

        assert 'Passed:  1' in process.stdout


@requires(zk2='Zk2')
def test_serial_containing_input_overrun_errors(zk2, VirtualSerialConnection):

    with VirtualSerialConnection() as serial:
        process = zk2(
            [
                'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'textreport', 'zserial'
            ],
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@serial-enabled true '
            '--suts-box@serial-device {device} --suts-box@serial-baudrate 9600 '
            'zserial.systest.data.suites.test_serial:test_read_from_serial'.format(
                device=serial.device),
            wait=False)

        try:
            command = None
            while not command:
                command = serial.readline()
            serial.writeline('ttyS0: 42 input overrun(s)')
        finally:
            process.wait(timeout=15)

        assert 'TTY input overrun. 42 characters were dropped.' in process.stdout


@requires(zk2='Zk2')
@requires(remote_client='SystestRemoteClient')
def test_sut_recovery_initiated_when_serial_connection_check_fails(
        zk2, VirtualSerialConnection, remote_client):
    """
    Tests that the serial connection check can fail and that SUT_RECOVER_PERFORM is triggered.

    This is triggered by using a short timeout and not responding to serial communication from the
    serial connection check.
    """
    with VirtualSerialConnection() as serial:
        process = zk2(
            [
                'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'zserial',
                'zserialcc', 'connectioncheck', 'remote'
            ],
            '--remote-enabled true '
            '--remote-port {remote_port} '
            '--log-debug k2.extension.zserial '
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@serial-enabled true '
            '--suts-box@serial-device {device} --suts-box@serial-baudrate 9600 '
            '--suts-box@serial-timeout 0.1 '
            '--suts-box@serialcc-enabled true '
            'zserial.systest.data.suites.test_minimal'.format(
                remote_port=remote_client.port, device=serial.device),
            wait=False)
        try:
            with remote_client.client() as client:
                client.define_endpoints_and_messages({SYSTEST: [SUT_RECOVERY_PERFORM]})
                with client.local_message_queue([SUT_RECOVERY_PERFORM], entities=['box']) as queue:
                    serial.readline()
                    queue.get(timeout=1)
                process.wait_for_match_in_stderr(
                    'Received SERIAL_RECONNECT. Reconnecting serial connection', timeout=10)
        finally:
            process.wait(timeout=10)
