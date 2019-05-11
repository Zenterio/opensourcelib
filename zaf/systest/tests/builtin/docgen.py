from os import path
from tempfile import TemporaryDirectory

from zaf.component.decorator import component, requires


@component
@requires(app='ZafApp')
class Docgen(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, tmpdir, expected_exit_code=0):
        return self.app(
            ['docgencommand'],
            '--config-file-pattern systest/data/simple_config.yaml '
            'docgen '
            '--doc-dir {tmpdir}'.format(tmpdir=tmpdir),
            expected_exit_code=expected_exit_code)


@requires(docgen=Docgen)
def test_docgen_creates_files(docgen):
    with TemporaryDirectory() as tmpdir:
        docgen(tmpdir)

        assert path.isdir(path.join(tmpdir, 'extensions'))
        assert path.isdir(path.join(tmpdir, 'commands'))
        assert path.isdir(path.join(tmpdir, 'components'))

        assert path.isfile(path.join(tmpdir, 'extension_list.rst'))
        assert path.isfile(path.join(tmpdir, 'command_list.rst'))
        assert path.isfile(path.join(tmpdir, 'component_list.rst'))

        assert path.isfile(path.join(tmpdir, 'config_option_id_list.rst'))
        assert path.isfile(path.join(tmpdir, 'endpoint_list.rst'))
        assert path.isfile(path.join(tmpdir, 'message_list.rst'))

        assert path.isfile(path.join(tmpdir, 'extensions', 'docgencommand.rst'))
        assert path.isfile(path.join(tmpdir, 'commands', 'zafapp_docgen.rst'))
        assert path.isfile(path.join(tmpdir, 'components', 'MessageBus.rst'))
