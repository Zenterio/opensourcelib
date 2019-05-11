from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_command_timeout_triggers_critical_abort(zk2):
    result = zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'commandtimeout',
            'testresults'
        ],
        '--command-timeout 0 '
        '--log-level debug '
        'run '
        '--exitcode-from-verdict true '
        'systest.data.suites.test_sleep',
        expected_exit_code=1)
    assert "Triggering event 'CRITICAL_ABORT' from endpoint 'commandtimeout" in result.stderr, result.stderr


@requires(zk2='Zk2')
def test_command_timeout_triggers_exit_with_exit_code_3_if_not_terminated_quick_enough(zk2):
    zk2(
        [
            'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'commandtimeout',
            'testresults'
        ],
        '--command-timeout 0 '
        '--command-timeout-exit-delay 0 '
        'run '
        '--exitcode-from-verdict true '
        'systest.data.suites.test_sleep',
        expected_exit_code=3)
