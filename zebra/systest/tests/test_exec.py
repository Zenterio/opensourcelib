from zaf.component.decorator import requires


@requires(zebra='Zebra')
def test_exec_make(zebra):
    zebra('exec --help')


@requires(zebra='Zebra')
def test_exec_command_runs_command_with_arguments(zebra):
    result = zebra('exec make help')

    assert ' make help' in result.stdout


@requires(zebra='Zebra')
def test_exec_command_supports_arguments_with_dashes(zebra):
    """Test that click doesn't consume arguments beginning with dashes."""
    result = zebra('-v exec make -j --output-sync help')

    assert ' make -j --output-sync help' in result.stdout
