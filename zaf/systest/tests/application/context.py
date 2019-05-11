from zaf.component.decorator import requires


@requires(app='ZafApp')
def test_standalone_application_does_not_contain_extendability_commands(app):
    result = app([], '--full-help', application_context='standalone')
    assert ' extensions ' not in result.stdout, result.stdout


@requires(app='ZafApp')
def test_standalone_application_does_not_contain_extendability_cli_options(app):
    result = app([], '--full-help', application_context='standalone')
    assert '--plugins-path' not in result.stdout, result.stdout


@requires(app='ZafApp')
def test_extendable_application_contains_extendability_commands(app):
    result = app(['extensionscommand'], '--full-help')
    assert ' extensions ' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_extendable_application_contains_extendability_cli_options(app):
    result = app([], '--full-help')
    assert '--plugins-path' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_internal_options_are_never_included_on_cli(app):
    result = app([], '--full-help')
    assert '--application-name' not in result.stdout, result.stdout
