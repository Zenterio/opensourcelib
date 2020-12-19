import os

from zaf.component.decorator import requires
from zaf.messages.dispatchers import LocalMessageQueue

from zserial import SERIAL_CONNECTED, SERIAL_CONNECTION_LOST, SERIAL_ENDPOINT


@requires(exec='Exec', can=['serial'])
def test_read_from_serial(exec):
    exec.send_line('command', timeout=10)


@requires(exec='Exec', can=['serial'])
def test_serial_can_filter_out_command_results(exec):
    response = exec.send_line('ls {dir}'.format(dir=os.path.dirname(__file__)), timeout=1)
    assert 'test_serial.py' in response


@requires(exec='Exec', can=['serial'])
def test_serial_timeout(exec):
    timeout_occurred = False
    try:
        exec.send_line('ls {dir}'.format(dir=os.path.dirname(__file__)), timeout=0.3)
    except Exception:
        timeout_occurred = True

    assert timeout_occurred


@requires(exec='Exec', can=['serial'])
@requires(messagebus='MessageBus')
def test_connection_reestablished(exec, messagebus):
    with LocalMessageQueue(messagebus, [SERIAL_CONNECTION_LOST, SERIAL_CONNECTED],
                           [SERIAL_ENDPOINT]) as queue:
        exec.send_line_nowait('disconnect')
        assert queue.get(timeout=2).message_id == SERIAL_CONNECTION_LOST
        assert queue.get(timeout=2).message_id == SERIAL_CONNECTED
