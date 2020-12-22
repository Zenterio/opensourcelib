import json
from threading import Event

from zaf.component.decorator import component, requires
from zaf.messages.message import EndpointId

from gudemock.gudemock import GudeMock
from k2.runner.exceptions import SkipException
from k2.sut import SUT_RECOVERY_PERFORM
from powerswitch import AVAILABLE_POWER_SWITCHES

SYSTEST = EndpointId('systest', 'systest endpoint')


@component(name='SkipIfGudePowerSwitchIsUnavailable')
@requires(config='Config')
def skip_if_gude_power_switch_is_unavailable(config):
    if 'gude' not in config.get(AVAILABLE_POWER_SWITCHES):
        raise SkipException('Gude power switch not available')


@component
@requires(prereq='SkipIfGudePowerSwitchIsUnavailable')
@requires(zk2='Zk2')
class zk2PowerSwitch(object):

    def __init__(self, zk2):
        self.zk2 = zk2

    def __call__(self, command, server_port, json=False, expected_exit_code=0):
        return self.zk2(
            ['powerswitch', 'gude'],
            'powerswitch --suts-ids box '
            '--suts-box@powerswitch gude '
            '--suts-box@gude-ip localhost:{port} '
            '--suts-box@gude-port 4 '
            '{command}{json}'.format(
                port=server_port, command=command, json=' --json' if json else ''),
            expected_exit_code=expected_exit_code)


@requires(powerswitch=zk2PowerSwitch)
def test_powerswitch_state_is_on(powerswitch):
    with GudeMock() as server:
        result = powerswitch('state', server.port)
        assert 'ON' in result.stdout


@requires(powerswitch=zk2PowerSwitch)
def test_powerswitch_state_is_off(powerswitch):
    with GudeMock() as server:
        server.set_states([False] * 8)
        result = powerswitch('state', server.port)
        assert 'OFF' in result.stdout


@requires(powerswitch=zk2PowerSwitch)
def test_set_power_state_on(powerswitch):
    with GudeMock() as server:
        server.set_states([False] * 8)
        result = powerswitch('on', server.port)
        assert 'ON' in result.stdout


@requires(powerswitch=zk2PowerSwitch)
def test_set_power_state_off(powerswitch):
    with GudeMock() as server:
        result = powerswitch('off', server.port)
        assert 'OFF' in result.stdout


@requires(powerswitch=zk2PowerSwitch)
def test_powerswitch_state_error(powerswitch):
    with GudeMock() as server:
        server.set_error()
        powerswitch('state', server.port, expected_exit_code=1)


@requires(powerswitch=zk2PowerSwitch)
def test_powerswitch_set_state_to_on_error(powerswitch):
    with GudeMock() as server:
        server.set_error()
        powerswitch('on', server.port, expected_exit_code=1)


@requires(powerswitch=zk2PowerSwitch)
def test_powerswitch_set_state_to_off_error(powerswitch):
    with GudeMock() as server:
        server.set_error()
        powerswitch('off', server.port, expected_exit_code=1)


@requires(powerswitch=zk2PowerSwitch)
def test_powerswitch_state_json_format(powerswitch):
    with GudeMock() as server:
        result = powerswitch('state', server.port, json=True)
        json.loads(result.stdout)


@requires(powerswitch=zk2PowerSwitch)
def test_powerswitch_state_changed(powerswitch):
    with GudeMock() as server:
        result = powerswitch('off', server.port, json=True)
        assert json.loads(result.stdout)['box']['changed']


@requires(prereq='SkipIfGudePowerSwitchIsUnavailable')
@requires(zk2='Zk2')
@requires(remote_client='SystestRemoteClient')
def test_powerswitch_connection_check(zk2, remote_client):
    """
    Tests that the power switch connection check can fail and that SUT_RECOVER_PERFORM is triggered.

    Blocks the power switch request until the test case is in the correct state before registering
    messagebus dispatchers.
    """
    with GudeMock() as server:
        server.set_error()
        block = Event()
        server.set_block(block, timeout=1)

        process = zk2(
            [
                'sut', 'runcommand', 'testfinder', 'remote', 'powerswitch', 'powerswitchcc', 'gude',
                'connectioncheck'
            ],
            '--remote-enabled true '
            '--remote-port {remote_port} '
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@powerswitch gude '
            '--suts-box@gude-ip localhost:{port} '
            '--suts-box@gude-port 4 '
            'powerswitch.systest.data.suites.test_minimal'.format(
                remote_port=remote_client.port, port=server.port),
            wait=False)
        try:

            with remote_client.client() as client:
                client.define_endpoints_and_messages({SYSTEST: [SUT_RECOVERY_PERFORM]})
                with client.local_message_queue([SUT_RECOVERY_PERFORM], entities=['box']) as queue:
                    block.set()
                    queue.get(timeout=1)
        finally:
            process.wait()
