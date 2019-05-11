import unittest
from unittest.mock import MagicMock, Mock, patch

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import CallbackDispatcher
from zaf.messages.message import EndpointId

from zpider.asciidoctor import ADOC_FILE, ASCIIDOCTOR_ENDPOINT, GENERATE_DOC, \
    GET_ASCIIDOCTOR_OPTIONS, AsciidoctorCommand
from zpider.asciidoctor.asciidoctor import AsciidoctorExtension


class TestAsciidoctorExtension(unittest.TestCase):

    def setUp(self):
        self.tempdir = MagicMock()
        self.tempdir.name = 'tempdir'
        self.tempdir.__enter__.return_value = self.tempdir.name

        self.env_mock = Mock()

    def test_generate_doc_calls_env_run(self):
        with _create_harness(env=self.env_mock) as harness, \
                patch('tempfile.TemporaryDirectory', return_value=self.tempdir), \
                patch('os.makedirs'), \
                patch('shutil.copy'):
            futures = harness.messagebus.send_request(
                GENERATE_DOC, ASCIIDOCTOR_ENDPOINT, data=AsciidoctorCommand('output_path'))
            futures.wait(timeout=1)
            self.assertTrue(self.env_mock.run.called)

    def test_tempdir_used_for_output_path(self):
        with _create_harness(env=self.env_mock) as harness, \
                patch('tempfile.TemporaryDirectory', return_value=self.tempdir), \
                patch('os.makedirs'), \
                patch('shutil.copy'):
            futures = harness.messagebus.send_request(
                GENERATE_DOC, ASCIIDOCTOR_ENDPOINT, data=AsciidoctorCommand('output_path'))
            futures.wait(timeout=1)
            self.assertIn('--out-file tempdir/output_path', self.env_mock.run.call_args[0][0])

    def test_generate_doc_includes_command_options(self):

        class MockCommand(AsciidoctorCommand):

            def to_asciidoctor_options(self):
                return 'command options'

        with _create_harness(env=self.env_mock) as harness, \
                patch('tempfile.TemporaryDirectory', return_value=self.tempdir), \
                patch('os.makedirs'), \
                patch('shutil.copy'):
            futures = harness.messagebus.send_request(
                GENERATE_DOC, ASCIIDOCTOR_ENDPOINT, data=MockCommand('output_path'))
            futures.wait(timeout=1)
            self.assertIn('command options', self.env_mock.run.call_args[0][0])

    def test_additional_options_from_other_extensions_are_included_in_run_command(self):
        with _create_harness(env=self.env_mock) as harness, \
                patch('tempfile.TemporaryDirectory', return_value=self.tempdir), \
                patch('os.makedirs'), \
                patch('shutil.copy'):
            CallbackDispatcher(harness.messagebus, lambda m: 'additional options').register(
                [GET_ASCIIDOCTOR_OPTIONS], [OPTIONS_ENDPOINT])
            futures = harness.messagebus.send_request(
                GENERATE_DOC, ASCIIDOCTOR_ENDPOINT, data=AsciidoctorCommand('output_path'))
            futures.wait(timeout=1)
            self.assertIn('additional options', self.env_mock.run.call_args[0][0])


OPTIONS_ENDPOINT = EndpointId('OPTIONS_ENDPOINT', '')


def _create_harness(env=Mock()):
    config = ConfigManager()
    with patch('os.path.exists', return_value=True):
        config.set(ADOC_FILE, 'file.adoc')
    return ExtensionTestHarness(
        AsciidoctorExtension,
        endpoints_and_messages={OPTIONS_ENDPOINT: [GET_ASCIIDOCTOR_OPTIONS]},
        config=config,
        components=[ComponentMock('Env', env)])
