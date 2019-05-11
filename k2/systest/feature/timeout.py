from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_run_test_case_that_times_out(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testcasetimeout'], 'run '
        'systest.data.suites.test_timeout')
    assert 'test_that_times_out_blocked_on_a_queue aborted' in result.stdout
    assert 'test_that_times_out_while_sleeping aborted' in result.stdout
