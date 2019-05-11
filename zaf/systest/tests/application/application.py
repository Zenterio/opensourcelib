from zaf.component.decorator import requires


@requires(app='ZafApp')
def test_application_noop(app):
    app(['noop'], 'noop')


@requires(app='ZafApp')
def test_help_on_subcommand(app):
    result = app(['noop'], 'noop --help')
    assert 'Usage:' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_help(app):
    result = app([], '--help')
    assert 'Usage:' in result.stdout, result.stdout


@requires(app='ZafApp')
def test_version(app):
    result = app([], '--version')
    assert '1.23' in result.stdout
