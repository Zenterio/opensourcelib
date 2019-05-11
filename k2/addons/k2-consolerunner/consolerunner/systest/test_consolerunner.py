from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_console_runner_with_no_patterns(zk2):
    result = zk2(
        [
            'runcommand', 'multirunner', 'consolerunner', 'hostshellexec', 'testresults',
            'textreport'
        ], 'run '
        '--multi-runner-enabled true '
        '--host-shell-exec-enabled true '
        '--console-binary-ids binary1 '
        '--console-binary-binary1@binary "echo failure"')

    assert 'Passed:  0' in result.stdout
    assert 'Failed:  0' in result.stdout


@requires(zk2='Zk2')
def test_console_runner_with_a_failure(zk2):
    result = zk2(
        [
            'runcommand', 'multirunner', 'consolerunner', 'hostshellexec', 'testresults',
            'textreport'
        ], 'run '
        '--multi-runner-enabled true '
        '--host-shell-exec-enabled true '
        '--console-binary-ids binary1 '
        '--console-binary-binary1@binary "echo failure" '
        '--console-binary-binary1@failed-pattern failure ')

    assert 'Passed:  0' in result.stdout
    assert 'Failed:  1' in result.stdout


@requires(zk2='Zk2')
def test_console_runner_with_a_success(zk2):
    result = zk2(
        [
            'runcommand', 'multirunner', 'consolerunner', 'hostshellexec', 'testresults',
            'textreport'
        ], 'run '
        '--multi-runner-enabled true '
        '--host-shell-exec-enabled true '
        '--console-binary-ids binary1 '
        '--console-binary-binary1@binary "echo success" '
        '--console-binary-binary1@passed-pattern success ')

    assert 'Passed:  1' in result.stdout
    assert 'Failed:  0' in result.stdout


@requires(zk2='Zk2')
def test_console_runner_with_mixed_results(zk2):
    result = zk2(
        [
            'runcommand', 'multirunner', 'consolerunner', 'hostshellexec', 'testresults',
            'textreport'
        ], 'run '
        '--multi-runner-enabled true '
        '--host-shell-exec-enabled true '
        '--console-binary-ids binary1 '
        '--console-binary-binary1@binary "echo success && echo failure" '
        '--console-binary-binary1@passed-pattern success '
        '--console-binary-binary1@failed-pattern failure ')

    assert 'Passed:  1' in result.stdout
    assert 'Failed:  1' in result.stdout


@requires(zk2='Zk2')
def test_console_runner_with_multiple_binaries(zk2):
    result = zk2(
        [
            'runcommand', 'multirunner', 'consolerunner', 'hostshellexec', 'testresults',
            'textreport'
        ], 'run '
        '--multi-runner-enabled true '
        '--host-shell-exec-enabled true '
        '--console-binary-ids binary1 '
        '--console-binary-binary1@binary "echo success && echo failure" '
        '--console-binary-binary1@passed-pattern success '
        '--console-binary-binary1@failed-pattern failure '
        '--console-binary-ids binary2 '
        '--console-binary-binary2@binary "echo success && echo success" '
        '--console-binary-binary2@passed-pattern success ')

    assert 'Passed:  3' in result.stdout
    assert 'Failed:  1' in result.stdout


@requires(zk2='Zk2')
def test_console_runner_all_verdicts(zk2):
    result = zk2(
        [
            'runcommand', 'multirunner', 'consolerunner', 'hostshellexec', 'testresults',
            'textreport'
        ], 'run '
        '--multi-runner-enabled true '
        '--host-shell-exec-enabled true '
        '--console-binary-ids binary1 '
        '--console-binary-binary1@binary "echo success && echo failure '
        '&& echo error && echo ignored && echo skipped && echo pending" '
        '--console-binary-binary1@passed-pattern success '
        '--console-binary-binary1@failed-pattern failure '
        '--console-binary-binary1@error-pattern error '
        '--console-binary-binary1@pending-pattern pending '
        '--console-binary-binary1@skipped-pattern skipped '
        '--console-binary-binary1@ignored-pattern ignored ')

    assert 'Passed:  1' in result.stdout
    assert 'Failed:  1' in result.stdout
    assert 'Error:   1' in result.stdout
    assert 'Pending: 1' in result.stdout
    assert 'Skipped: 1' in result.stdout
    assert 'Ignored: 1' in result.stdout
    assert 'Total:   6' in result.stdout
