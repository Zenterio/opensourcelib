from zaf.component.decorator import requires


@requires(zchangelog='Zchangelog')
def test_version(zchangelog):
    result = zchangelog('--version')
    assert 'zchangelog, version' in result.stdout
