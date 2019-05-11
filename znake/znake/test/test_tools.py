from unittest import TestCase
from unittest.mock import Mock

from znake.tools import _render_isort, _render_yapf, render_flake8_check, render_pydocstyle_check


class TestToolsRenderCommandLine(TestCase):

    @staticmethod
    def get_ctx(tool):
        ctx = Mock()
        ctx.znake.static.packages = ['my_package', 'my_other_package']
        getattr(ctx.znake.static, tool).flags = ['--my-flag', '--my-other-flag']
        return ctx

    def test_flake8(self):
        ctx = self.get_ctx('flake8')
        result = render_flake8_check(ctx)
        assert 'flake8' in result
        assert '--my-flag --my-other-flag' in result
        assert 'my_package my_other_package' in result

    def test_isort(self):
        ctx = self.get_ctx('isort')
        result = _render_isort(ctx, '--EXTRA')
        assert 'isort --recursive --EXTRA' in result
        assert '--my-flag --my-other-flag' in result
        assert 'my_package my_other_package' in result

    def test_pydocstyle(self):
        ctx = self.get_ctx('pydocstyle')
        result = render_pydocstyle_check(ctx)
        assert 'pydocstyle' in result
        assert '--my-flag --my-other-flag' in result
        assert 'my_package my_other_package' in result

    def test_yapf(self):
        ctx = self.get_ctx('yapf')
        result = _render_yapf(ctx, '--EXTRA')
        assert 'yapf -p --recursive --EXTRA' in result
        assert '--my-flag --my-other-flag' in result
        assert 'my_package my_other_package' in result
