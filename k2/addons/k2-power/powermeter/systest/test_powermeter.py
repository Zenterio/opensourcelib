import json
from threading import Event

from zaf.component.decorator import component, requires
from zaf.messages.message import EndpointId

from gudemock.gudemock import GudeMock
from k2.runner.exceptions import SkipException
from k2.sut import SUT_RECOVERY_PERFORM
from powermeter import AVAILABLE_POWER_METERS

SYSTEST = EndpointId('systest', 'systest endpoint')


@component(name='SkipIfGudePowerMeterIsUnavailable')
@requires(config='Config')
def skip_if_gude_power_meter_is_unavailable(config):
    if 'gude' not in config.get(AVAILABLE_POWER_METERS):
        raise SkipException('Gude power meter not available')


@component
@requires(prereq='SkipIfGudePowerMeterIsUnavailable')
@requires(zk2='Zk2')
class zk2PowerMeter(object):

    def __init__(self, zk2):
        self.zk2 = zk2

    def __call__(self, server_port, json=False, expected_exit_code=0):
        return self.zk2(
            ['powermeter', 'gude'],
            'powermeter --suts-ids box '
            '--suts-box@powermeter gude '
            '--suts-box@gude-ip localhost:{port} '
            '--suts-box@gude-port 4 '
            '{json}'.format(port=server_port, json='--json' if json else ''),
            expected_exit_code=expected_exit_code)


@requires(powermeter=zk2PowerMeter)
def test_powermeter_power(powermeter):
    with GudeMock() as server:
        server.set_default_sensor_value(42)
        result = powermeter(server.port)
        assert '42.0 W' in result.stdout


@requires(powermeter=zk2PowerMeter)
def test_powermeter_power_error(powermeter):
    with GudeMock() as server:
        server.set_error()
        powermeter(server.port, expected_exit_code=1)


@requires(powermeter=zk2PowerMeter)
def test_powermeter_state_json_format(powermeter):
    with GudeMock() as server:
        result = powermeter(server.port, json=True)
        json.loads(result.stdout)


@requires(prereq='SkipIfGudePowerMeterIsUnavailable')
@requires(zk2='Zk2')
@requires(remote_client='SystestRemoteClient')
def test_powermeter_connection_check(zk2, remote_client):
    """
    Tests that the power meter connection check can fail and that SUT_RECOVER_PERFORM is triggered.

    Blocks the power meter request until the test case is in the correct state before registering
    messagebus dispatchers.
    """
    with GudeMock() as server:
        server.set_error()
        block = Event()
        server.set_block(block, timeout=1)

        process = zk2(
            [
                'sut', 'runcommand', 'testfinder', 'remote', 'powermeter', 'powermetercc', 'gude',
                'connectioncheck'
            ],
            '--remote-enabled true '
            '--remote-port {remote_port} '
            'run --suts-ids box --suts-box@ip localhost '
            '--suts-box@powermeter gude '
            '--suts-box@gude-ip localhost:{port} '
            '--suts-box@gude-port 4 '
            'powermeter.systest.data.suites.test_minimal'.format(
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
