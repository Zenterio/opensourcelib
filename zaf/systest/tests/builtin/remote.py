from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_remote_and_blocker(zafapp):
    process = zafapp(
        ['remote', 'blocker', 'usestheblockerandremotefacilitiesextension'],
        '--log-debug zaf.messages.messagebus '
        '--remote-enabled true --remoteclient-enabled true --blocker-enabled true '
        '--config-file-pattern systest/data/simple_config.yaml '
        'remoteandblockercommand')

    assert process.exit_code == 0
    assert 'Reached end of command' in process.stdout


@requires(zafapp='ZafApp')
def test_remote_and_blocker_using_blocker_component(zafapp):

    process = zafapp(
        ['remote', 'blocker', 'usestheblockerandremotefacilitiesextension'],
        '--log-debug zaf.messages.messagebus '
        '--remote-enabled true --remoteclient-enabled true --blocker-enabled true '
        '--config-file-pattern systest/data/simple_config.yaml '
        'remoteandblockerusingblockercomponentcommand')

    assert process.exit_code == 0
    assert 'Reached end of command' in process.stdout
