from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_run_with_repeats_repeats(zk2):
    zk2 = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport',
            'looper'
        ], 'run looper.systest.data.suites.test_minimal --schedule-repeats 5')

    stdout = zk2.stdout
    assert 'Passed:  5' in stdout


@requires(zk2='Zk2')
def test_run_with_duration_repeats(zk2):
    zk2 = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport',
            'looper'
        ], 'run looper.systest.data.suites.test_short_sleep --schedule-duration 2')

    assert zk2.stdout.count(
        'looper.systest.data.suites.test_short_sleep.test_my_test_case PASSED ') > 3
    assert 'Execution time: 0:00:02' in zk2.stdout
