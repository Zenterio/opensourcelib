from zaf.component.decorator import requires


@requires(zebra='Zebra')
def test_help(zebra):
    result = zebra('--help')

    assert 'make' in result.stdout
    assert 'exec' in result.stdout


@requires(zebra='Zebra')
def test_help_fails_for_unknown_command(zebra):
    zebra('unknowncommand --help', expected_exit_code=2)


@requires(zebra='Zebra')
def test_help_html_user_guide(zebra):
    result = zebra('help --print-path --guide ug')

    assert 'user_guide/html/index.html' in result.stdout


@requires(zebra='Zebra')
def test_help_pdf_user_guide(zebra):
    result = zebra('help --print-path --pdf ug')

    assert 'user_guide/pdf/user_guide.pdf' in result.stdout


@requires(zebra='Zebra')
def test_help_html_command(zebra):
    result = zebra('help --print-path --command exec')

    assert 'user_guide/html/commands/zebra_exec.html' in result.stdout


@requires(zebra='Zebra')
def test_help_html_command_with_no_type(zebra):
    result = zebra('help --print-path exec')

    assert 'user_guide/html/commands/zebra_exec.html' in result.stdout


@requires(zebra='Zebra')
def test_error_on_multiple_types(zebra):
    zebra('help --print-path --pdf --html ug', expected_exit_code=1)
