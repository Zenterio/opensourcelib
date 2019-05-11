from unittest import TestCase
from unittest.mock import call, patch

from debpacker.common.test.utils import AssertFileRegexMixin
from debpacker.toolchain.configuration import ToolchainDefinition
from debpacker.toolchain.toolchain import package_toolchain_list


class TestPackageToolchainList(TestCase, AssertFileRegexMixin):

    def setUp(self):
        self.toolchain_definitions = [
            ToolchainDefinition(
                name='zenterio-name1',
                paths=['/tmp/tools/t1'],
                url='http://url1/file',
                version='1.0.0',
                toolchain_root='',
                links=[['src1', 'dst1'], ['src2', 'dst2']],
                depends=['test-depend']),
            ToolchainDefinition(
                name='zenterio-name2',
                paths=['/tmp/install/some/path/', '/tmp/install/some/other/path/'],
                url='ftp://url2/file',
                version='1.1.0',
                toolchain_root='some/path/',
                links=[],
                depends=[])
        ]

    def test_package_toolchain_list(self):
        with patch(
                package_toolchain_list.__module__ + '.package_toolchain') as package_toolchain_mock:
            package_toolchain_list(self.toolchain_definitions, 'out')
            package_toolchain_mock.assert_has_calls(
                calls=[
                    call(
                        'http://url1/file', ['/tmp/tools/t1'],
                        'out',
                        version='1.0.0',
                        package_name='zenterio-name1',
                        toolchain_root='',
                        links=[['src1', 'dst1'], ['src2', 'dst2']],
                        depends=['test-depend'],
                        create_dummy_archive=False),
                    call(
                        'ftp://url2/file',
                        ['/tmp/install/some/path/', '/tmp/install/some/other/path/'],
                        'out',
                        version='1.1.0',
                        package_name='zenterio-name2',
                        toolchain_root='some/path/',
                        links=[],
                        depends=[],
                        create_dummy_archive=False)
                ],
                any_order=False)
