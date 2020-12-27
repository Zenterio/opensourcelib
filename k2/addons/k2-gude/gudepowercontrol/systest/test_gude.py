import json

from zaf.component.decorator import component, requires

from gudemock.gudemock import GudeMock


@component
@requires(zk2='Zk2')
class Gude(object):

    def __init__(self, zk2):
        self.zk2 = zk2

    def __call__(self, command, server_port, port_arg='--port 4', json=False, expected_exit_code=0):
        return self.zk2(
            ['gude'],
            'gude --ip localhost:{port} '
            '{port_arg} '
            '{command}{json}'.format(
                port=server_port,
                port_arg=port_arg,
                command=command,
                json=' --json' if json else ''),
            expected_exit_code=expected_exit_code)


@requires(gude=Gude)
def test_gude_state_on(gude):
    with GudeMock() as server:
        result = gude('state', server.port)
        assert 'ON' in result.stdout


@requires(gude=Gude)
def test_gude_state_off(gude):
    with GudeMock() as server:
        server.states = [False] * 8
        result = gude('state', server.port)
        assert 'OFF' in result.stdout


@requires(gude=Gude)
def test_gude_state_set_to_on(gude):
    with GudeMock() as server:
        server.states = [False] * 8
        result = gude('on', server.port)
        assert 'ON' in result.stdout


@requires(gude=Gude)
def test_gude_state_set_to_off(gude):
    with GudeMock() as server:
        result = gude('off', server.port)
        assert 'OFF' in result.stdout


@requires(gude=Gude)
def test_gude_state_for_all_ports_with_different_states(gude):
    with GudeMock() as server:
        server.states = [True, False, True, True, False, False, True, True]
        result = gude('state', server.port, port_arg='')
        assert result.stdout.count('ON') == 5
        assert result.stdout.count('OFF') == 3


@requires(gude=Gude)
def test_gude_state_set_for_multiple_ports(gude):
    with GudeMock() as server:
        result = gude('state', server.port, port_arg='--port 4 --port 6')
        assert result.stdout.count('ON') == 2


@requires(gude=Gude)
def test_gude_state_with_json_flag(gude):
    with GudeMock() as server:
        result = gude('state', server.port, json=True)
        assert json.loads(result.stdout) == {'4': {'state': 'ON', 'changed': False}}


@requires(gude=Gude)
def test_gude_state_changed(gude):
    with GudeMock() as server:
        result = gude('off', server.port, json=True)
        assert json.loads(result.stdout) == {'4': {'state': 'OFF', 'changed': True}}


@requires(gude=Gude)
def test_gude_state_error(gude):
    with GudeMock() as server:
        server.set_error()
        gude('state', server.port, expected_exit_code=1)


@requires(gude=Gude)
def test_gude_power(gude):
    with GudeMock() as server:
        server.set_default_sensor_value(42)
        result = gude('power', server.port)
        assert '42 W' in result.stdout


@requires(gude=Gude)
def test_gude_power_json(gude):
    with GudeMock() as server:
        server.set_default_sensor_value(42)
        result = gude('power', server.port, json=True)
        assert json.loads(result.stdout) == {'4': {'power': 42}}


@requires(gude=Gude)
def test_gude_power_error(gude):
    with GudeMock() as server:
        server.set_error()
        gude('power', server.port, expected_exit_code=1)
