import os
import tempfile

from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_entity_include_in_config_file(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file:

        additional_config_file.write(
            'id.include.files: [{included_config_file}]'.format(
                included_config_file=included_config_file.name))
        additional_config_file.flush()

        included_config_file.write('included.config: 1')
        included_config_file.flush()

        result = zafapp(
            ['configcommand'], (
                '--config-file-pattern systest/data/simple_config.yaml '
                '--additional-config-file-pattern {additional_config_pattern} '
                'config').format(additional_config_pattern=additional_config_file.name))

        assert 'id.included.config: 1  -  prio: 39, source: {included_config_file}'.format(
            included_config_file=included_config_file.name) in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_entity_include_file_not_found(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file:

        additional_config_file.write('id.include.files: [does_not_exist]')
        additional_config_file.flush()

        result = zafapp(
            ['configcommand'], (
                '--config-file-pattern systest/data/simple_config.yaml '
                '--additional-config-file-pattern {additional_config_pattern} '
                'config').format(additional_config_pattern=additional_config_file.name),
            expected_exit_code=1)

        assert "File '/tmp/does_not_exist', included from file '{additional_config}', was not found.".format(
            additional_config=additional_config_file.name) in result.stderr, result.stderr


@requires(zafapp='ZafApp')
def test_relative_entity_include_in_config_file(zafapp):
    with tempfile.TemporaryDirectory() as config_dir:
        with tempfile.NamedTemporaryFile(mode='w', dir=config_dir) as additional_config_file, \
             tempfile.NamedTemporaryFile(mode='w', dir=config_dir) as included_config_file:
            additional_config_file.write(
                'id.include.files: [{included_config_file}]'.format(
                    included_config_file=os.path.basename(included_config_file.name)))
            additional_config_file.flush()

            included_config_file.write('included.config: 1')
            included_config_file.flush()

            result = zafapp(
                ['configcommand'], (
                    '--config-file-pattern systest/data/simple_config.yaml '
                    '--additional-config-file-pattern {additional_config_pattern} '
                    'config').format(additional_config_pattern=additional_config_file.name))

            assert 'id.included.config: 1  -  prio: 39, source: {included_config_file}'.format(
                included_config_file=included_config_file.name) in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_entity_include_with_included_config_files(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_1, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_2, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file_3:

        additional_config_file.write(
            'id.include.files: [{included_config_file_1}]'.format(
                included_config_file_1=included_config_file_1.name))
        additional_config_file.flush()

        included_config_file_1.write(
            'include.files: [{included_config_file_2}]'.format(
                included_config_file_2=included_config_file_2.name))
        included_config_file_1.flush()

        included_config_file_2.write(
            'include.files: [{included_config_file_3}]'.format(
                included_config_file_3=included_config_file_3.name))
        included_config_file_2.flush()

        included_config_file_3.write('included.config: 3')
        included_config_file_3.flush()

        result = zafapp(
            ['configcommand'], (
                '--config-file-pattern systest/data/simple_config.yaml '
                '--additional-config-file-pattern {additional_config_pattern} '
                'config').format(additional_config_pattern=additional_config_file.name))

        assert 'id.included.config: 3  -  prio: 37, source: {included_config_file}'.format(
            included_config_file=included_config_file_3.name) in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_entity_include_in_config_file_for_existing_entities(zafapp):
    with tempfile.NamedTemporaryFile(mode='w') as additional_config_file, \
         tempfile.NamedTemporaryFile(mode='w') as included_config_file:

        additional_config_file.write(
            'main.mainentity1.include.files: [{included_config_file}]\n'.format(
                included_config_file=included_config_file.name))
        additional_config_file.write(
            'command.commandentity1.include.files: [{included_config_file}]\n'.format(
                included_config_file=included_config_file.name))

        additional_config_file.flush()

        included_config_file.write('required: 1')
        included_config_file.flush()

        result = zafapp(
            ['configcommand', 'configcommandentityoptions'], (
                '--config-file-pattern systest/data/simple_config.yaml '
                '--additional-config-file-pattern {additional_config_pattern} '
                '--main-entities mainentity1 '
                'config '
                '--command-entities commandentity1  '
            ).format(additional_config_pattern=additional_config_file.name))

        assert 'main.mainentity1.required: 1  -  prio: 39, source: {included_config_file}'.format(
            included_config_file=included_config_file.name) in result.stdout, result.stdout

        assert 'command.commandentity1.required: 1  -  prio: 39, source: {included_config_file}'.format(
            included_config_file=included_config_file.name) in result.stdout, result.stdout


@requires(zafapp='ZafApp')
def test_entity_include_with_required_option_using_command_line_option(zafapp):
    """
    Test that required options in entity include files work.

    The option is read from the entity include file after the first complete command line parsing.
    This means that the first complete command line parsing must not fail on missing required.
    """
    with tempfile.NamedTemporaryFile(mode='w') as included_config_file:
        included_config_file.write('required: 1')
        included_config_file.flush()

        result = zafapp(
            ['configcommand', 'configcommandentityoptions'], (
                '--config-file-pattern systest/data/simple_config.yaml '
                '--main-entities mainentity1 '
                '--main-mainentity1@include-files {file} '
                'config '
                '--command-entities commandentity1 '
                '--command-commandentity1@include-files {file}'.format(
                    file=included_config_file.name)))

        assert 'main.mainentity1.required: 1  -  prio: 89, source: {included_config_file}'.format(
            included_config_file=included_config_file.name) in result.stdout, result.stdout

        assert 'command.commandentity1.required: 1  -  prio: 89, source: {included_config_file}'.format(
            included_config_file=included_config_file.name) in result.stdout, result.stdout
