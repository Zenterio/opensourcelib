from zaf.component.decorator import requires
from zaf.messages.message import EndpointId

from k2.runner import TEST_CASE_FINISHED
from k2.sut import SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, SUT_RESET_STARTED
from sutevents import SUTEVENTSTIME_ENDPOINT

SYSTEST = EndpointId('systest', 'systest endpoint')
PROCESS_TIMEOUT = 10
QUEUE_TIMEOUT = 5


@requires(zk2='Zk2')
def test_wait_for_log_lines_component(zk2):
    result = zk2(
        [
            'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'textreport'
        ],
        'run sutevents.systest.data.suites.test_loglines '
        '--suts-ids sut ',
        wait=False)
    result.wait(timeout=PROCESS_TIMEOUT)

    assert 'sutevents.systest.data.suites.test_loglines.test_matching_log_line     PASSED' in result.stdout
    assert 'sutevents.systest.data.suites.test_loglines.test_not_matching_log_line FAILED' in result.stdout


@requires(blocker_helper='BlockerHelper')
@requires(zk2='Zk2')
@requires(remote_client='SystestRemoteClient')
def test_suteventslog(zk2, blocker_helper, remote_client, VirtualSerialConnection):
    # suteventslog is activated on serial enabled, hence the need for serial
    with VirtualSerialConnection() as serial:
        process = zk2(
            [
                'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'textreport', 'zserial', 'sutevents', 'remote', 'blocker'
            ],
            '--log-info testcase '
            '--remote-enabled true '
            '--remote-port {remote_port} '
            '--blocker-enabled true '
            '--blocker-init-enabled true '
            'run '
            '--suts-ids box --suts-box@ip localhost '
            '--suts-box@serial-enabled true '
            '--suts-box@serial-device {device} --suts-box@serial-baudrate 9600 '
            '--suts-box@resetstarted-pattern RESET_BOX_STARTED '
            '--suts-box@resetdone-pattern RESET_BOX_DONE '
            '--suts-box@resetdone-delay 1 '
            'sutevents.systest.data.suites.test_dummy'.format(
                remote_port=remote_client.port, device=serial.device),
            wait=False)
        try:
            with remote_client.client() as client:
                test_msgs = [TEST_CASE_FINISHED]
                sut_msgs = [SUT_RESET_STARTED, SUT_RESET_DONE]
                with client.local_message_queue(test_msgs) as test_queue, \
                        client.local_message_queue(sut_msgs, entities=['box']) as sut_queue:
                    blocker_helper.stop_init_blocking(client)
                    process.wait_for_match_in_stderr('testcase - INFO - test 1')
                    serial.writeline('RESET_BOX_STARTED')
                    assert_equal_message_id(
                        sut_queue.get(timeout=QUEUE_TIMEOUT).message_id, SUT_RESET_STARTED)
                    assert_equal_message_id(
                        test_queue.get(timeout=QUEUE_TIMEOUT).message_id, TEST_CASE_FINISHED)
                    serial.writeline('RESET_BOX_DONE')
                    assert_equal_message_id(
                        sut_queue.get(timeout=QUEUE_TIMEOUT).message_id, SUT_RESET_DONE)
        finally:
            process.wait(timeout=PROCESS_TIMEOUT)

        assert 'Passed:  2' in process.stdout


@requires(blocker_helper='BlockerHelper')
@requires(zk2='Zk2')
@requires(remote_client='SystestRemoteClient')
def test_suteventstime(zk2, blocker_helper, remote_client):
    process = zk2(
        [
            'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'textreport', 'sutevents', 'remote', 'blocker'
        ],
        '--log-info testcase '
        '--remote-enabled true '
        '--remote-port {remote_port} '
        '--blocker-enabled true '
        '--blocker-init-enabled true '
        'run '
        '--suts-ids box --suts-box@ip localhost '
        '--suts-box@resetstarted-timeout 1 '
        '--suts-box@resetdone-timeout 1 '
        'sutevents.systest.data.suites.test_dummy'.format(remote_port=remote_client.port),
        wait=False)
    try:
        with remote_client.client() as client:
            test_msgs = [TEST_CASE_FINISHED]
            sut_msgs = [SUT_RESET_STARTED, SUT_RESET_DONE]
            with client.local_message_queue(test_msgs) as test_queue, \
                    client.local_message_queue(sut_msgs, entities=['box']) as sut_queue:
                blocker_helper.stop_init_blocking(client)
                process.wait_for_match_in_stderr('testcase - INFO - test 1')
                client.trigger_event(SUT_RESET_EXPECTED, SUTEVENTSTIME_ENDPOINT, entity='box')
                client.trigger_event(SUT_RESET_NOT_EXPECTED, SUTEVENTSTIME_ENDPOINT, entity='box')
                assert_equal_message_id(
                    sut_queue.get(timeout=QUEUE_TIMEOUT).message_id, SUT_RESET_STARTED)
                assert_equal_message_id(
                    test_queue.get(timeout=QUEUE_TIMEOUT).message_id, TEST_CASE_FINISHED)
                assert_equal_message_id(
                    sut_queue.get(timeout=QUEUE_TIMEOUT).message_id, SUT_RESET_DONE)
    finally:
        process.wait(timeout=PROCESS_TIMEOUT)

    assert 'Passed:  2' in process.stdout


@requires(blocker_helper='BlockerHelper')
@requires(zk2='Zk2')
@requires(remote_client='SystestRemoteClient')
def test_suteventscomponents(zk2, blocker_helper, remote_client):
    process = zk2(
        [
            'sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'textreport', 'sutevents', 'remote', 'blocker'
        ],
        '--remote-enabled true '
        '--remote-port {remote_port} '
        '--blocker-enabled true '
        '--blocker-init-enabled true '
        'run '
        '--suts-ids box --suts-box@ip localhost '
        '--suts-box@resetstarted-timeout 5 '
        '--suts-box@resetdone-timeout 1 '
        'sutevents.systest.data.suites.test_suteventscomponent'.format(
            remote_port=remote_client.port),
        wait=False)
    try:
        with remote_client.client() as client:
            sut_msgs = [SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED]
            with client.local_message_queue(sut_msgs, entities=['box']) as queue:
                blocker_helper.stop_init_blocking(client)
                assert_equal_message_id(
                    queue.get(timeout=QUEUE_TIMEOUT).message_id, SUT_RESET_EXPECTED)
                assert_equal_message_id(
                    queue.get(timeout=QUEUE_TIMEOUT).message_id, SUT_RESET_NOT_EXPECTED)
    finally:
        process.wait(timeout=PROCESS_TIMEOUT)

    assert 'Passed:  1' in process.stdout


def assert_equal_message_id(id1, id2):
    assert id1.name == id2.name, str(id1)
