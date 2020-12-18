import socketserver
from threading import Event

from zaf.component.decorator import requires
from zaf.messages.message import EndpointId

from k2.sut import SUT_RECOVERY_PERFORM
from mockserver.mockserver import TcpMockServer

SYSTEST = EndpointId('systest', 'systest endpoint')


@requires(zk2='Zk2')
def test_telnet_can_connect_to_server(zk2):

    seen_lines = []

    class EchoingRequestHandler(socketserver.BaseRequestHandler):

        def handle(self):
            try:
                while True:
                    self.request.send('/ # '.encode('ascii'))
                    line = self.request.recv(1024).decode('ascii')
                    seen_lines.append(line)
                    self.request.send(line.encode('ascii'))
                    self.request.send(line.encode('ascii'))
            except Exception:
                pass

    with TcpMockServer(EchoingRequestHandler) as server:
        zk2(
            [
                'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'telnet'
            ],
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@telnet-port {telnet_port} '
            'telnet.systest.data.suites.test_telnet:test_telnet_send_hello_world'.format(
                telnet_port=server.port))
    expected_lines = ['hello\r\n', 'world\r\n']
    filtered_seen_lines = [line for line in seen_lines if line in expected_lines]
    assert expected_lines == filtered_seen_lines


@requires(zk2='Zk2')
def test_telnet_check_exit_code(zk2):

    test_completed_event = Event()

    class ExitCodeRequestHandler(socketserver.BaseRequestHandler):

        def handle(self):
            self.request.send('/ # '.encode('ascii'))
            self.request.recv(1024)
            self.request.send('TEST\r\n'.encode('ascii'))
            self.request.send('/ # '.encode('ascii'))
            self.request.recv(1024)
            self.request.send('/ # '.encode('ascii'))
            self.request.recv(1024)
            self.request.send('1\r\n'.encode('ascii'))
            self.request.send('/ # '.encode('ascii'))
            test_completed_event.wait()

    with TcpMockServer(ExitCodeRequestHandler) as server:
        try:
            zk2(
                [
                    'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                    'telnet'
                ],
                'run --suts-ids box --suts-box@ip localhost '
                '--suts-box@telnet-port {telnet_port} '
                '--exitcode-from-verdict true '
                'telnet.systest.data.suites.test_telnet:test_telnet_check_exit_code'.format(
                    telnet_port=server.port))
        finally:
            test_completed_event.set()


@requires(blocker_helper='BlockerHelper')
@requires(zk2='Zk2')
@requires(remote_client='SystestRemoteClient')
def test_sut_recovery_initiated_when_telnet_connection_check_fails(
        zk2, remote_client, blocker_helper):
    """
    Tests that the telnet connection check can fail and that SUT_RECOVER_PERFORM is triggered.

    This is done by giving an invalid telnet port that causes exception when
    initiating the telnet connection.

    """
    process = zk2(
        [
            'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'telnet', 'telnetcc',
            'connectioncheck', 'remote', 'blocker'
        ],
        '--remote-enabled true '
        '--remote-port {remote_port} '
        '--blocker-enabled true '
        '--blocker-init-enabled true '
        'run --suts-ids box --suts-box@ip invalid_ip '
        '--suts-box@telnet-enabled true '
        '--suts-box@telnet-port -3 '
        '--suts-box@telnet-timeout 1 '
        '--suts-box@telnetcc-enabled true '
        'telnet.systest.data.suites.test_minimal'.format(remote_port=remote_client.port),
        wait=False)
    try:
        with remote_client.client() as client:
            client.define_endpoints_and_messages({SYSTEST: [SUT_RECOVERY_PERFORM]})
            with client.local_message_queue([SUT_RECOVERY_PERFORM], entities=['box']) as queue:
                blocker_helper.stop_init_blocking(client)
                queue.get(timeout=10)
    finally:
        process.wait(timeout=10)
