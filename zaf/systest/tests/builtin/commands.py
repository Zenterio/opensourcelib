from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_commands(zafapp):
    result = zafapp(['commandscommand'], 'commands')

    assert 'commands' in result.stdout
    assert 'List the available commands provided by the loaded extensions' in result.stdout


@requires(zafapp='ZafApp')
def test_commands_short(zafapp):
    result = zafapp(['commandscommand'], 'commands --short')

    assert 'commands' in result.stdout
    assert 'List the available commands provided by the loaded extensions' not in result.stdout
