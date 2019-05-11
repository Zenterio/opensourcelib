import signal
import time

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_run(zk2):
    zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.test_minimal')


@requires(zk2='Zk2')
def test_run_abort_with_sigint_stops_after_current_test_marks_rest_as_skipped(zk2):
    zk2 = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.test_sleep',
        wait=False)
    zk2.wait_for_match_in_stdout('Test case 1 started')
    zk2.signal(signal.SIGINT)

    zk2.wait()
    stdout = zk2.stdout
    assert 'Passed:  1' in stdout
    assert 'Skipped: 1' in stdout


@requires(zk2='Zk2')
def test_run_abort_with_two_sigint_aborts_current_test_marks_rest_as_skipped(zk2):
    zk2 = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.test_sleep',
        wait=False)
    zk2.wait_for_match_in_stdout('Test case 1 started')
    zk2.signal(signal.SIGINT)
    time.sleep(0.1)
    zk2.signal(signal.SIGINT)

    zk2.wait()
    stdout = zk2.stdout
    assert 'Error:   1' in stdout
    assert 'Skipped: 1' in stdout


@requires(zk2='Zk2')
def test_run_abort_with_sigabrt_aborts_current_test_marks_rest_as_skipped(zk2):
    zk2 = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.test_sleep',
        wait=False)
    zk2.wait_for_match_in_stdout('Test case 1 started')
    zk2.signal(signal.SIGABRT)

    zk2.wait()
    stdout = zk2.stdout
    assert 'Error:   1' in stdout
    assert 'Skipped: 1' in stdout


@requires(zk2='Zk2')
def test_run_abort_with_sigterm_aborts_current_test_marks_rest_as_skipped(zk2):
    zk2 = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.test_sleep',
        wait=False)
    zk2.wait_for_match_in_stdout('Test case 1 started')
    zk2.signal(signal.SIGTERM)

    zk2.wait()
    stdout = zk2.stdout
    assert 'Error:   1' in stdout
    assert 'Skipped: 1' in stdout
