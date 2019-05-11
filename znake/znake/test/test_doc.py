import unittest
from unittest.mock import Mock

from znake.builddir import BuildDir
from znake.doc import _render_generate_documentation_command, \
    _render_remove_html_documentation_command, _render_remove_pdf_documentation_command, \
    get_namespace


class TestRenderDocumentation(unittest.TestCase):

    def test_render_generate_documentation_command(self):
        ctx = self._get_mock_context()

        command_pattern = '{sphinx_build} {doc_dir}/{target}'
        result = _render_generate_documentation_command('my_doc', ctx, command_pattern)
        self.assertTrue(result.endswith('bin/sphinx-build ./build/doc/my_doc'))

    def test_render_remove_html_documentation_command(self):
        ctx = self._get_mock_context()
        result = _render_remove_html_documentation_command('my_doc', ctx)
        self.assertEqual(result, 'rm -rf ./build/doc/my_doc/html')

    def test_render_remove_pdf_documentation_command(self):
        ctx = self._get_mock_context()
        result = _render_remove_pdf_documentation_command('my_doc', ctx)
        self.assertEqual(result, 'rm -rf ./build/doc/my_doc/pdf')

    def _get_mock_context(self):
        ctx = Mock()
        ctx.build_dir = BuildDir()
        return ctx


class TestGetNamespace(unittest.TestCase):

    def test_get_namespace_with_no_target(self):
        config = self._get_mock_config()
        namespace = get_namespace(config)
        assert len(namespace.tasks) == 0
        assert len(namespace.collections) == 0

    def test_get_namespace_with_single_doc_target(self):
        config = self._get_mock_config()
        config.znake.doc.targets = [{'guide': 'user_guide'}]
        namespace = get_namespace(config)
        print(len(namespace.tasks))
        assert len(namespace.tasks) == 2
        assert len(namespace.collections) == 1

    def test_get_namespace_with_multiple_doc_targets(self):
        config = self._get_mock_config()
        config.znake.doc.targets = [{'guide': 'dev_guide'}, {'guide': 'user_guide'}]
        namespace = get_namespace(config)
        assert len(namespace.tasks) == 2
        assert len(namespace.collections) == 2

    def _get_mock_config(self):
        config = Mock()
        config.znake.doc.targets = []
        return config
