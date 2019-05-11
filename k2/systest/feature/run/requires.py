from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_running_test_that_requires_components_by_can_labels(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.requires.test_require_instances_by_capability')

    expected_output = '\n'.join(
        (
            'test_need_a_component got a A component',
            'test_need_b_component got a B component',
        ))

    assert expected_output in result.stdout


@requires(zk2='Zk2')
def test_that_enters_fails_reports_test_as_failed(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.requires.test_requires_fails:test_fail_on_enter '
        '--reports-text true')

    assert 'Error:   1' in result.stdout, '"Error:  1" not found in {result}'.format(
        result=result.stdout)
    assert 'Results (ERROR)' in result.stdout, '"Result (ERROR)" not found in {result}'.format(
        result=result.stdout)


@requires(zk2='Zk2')
def test_that_exit_fails_reports_run_as_failed(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.requires.test_requires_fails:test_fail_on_exit '
        '--reports-text true')

    assert 'Error:   0' in result.stdout, '"Error:  0" not found in {result}'.format(
        result=result.stdout)
    assert 'Results (ERROR)' in result.stdout, '"Result (ERROR)" not found in {result}'.format(
        result=result.stdout)


@requires(zk2='Zk2')
def test_that_exit_fails_reports_skips_remaining_tests(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.requires.test_requires_fails:test_fail_on_exit '
        'systest.data.suites.requires.test_requires_fails:test_after_fail '
        '--reports-text true')

    assert 'Error:   0' in result.stdout, '"Error:   0" not found in stdout'
    assert 'Skipped: 1' in result.stdout, '"Skipped: 1" not found in stdout'
    assert 'Results (ERROR)' in result.stdout, '"Result (ERROR)" not found in stdout'


@requires(zk2='Zk2')
def test_that_skip_exception_raised_in_required_component_init_skips_test_case(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.requires.test_requires_skips:test_skipped_in_component_init '
        '--reports-text true')

    assert 'Skipped: 1' in result.stdout, '"Skipped: 1" not found in {result}'.format(
        result=result.stdout)
    assert 'Results (PASSED)' in result.stdout, '"Results (PASSED)" not found in {result}'.format(
        result=result.stdout)


@requires(zk2='Zk2')
def test_that_skip_exception_raised_in_required_component_enter_skips_test_case(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.requires.test_requires_skips:test_skipped_in_component_enter '
        '--reports-text true')

    assert 'Skipped: 1' in result.stdout, '"Skipped: 1" not found in {result}'.format(
        result=result.stdout)
    assert 'Results (PASSED)' in result.stdout, '"Results (PASSED)" not found in {result}'.format(
        result=result.stdout)


@requires(zk2='Zk2')
def test_that_skip_exception_raised_in_required_component_exit_is_treated_as_an_error_on_run(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults', 'textreport'],
        'run systest.data.suites.requires.test_requires_skips:test_skipped_in_component_exit '
        '--reports-text true')

    assert 'Passed:  1' in result.stdout, '"Passed:  1" not found in {result}'.format(
        result=result.stdout)
    assert 'Results (ERROR)' in result.stdout, '"Results (ERROR)" not found in {result}'.format(
        result=result.stdout)
