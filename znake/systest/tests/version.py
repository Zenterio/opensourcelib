
from zaf.component.decorator import requires


@requires(znake='Znake')
def test_znake_version(znake):
    result = znake('--version', expected_exit_code=0)
    assert 'Znake' in result.stdout
