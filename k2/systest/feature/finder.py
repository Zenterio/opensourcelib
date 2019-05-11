from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_finder_errors_are_reported_as_test_cases_with_error_verdict(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.invalid_module_name')

    assert 'Error:   1' in result.stdout
