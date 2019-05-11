import os

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_abort_on_fail_disabled(zk2):
    zk2 = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'aborttestrun', 'textreport'
        ], 'run systest.data.suites.test_abortonfail')

    stdout = zk2.stdout
    assert 'Passed:  2' in stdout
    assert 'Failed:  1' in stdout
    assert 'Error:   0' in stdout
    assert 'Pending: 0' in stdout
    assert 'Skipped: 0' in stdout
    assert 'Ignored: 0' in stdout
    assert 'Total:   3' in stdout


@requires(zk2='Zk2')
def test_abort_on_fail_enabled(zk2):
    zk2 = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'aborttestrun', 'textreport'
        ], 'run '
        '--abort-on-fail '
        'systest.data.suites.test_abortonfail')

    stdout = zk2.stdout
    assert 'Passed:  1' in stdout
    assert 'Failed:  1' in stdout
    assert 'Error:   0' in stdout
    assert 'Pending: 0' in stdout
    assert 'Skipped: 1' in stdout
    assert 'Ignored: 0' in stdout
    assert 'Total:   3' in stdout


@requires(zk2='Zk2')
def test_abort_on_fail_enabled_repeat(zk2):
    zk2 = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'aborttestrun', 'textreport', 'looper'
        ], 'run '
        '--abort-on-fail '
        '--schedule-repeats 2 '
        'systest.data.suites.test_abortonfail')

    stdout = zk2.stdout
    assert 'Passed:  1' in stdout
    assert 'Failed:  1' in stdout
    assert 'Error:   0' in stdout
    assert 'Pending: 0' in stdout
    assert 'Skipped: 4' in stdout
    assert 'Ignored: 0' in stdout
    assert 'Total:   6' in stdout


@requires(zk2='Zk2')
def test_abort_on_unexpected_sut_reset_disabled(zk2):
    zk2 = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'aborttestrun', 'textreport', 'sutmessages'
        ],
        'run systest.data.suites.test_abortonunexpectedsutresetdisabled',
        plugin_path=os.path.join('systest', 'data', 'plugins'))

    stdout = zk2.stdout
    assert 'Passed:  3' in stdout, stdout
    assert 'Failed:  0' in stdout, stdout
    assert 'Error:   0' in stdout, stdout
    assert 'Pending: 0' in stdout, stdout
    assert 'Skipped: 0' in stdout, stdout
    assert 'Ignored: 0' in stdout, stdout
    assert 'Total:   3' in stdout, stdout


@requires(zk2='Zk2')
def test_abort_on_unexpected_sut_reset_enabled(zk2):
    zk2 = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
            'aborttestrun', 'textreport', 'sutmessages'
        ],
        'run '
        '--abort-on-unexpected-sut-reset '
        'systest.data.suites.test_abortonunexpectedsutresetenabled',
        plugin_path=os.path.join('systest', 'data', 'plugins'))

    stdout = zk2.stdout
    assert 'Skipped: 1' in stdout, stdout
