from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_file(zk2):
    result = zk2(
        [
            'infra', 'hostshellexec', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], 'run '
        '--host-shell-exec-enabled true '
        'infra.systest.data.suites.test_infra:test_file')

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout
