from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_running_tests_that_require_components(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.test_components')

    assert 'test_that_implicitly_requires_A_and_B got component A' in result.stdout
    assert 'test_that_implicitly_requires_A_and_B got component B' in result.stdout

    assert 'test_that_explicitly_requires_A_and_B got component A' in result.stdout
    assert 'test_that_explicitly_requires_A_and_B got component B' in result.stdout

    assert 'test_that_requires_A_and_B_instances got component instance A' in result.stdout
    assert 'test_that_requires_A_and_B_instances got component instance B' in result.stdout
