from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_extensions(zafapp):
    result = zafapp(['extensionscommand'], 'extensions --target-command testcmd')
    assert 'zaftestappextension' in result.stdout


@requires(zafapp='ZafApp')
def test_extensions_with_instanced_extension(zafapp):
    result = zafapp(
        ['instantiated', 'extensionscommand'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'extensions '
        '--target-command extensions --instances-ids xid --instances-xid@dependent-option TXT '
        '--include-framework false')
    assert 'xid: ids: xid' in result.stdout


@requires(zafapp='ZafApp')
def test_extension_with_activate_on_can_be_activated(zafapp):
    result = zafapp(
        ['extensionthatcanbeactivated'],
        '--config-file-pattern systest/data/simple_config.yaml --activate-on true testcmd')
    assert 'extension was activated' in result.stdout


@requires(zafapp='ZafApp')
def test_extension_with_activate_on_can_be_deactivated(zafapp):
    result = zafapp(
        ['extensionthatcanbeactivated'],
        '--config-file-pattern systest/data/simple_config.yaml --activate-on false testcmd')

    assert 'extension was activated' not in result.stdout


@requires(zafapp='ZafApp')
def test_extension_that_is_default_disabled_can_be_enabled(zafapp):
    result = zafapp(
        ['extensionthatisdefaultdisabled'],
        '--config-file-pattern systest/data/simple_config.yaml testcmd')

    assert 'extension was enabled' in result.stdout


@requires(zafapp='ZafApp')
def test_extension_can_replace_another_extension(zafapp):
    result = zafapp(
        ['extensionthatreplacesanotherextension', 'extensionthatgetsreplaced'],
        '--config-file-pattern systest/data/simple_config.yaml testcmd')

    assert 'extension that replaces another extension was enabled' in result.stdout
    assert 'extension that gets replaced was enabled' not in result.stdout
