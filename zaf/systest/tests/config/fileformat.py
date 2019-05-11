import tempfile

from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_invalid_yaml(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file:
        system_config_file.write('a: a:')
        system_config_file.flush()
        result = zafapp(
            ['configcommand'], ('--system-config-file-pattern {pattern} config'
                                ).format(pattern=system_config_file.name),
            expected_exit_code=1)
        assert 'ConfigLoaderError' in result.stderr, result.stderr
        assert system_config_file.name in result.stderr, result.stderr


@requires(zafapp='ZafApp')
def test_invalid_structured_yaml(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file:
        system_config_file.write('a: {b: c}')
        system_config_file.flush()
        result = zafapp(
            ['configcommand'], ('--system-config-file-pattern {pattern} config'
                                ).format(pattern=system_config_file.name),
            expected_exit_code=1)
        assert 'ConfigLoaderError' in result.stderr, result.stderr
        assert 'dictionary' in result.stderr, result.stderr
        assert system_config_file.name in result.stderr, result.stderr


@requires(zafapp='ZafApp')
def test_only_comment_in_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file:
        system_config_file.write('# comment')
        system_config_file.flush()
        result = zafapp(
            ['configcommand'], ('--system-config-file-pattern {pattern} config'
                                ).format(pattern=system_config_file.name),
            expected_exit_code=0)
        assert '' == result.stderr


@requires(zafapp='ZafApp')
def test_empty_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file:
        system_config_file.flush()
        result = zafapp(
            ['configcommand'], ('--system-config-file-pattern {pattern} config'
                                ).format(pattern=system_config_file.name),
            expected_exit_code=0)
        assert '' == result.stderr
