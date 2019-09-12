from zaf.component.decorator import requires


@requires(zit='Zit')
def test_zit_version(zit):
    result = zit('--version', expected_exit_code=0)
    assert 'zit' in result.stdout


@requires(zit='Zit')
def test_zit_help(zit):
    result = zit('--help', expected_exit_code=0)
    assert 'Usage' in result.stdout
