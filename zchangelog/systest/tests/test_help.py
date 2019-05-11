from zaf.component.decorator import requires


@requires(zchangelog='Zchangelog')
def test_help(zchangelog):
    result = zchangelog('--help')
    assert 'Usage: zchangelog' in result.stdout
