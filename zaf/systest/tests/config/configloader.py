import os
import tempfile

from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_system_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file:
        system_config_file.write('system.file.config.option: 123')
        system_config_file.flush()
        result = zafapp(
            ['configcommand'],
            ('--system-config-file-pattern {pattern} config '
             'system.file.config.option').format(pattern=system_config_file.name))
        assert system_config_file.name in result.stdout, result.stdout
        assert 'system.file.config.option: 123' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_user_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as user_config_file:
        user_config_file.write('user.file.config.option: 321')
        user_config_file.flush()
        result = zafapp(
            ['configcommand'],
            ('--user-config-file-pattern {pattern} config '
             'user.file.config.option').format(pattern=user_config_file.name))
        assert user_config_file.name in result.stdout, result.stdout
        assert 'user.file.config.option: 321' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_local_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as local_config_file:
        local_config_file.write('local.file.config.option: 132')
        local_config_file.flush()
        result = zafapp(
            ['configcommand'],
            ('--local-config-file-pattern {pattern} config '
             'local.file.config.option').format(pattern=local_config_file.name))
        assert local_config_file.name in result.stdout, result.stdout
        assert 'local.file.config.option: 132' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_user_config_can_override_system_config(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as user_config_file:
        system_config_file.write('option.to.override: 1')
        system_config_file.flush()
        user_config_file.write('option.to.override: 2')
        user_config_file.flush()
        result = zafapp(
            ['configcommand'], (
                '--system-config-file-pattern {system_config_pattern} '
                '--user-config-file-pattern {user_config_pattern} '
                'config option.to.override').format(
                    system_config_pattern=system_config_file.name,
                    user_config_pattern=user_config_file.name))
        assert user_config_file.name in result.stdout, result.stdout
        assert 'option.to.override: 2' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_local_config_can_override_user_config(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as user_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as local_config_file:
        user_config_file.write('option.to.override: 2')
        user_config_file.flush()
        local_config_file.write('option.to.override: 3')
        local_config_file.flush()
        result = zafapp(
            ['configcommand'], (
                '--user-config-file-pattern {user_config_pattern} '
                '--local-config-file-pattern {local_config_pattern} '
                'config option.to.override').format(
                    user_config_pattern=user_config_file.name,
                    local_config_pattern=local_config_file.name))
        assert local_config_file.name in result.stdout, result.stdout
        assert 'option.to.override: 3' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_single_additional_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file:
        additional_config_file.write('additional.config: 1')
        additional_config_file.flush()
        result = zafapp(
            ['configcommand'], (
                '--additional-config-file-pattern {additional_config_pattern} '
                'config additional.config'
            ).format(additional_config_pattern=additional_config_file.name))
        assert additional_config_file.name in result.stdout, result.stdout
        assert 'additional.config: 1' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_multiple_additional_config_files(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as additional_additional_config_file:
        additional_config_file.write('additional.config: 1')
        additional_config_file.flush()
        additional_additional_config_file.write('additional.config: 2')
        additional_additional_config_file.flush()
        result = zafapp(
            ['configcommand'], (
                '--additional-config-file-pattern {additional_config_pattern} '
                '--additional-config-file-pattern {additional_additional_config_pattern} '
                'config additional.config').format(
                    additional_config_pattern=additional_config_file.name,
                    additional_additional_config_pattern=additional_additional_config_file.name))
        assert additional_config_file.name in result.stdout, result.stdout
        assert 'additional.config: 1' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_single_explicit_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as explicit_config_file:
        explicit_config_file.write('explicit.config: 1')
        explicit_config_file.flush()
        result = zafapp(
            ['configcommand'],
            ('--config-file-pattern {explicit_config_pattern} '
             'config explicit.config').format(explicit_config_pattern=explicit_config_file.name))
        assert explicit_config_file.name in result.stdout, result.stdout
        assert 'explicit.config: 1' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_multiple_explicit_config_files(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as explicit_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as additional_explicit_config_file:
        explicit_config_file.write('explicit.config: 1')
        explicit_config_file.flush()
        additional_explicit_config_file.write('explicit.config: 2')
        additional_explicit_config_file.flush()
        result = zafapp(
            ['configcommand'], (
                '--config-file-pattern {explicit_config_pattern} '
                '--config-file-pattern {additional_explicit_config_pattern} '
                'config explicit.config').format(
                    explicit_config_pattern=explicit_config_file.name,
                    additional_explicit_config_pattern=additional_explicit_config_file.name))
        assert explicit_config_file.name in result.stdout, result.stdout
        assert 'explicit.config: 1' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_additional_config_extends_other_config(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as additional_config_file:
        system_config_file.write('system.file.config.option: 123')
        system_config_file.flush()
        additional_config_file.write('additional.config: 1')
        additional_config_file.flush()
        result = zafapp(
            ['configcommand'], (
                '--system-config-file-pattern {system_config_pattern} '
                '--additional-config-file-pattern {additional_config_pattern} '
                'config').format(
                    system_config_pattern=system_config_file.name,
                    additional_config_pattern=additional_config_file.name))
        assert system_config_file.name in result.stdout, '{file} not found in:\n{stdout}'.format(
            file=system_config_file.name, stdout=result.stdout)
        assert additional_config_file.name in result.stdout, '{file} not found in:\n{stdout}'.format(
            file=additional_config_file.name, stdout=result.stdout)
        assert 'system.file.config.option: 123' in result.stdout, result.stdout
        assert 'additional.config: 1' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_explicit_config_overrides_other_config(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as system_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as explicit_config_file:
        system_config_file.write('system.file.config.option: 123')
        system_config_file.flush()
        explicit_config_file.write('explicit.config: 1')
        explicit_config_file.flush()
        result = zafapp(
            ['configcommand'], (
                '--system-config-file-pattern {system_config_pattern} '
                '--config-file-pattern {explicit_config_pattern} '
                'config').format(
                    system_config_pattern=system_config_file.name,
                    explicit_config_pattern=explicit_config_file.name))
        assert explicit_config_file.name in result.stdout, result.stdout
        assert 'system.file.config.option: 123' not in result.stdout, result.stdout
        assert 'explicit.config: 1' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_glob_config_files(zafapp):
    config_file_prefix = 'my_config_file'
    with tempfile.NamedTemporaryFile(mode='w', prefix=config_file_prefix) as config_file, \
         tempfile.NamedTemporaryFile(mode='w', prefix=config_file_prefix) as additional_config_file:  # noqa
        config_file.write('config.file.option: 123')
        config_file.flush()
        additional_config_file.write('additional.config.file.option: 321')
        additional_config_file.flush()
        config_file_pattern = os.path.join(os.path.dirname(config_file.name),
                                           config_file_prefix) + '*'
        result = zafapp(
            ['configcommand'], ('--config-file-pattern "{config_pattern}" config'
                                ).format(config_pattern=config_file_pattern))
        assert 'config.file.option: 123' in result.stdout, result.stdout
        assert 'additional.config.file.option: 321' in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_system_config_file_does_not_exist(zafapp):
    zafapp(
        ['configcommand'], ('--system-config-file-pattern ./this/file/does/not/exist config'),
        expected_exit_code=0)


@requires(zafapp='ZafApp')
def test_explicit_config_file_does_not_exist(zafapp):
    zafapp(
        ['configcommand'], ('--config-file-pattern ./this/file/does/not/exist config'),
        expected_exit_code=1)
