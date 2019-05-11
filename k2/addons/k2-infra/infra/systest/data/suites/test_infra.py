import tempfile

from zaf.component.decorator import requires


@requires(infra='Infra')
def test_file(infra):
    with tempfile.NamedTemporaryFile() as file:
        assert infra.file(file.name).exists
    assert not infra.file(file.name).exists
