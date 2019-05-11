from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_messages_for_extension(zafapp):
    result = zafapp(
        ['noop', 'messagescommand', 'myextensionthatdefinesmessagesandendpoints'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'messages --target-command noop')

    assert 'MY_EXTENSION_ENDPOINT' in result.stdout
    assert 'MY_EXTENSION_MESSAGE' in result.stdout


@requires(zafapp='ZafApp')
def test_endpoints_for_extension(zafapp):
    result = zafapp(
        ['noop', 'endpointscommand', 'myextensionthatdefinesmessagesandendpoints'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'endpoints --target-command noop')

    assert 'MY_EXTENSION_ENDPOINT' in result.stdout
    assert 'MY_EXTENSION_MESSAGE' in result.stdout


@requires(zafapp='ZafApp')
def test_messages_with_instanced_extension(zafapp):
    result = zafapp(
        ['noop', 'messagescommand', 'myinstantiatedextensionthatdefinesmessagesandendpoints'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'messages --target-command noop')

    assert 'MY_EXTENSION_ENDPOINT' in result.stdout
    assert 'MY_EXTENSION_MESSAGE' in result.stdout


@requires(zafapp='ZafApp')
def test_endpoints_with_instanced_extension(zafapp):
    result = zafapp(
        ['noop', 'endpointscommand', 'myinstantiatedextensionthatdefinesmessagesandendpoints'],
        '--config-file-pattern systest/data/simple_config.yaml '
        'endpoints --target-command noop')

    assert 'MY_EXTENSION_ENDPOINT' in result.stdout
    assert 'MY_EXTENSION_MESSAGE' in result.stdout
