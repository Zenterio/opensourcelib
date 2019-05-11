from zaf.component.decorator import requires


@requires(app='ZafApp')
def test_not_hidden_option_visible_in_help(app):
    result = app([], '--help')
    assert '--config-file-pattern' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_hidden_option_not_visible_in_help(app):
    result = app([], '--help')
    assert '--application-messagebus-timeout' not in result.stdout, result.stdout


@requires(app='ZafApp')
def test_hidden_option_visible_in_full_help(app):
    result = app([], '--full-help')
    assert '--application-messagebus-timeout' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_not_hidden_command_visible_in_help(app):
    result = app([], '--help')
    assert ' sleep ' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_hidden_command_not_visible_in_help(app):
    result = app(['unittestcommand'], '--help')
    assert ' unittest ' not in result.stdout, result.stdout


@requires(app='ZafApp')
def test_hidden_command_visible_in_full_help(app):
    result = app(['unittestcommand'], '--full-help')
    assert ' unittest ' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_command_with_option(zafapp):
    result = zafapp(
        ['subcommands'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'command --command-option a',
        expected_exit_code=2)

    assert 'Error: Missing command.' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_subcommand_with_options_on_both_level(zafapp):
    result = zafapp(
        ['subcommands'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'command --command-option a '
        'subcommand --subcommand-option b',
        expected_exit_code=2)

    assert 'Error: Missing command.' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_subsubcommand_with_options_on_all_levels(zafapp):
    result = zafapp(
        ['subcommands'], '--config-file-pattern systest/data/simple_config.yaml '
        'command --command-option a '
        'subcommand --subcommand-option b '
        'subsubcommand --subsubcommand-option c')

    assert 'subsubcommand a b c' == result.stdout


@requires(zafapp='ZafApp')
def test_duplicate_framework_cli_options_are_not_allowed(zafapp):
    result = zafapp(
        ['duplicatedframework1', 'duplicatedframework2'],
        '--config-file-pattern systest/data/simple_config.yaml ',
        expected_exit_code=1,
    )

    assert 'Duplicate command line option' in result.stdout


@requires(zafapp='ZafApp')
def test_duplicate_cli_option_names_for_framework_and_command_options_are_not_allowed(zafapp):
    result = zafapp(
        ['duplicatedcommands', 'duplicatedframework1', 'duplicatedcommand2'],
        '--config-file-pattern systest/data/simple_config.yaml ',
        expected_exit_code=1,
    )

    assert 'Duplicate command line option' in result.stdout


@requires(zafapp='ZafApp')
def test_duplicate_cli_option_names_for_command_options_on_same_command_are_not_allowed(zafapp):
    result = zafapp(
        ['duplicatedcommands', 'duplicatedcommand1', 'duplicatedcommand3'],
        '--config-file-pattern systest/data/simple_config.yaml ',
        expected_exit_code=1,
    )

    assert 'Duplicate command line option' in result.stdout


@requires(zafapp='ZafApp')
def test_duplicate_cli_option_names_for_command_options_on_different_commands_are_allowed(zafapp):
    zafapp(
        ['duplicatedcommands', 'duplicatedcommand2', 'duplicatedcommand3'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'command',
        expected_exit_code=0,
    )
