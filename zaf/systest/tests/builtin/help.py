# from os.path import exists

from zaf.component.decorator import component, requires


@component
@requires(zafapp='ZafApp')
class Help(object):

    def __init__(self, zafapp):
        self.zafapp = zafapp

    def __call__(self, name, flag='', output_type='', expected_exit_code=0):
        return self.zafapp(
            ['helpcommand'],
            '--config-file-pattern systest/data/simple_config.yaml '
            'help '
            '{flag} '
            '{output_type} '
            '{name} '
            '--print-path '.format(name=name, flag=flag, output_type=output_type),
            expected_exit_code=expected_exit_code).stdout.strip()


@requires(help=Help)
def test_default_type_is_html(help):
    stdout = help('user-guide', '--guide')
    # assert exists(stdout), stdout
    assert 'user_guide/html/index.html' in stdout, stdout


@requires(help=Help)
def test_user_guide_with_pdf_type(help):
    stdout = help('user_guide', output_type='--pdf')
    # assert exists(stdout), stdout
    assert 'user_guide/pdf/user_guide.pdf' in stdout, stdout


@requires(help=Help)
def test_guide_flag_is_not_needed(help):
    stdout = help('user-guide')
    # assert exists(stdout), stdout
    assert 'user_guide/html/index.html' in stdout, stdout


@requires(help=Help)
def test_dev_guide_can_be_specified(help):
    stdout = help('dev-guide')
    # assert exists(stdout), stdout
    assert 'dev_guide/html/index.html' in stdout, stdout


@requires(help=Help)
def test_dev_guide_with_pdf_type(help):
    stdout = help('dev-guide', output_type='--pdf')
    # assert exists(stdout), stdout
    assert 'dev_guide/pdf/dev_guide.pdf' in stdout, stdout


@requires(help=Help)
def test_guide_not_found(help):
    help('noguide', '--guide', expected_exit_code=1)


@requires(help=Help)
def test_component_opens_user_guide_html_in_correct_page(help):
    stdout = help('messagebus', '--component')
    # assert exists(stdout), stdout
    assert 'user_guide/html/components/MessageBus.html' in stdout, stdout


@requires(help=Help)
def test_component_not_found(help):
    help('nocomponent', '--component', expected_exit_code=1)


@requires(help=Help)
def test_component_opens_user_guide_pdf_on_top_level(help):
    stdout = help('messagebus', '--component', '--pdf')
    # assert exists(stdout), stdout
    assert 'user_guide/pdf/user_guide.pdf' in stdout, stdout


@requires(help=Help)
def test_component_found_without_specifying_component_flag(help):
    stdout = help('messagebus')
    # assert exists(stdout), stdout
    assert 'user_guide/html/components/MessageBus.html' in stdout, stdout


@requires(help=Help)
def test_command_opens_user_guide_html_in_correct_page(help):
    stdout = help('help', '--command')
    # assert exists(stdout), stdout
    assert 'user_guide/html/commands/zafapp_help.html' in stdout, stdout


@requires(help=Help)
def test_command_not_found(help):
    help('nocommand', '--command', expected_exit_code=1)


@requires(help=Help)
def test_command_opens_user_guide_pdf_on_top_level(help):
    stdout = help('help', '--command', '--pdf')
    # assert exists(stdout), stdout
    assert 'user_guide/pdf/user_guide.pdf' in stdout, stdout


@requires(help=Help)
def test_command_found_without_specifying_command_flag(help):
    stdout = help('help')
    # assert exists(stdout), stdout
    assert 'user_guide/html/commands/zafapp_help.html' in stdout, stdout


@requires(help=Help)
def test_extension_opens_user_guide_html_in_correct_page(help):
    stdout = help('helpcommand', '--extension')
    # assert exists(stdout), stdout
    assert 'user_guide/html/extensions/helpcommand.html' in stdout, stdout


@requires(help=Help)
def test_extension_not_found(help):
    help('noextension', '--extension', expected_exit_code=1)


@requires(help=Help)
def test_extension_opens_user_guide_pdf_on_top_level(help):
    stdout = help('helpcommand', '--extension', '--pdf')
    # assert exists(stdout), stdout
    assert 'user_guide/pdf/user_guide.pdf' in stdout, stdout


@requires(help=Help)
def test_extension_found_without_specifying_extension_flag(help):
    stdout = help('helpcommand')
    # assert exists(stdout), stdout
    assert 'user_guide/html/extensions/helpcommand.html' in stdout, stdout


@requires(help=Help)
def test_extension_not_found_when_specifying_command_flag(help):
    """Tests that specifying a flag limits the search to that type."""
    help('helpcommand', '--command', expected_exit_code=1)
