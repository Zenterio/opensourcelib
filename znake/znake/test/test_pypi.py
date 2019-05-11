import unittest
from unittest.mock import Mock

from znake.builddir import BuildDir
from znake.pypi import _render_build_bdist_package_command, _render_build_sdist_package_command, \
    get_namespace


class TestPypi(unittest.TestCase):

    def test_render_build_sdist_package_command(self):
        ctx = self._get_mock_context()
        result = _render_build_sdist_package_command(ctx)
        self.assertTrue(
            result.endswith(
                'mkdir -p ./build/pypi/sdist && python3 setup.py sdist '
                '-d ./build/pypi/sdist && touch ./build/pypi/sdist'))

    def test_render_build_bdist_package_command(self):
        ctx = self._get_mock_context()
        result = _render_build_bdist_package_command(ctx)
        self.assertEqual(
            result, 'mkdir -p ./build/pypi/wheel && python3 setup.py bdist_wheel '
            '-d ./build/pypi/wheel && touch ./build/pypi/wheel')

    def test_get_namespace(self):
        config = Mock()
        namespace = get_namespace(config)
        assert len(namespace.tasks) == 4

    def _get_mock_context(self):
        ctx = Mock()
        ctx.build_dir = BuildDir()

        return ctx
