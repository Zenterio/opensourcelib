from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_running_tests_that_uses_module_scope_component(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.lifetime.module_scope')

    expected_output = '\n'.join(
        (
            'my_module_component created',
            'test_something called',
            'test_something_else called',
            'my_module_component created',
            'test_something_entierly_different called',
        ))

    assert expected_output in result.stdout


@requires(zk2='Zk2')
def test_running_tests_that_uses_class_scope_component(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.lifetime.class_scope')

    expected_output = '\n'.join(
        (
            'my_class_component created',
            'test_a called',
            'test_b called',
            'my_class_component created',
            'test_c called',
        ))

    assert expected_output in result.stdout


@requires(zk2='Zk2')
def test_running_tests_that_uses_class_session_component(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.lifetime.session_scope')

    expected_output = '\n'.join(
        (
            'my_session_component created',
            'test_a called',
            'test_b called',
            'test_c called',
        ))

    assert expected_output in result.stdout


@requires(zk2='Zk2')
def test_running_tests_that_yield_from_components(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.lifetime.test_yield_from_components')

    expected_output = (
        'my_session_component setup',
        'my_class_component setup',
        'my_test_component setup',
        'my_module_component setup',
        'test_my_feature called',
        'my_module_component teardown',
        'my_test_component teardown',
        'my_session_component teardown',
        'my_class_component teardown',
    )

    for line in expected_output:
        assert line in result.stdout


@requires(zk2='Zk2')
def test_running_tests_that_uses_context_managers_as_components(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.lifetime.test_context_managers_as_components')

    expected_output = '\n'.join(
        (
            'ContextManager enter',
            'got data ContextManager data',
            'ContextManager exit',
        ))

    assert expected_output in result.stdout


@requires(zk2='Zk2')
def test_running_tests_that_override_component_default_scope(zk2):
    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults'],
        'run systest.data.suites.lifetime.test_override_component_default_scope')

    expected_output = '\n'.join(
        (
            'my_component created',
            'test_my_feature called',
            'my_component created',
            'test_my_other_feature called',
        ))

    assert expected_output in result.stdout
