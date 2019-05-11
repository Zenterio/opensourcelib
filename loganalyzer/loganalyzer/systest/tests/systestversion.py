"""Tests the cli version output."""
from loganalyzer.systest.utils import assert_installed, get_os_codename, invoke_for_output

from ..systest import SysTest


class TestVersion(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()
        self.version_pattern = r'zloganalyzer v[0-9]\.[0-9]\.[0-9]\+[0-9]+(?:\+' \
                               r'{codename})? \([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}\)' \
            .format(codename=get_os_codename())

    def tearDown(self):
        super().tearDown()

    def test_V_prints_version_and_exits_with_code_0(self):
        output = invoke_for_output('zloganalyzer -V')
        self.assertRegex(output, self.version_pattern)

    def test_version_prints_version_and_exits_with_code_0(self):
        output = invoke_for_output('zloganalyzer --version')
        self.assertRegex(output, self.version_pattern)
