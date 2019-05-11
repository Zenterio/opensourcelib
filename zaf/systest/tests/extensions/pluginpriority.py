from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_load_order_of_plugins(zafapp):
    result = zafapp(
        ['loadorderplugins'], '--config-file-pattern systest/data/simple_config.yaml '
        '--help')

    assert 'load order: 22, previous: 21' in result.stdout, result.stdout
    assert 'load order: 23, previous: 22' in result.stdout, result.stdout
    assert 'load order: 24, previous: 23' in result.stdout, result.stdout
    assert 'load order: 25, previous: 24' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_config_priority_for_plugins(zafapp):
    result = zafapp(
        ['configpriorityplugins'], '--config-file-pattern systest/data/simple_config.yaml '
        '--help')

    assert '11: 11' in result.stdout, result.stdout
    assert '12: 12' in result.stdout, result.stdout
    assert '13: 13' in result.stdout, result.stdout
    assert '14: 14' in result.stdout, result.stdout
    assert '15: 15' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_loading_extension_where_all_can_not_be_initialized(zafapp):
    result = zafapp(
        ['canbeinitialized21', 'cannotbeinitialized22', 'canbeinitialized23'],
        '--config-file-pattern systest/data/simple_config.yaml --help',
        expected_exit_code=1)

    assert 'CanBeInitialized21 init' in result.stdout, result.stdout
    assert 'CanBeInitialized21 destroy' in result.stdout, result.stdout
    assert 'CanNotBeInitialized22 init' in result.stdout, result.stdout
    assert 'CanNotBeInitialized22 destroy' not in result.stdout, result.stdout
    assert 'CanBeInitialized23 init' not in result.stdout, result.stdout
    assert 'CanBeInitialized23 destroy' not in result.stdout, result.stdout
