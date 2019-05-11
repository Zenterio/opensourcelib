import os
import tempfile

from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_include_configs_file_from_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file:
        additional_config_file.write(
            'include.files: [{included_config_file}]'.format(
                included_config_file=included_config_file.name))
        additional_config_file.flush()
        included_config_file.write('included.config: 1')
        included_config_file.flush()

        result = zafapp(
            ['configcommand'],
            ('--additional-config-file-pattern {additional_config_pattern} '
             'config').format(additional_config_pattern=additional_config_file.name))
        assert additional_config_file.name in result.stdout, '{file} not found in:\n{stdout}'.format(
            file=additional_config_file.name, stdout=result.stdout)
        assert included_config_file.name in result.stdout, '{file} not found in:\n{stdout}'.format(
            file=included_config_file.name, stdout=result.stdout)

        assert 'included.config: 1  -  prio: 39, source: {included_config_file}'.format(
            included_config_file=included_config_file.name) in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_include_files_not_found(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file:
        additional_config_file.write('include.files: [does_not_exist]')
        additional_config_file.flush()

        result = zafapp(
            ['configcommand'],
            ('--additional-config-file-pattern {additional_config_pattern} '
             'config').format(additional_config_pattern=additional_config_file.name),
            expected_exit_code=1)
        assert "File '/tmp/does_not_exist', included from file '{additional_config}', was not found.".format(
            additional_config=additional_config_file.name) in result.stderr, result.stderr


@requires(zafapp='ZafApp')
def test_relative_include_configs_file_from_config_file(zafapp):
    with tempfile.TemporaryDirectory() as config_dir:
        with tempfile.NamedTemporaryFile(mode='w', dir=config_dir) as additional_config_file, \
             tempfile.NamedTemporaryFile(mode='w', dir=config_dir) as included_config_file:
            additional_config_file.write(
                'include.files: [{included_config_file}]'.format(
                    included_config_file=os.path.basename(included_config_file.name)))
            additional_config_file.flush()
            included_config_file.write('included.config: 1')
            included_config_file.flush()

            result = zafapp(
                ['configcommand'],
                ('--additional-config-file-pattern {additional_config_pattern} '
                 'config').format(additional_config_pattern=additional_config_file.name))
            assert additional_config_file.name in result.stdout, '{file} not found in:\n{stdout}'.format(
                file=additional_config_file.name, stdout=result.stdout)
            assert included_config_file.name in result.stdout, '{file} not found in:\n{stdout}'.format(
                file=included_config_file.name, stdout=result.stdout)

            assert 'included.config: 1  -  prio: 39, source: {included_config_file}'.format(
                included_config_file=included_config_file.name) in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_multiple_levels_of_includes_in_config_files(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_1, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_2, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_3:

        additional_config_file.write(
            'include.files: [{included_config_file}]'.format(
                included_config_file=included_config_file_1.name))
        additional_config_file.flush()

        included_config_file_1.write(
            'include.files: [{included_config_file}]'.format(
                included_config_file=included_config_file_2.name))
        included_config_file_1.flush()

        included_config_file_2.write(
            'include.files: [{included_config_file}]'.format(
                included_config_file=included_config_file_3.name))
        included_config_file_2.flush()

        included_config_file_3.write('included.config: 1')
        included_config_file_3.flush()

        result = zafapp(
            ['configcommand'],
            ('--additional-config-file-pattern {additional_config_pattern} '
             'config').format(additional_config_pattern=additional_config_file.name))

        assert 'included.config: 1  -  prio: 37, source: {included_config_file}'.format(
            included_config_file=included_config_file_3.name) in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_multiple_includes_in_same_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_1, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_2:

        additional_config_file.write(
            'include.files: [{included_config_file_1}, {included_config_file_2}]'.format(
                included_config_file_1=included_config_file_1.name,
                included_config_file_2=included_config_file_2.name))
        additional_config_file.flush()

        included_config_file_1.write('included.config1: 1')
        included_config_file_1.flush()

        included_config_file_2.write('included.config2: 2')
        included_config_file_2.flush()

        result = zafapp(
            ['configcommand'],
            ('--additional-config-file-pattern {additional_config_pattern} '
             'config').format(additional_config_pattern=additional_config_file.name))

        assert 'included.config1: 1  -  prio: 39, source: {included_config_file}'.format(
            included_config_file=included_config_file_1.name) in result.stdout, result.stdout

        assert 'included.config2: 2  -  prio: 39, source: {included_config_file}'.format(
            included_config_file=included_config_file_2.name) in result.stdout, result.stdout
