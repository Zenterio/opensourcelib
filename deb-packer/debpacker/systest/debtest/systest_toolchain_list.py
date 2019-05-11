import glob
import logging
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertFileExistsMixin, get_toolchain_test_data
from debpacker.systest.utils import AssertCorrectToolchainMixin, get_test_data, invoke_for_output, \
    prepare_template, uninstall

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ToolchainListSystest(TestCase, AssertFileExistsMixin, AssertCorrectToolchainMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.test_root_handle = TemporaryDirectory()
        self.test_root = self.test_root_handle.name

    def tearDown(self):
        self.test_root_handle.cleanup()
        uninstall('zenterio-tgz-archive')
        uninstall('zenterio-toolchain-dir')

    def test_create_toolchains_from_file_definition(self):
        with prepare_template(get_test_data('toolchain_definition_template.yaml'),
                              URL1=get_toolchain_test_data('tgz_archive.tgz'),
                              NAME1='zenterio-tgz-archive.', DEPENDS1='dpkg',
                              URL2=get_toolchain_test_data('toolchain_dir'),
                              NAME2='zenterio-toolchain-dir') as definition_file:
            command = 'zdeb-packer --verbose toolchain-list --file {file}'.format(
                file=definition_file)
            invoke_for_output(command, cwd=self.test_root)
            self.assert_file_exists(os.path.join(self.test_root, 'zenterio-tgz-archive*.deb'))
            self.assert_file_exists(os.path.join(self.test_root, 'zenterio-toolchain-dir*.deb'))
            debs = glob.glob(os.path.join(self.test_root, '*.deb'))
            debs.sort()
            self.assertEqual(2, len(debs))

            tgz_toolchain_files = map(
                lambda path: os.path.join(path, 'file'),
                ['/tmp/install/tool1', '/tmp/install/tools/tool1'])
            self.assert_correct_toolchain(
                debs[0], 'zenterio-tgz-archive', tgz_toolchain_files, 'This is the tgz archive.\n')
            self.assert_correct_toolchain(
                debs[1], 'zenterio-toolchain-dir',
                ['/tmp/install/tool2/file', '/tmp/install/tool2_link/file'],
                'This is the file in toolchain_dir.')

    def test_create_dummy_toolchains_form_file_definition(self):
        with prepare_template(get_test_data('toolchain_definition_dummy_template.yaml'),
                              URL1=get_toolchain_test_data('tgz_archive.tgz'),
                              NAME1='zenterio-dummy-1.', DEPENDS1='dpkg',
                              URL2=get_toolchain_test_data('tgz_archive.tgz'),
                              NAME2='zenterio-dummy-2') as definition_file:
            command = 'zdeb-packer --verbose toolchain-list --file {file} --dummy'.format(
                file=definition_file)
            invoke_for_output(command, cwd=self.test_root)
            for deb in glob.glob(os.path.join(self.test_root, 'zenterio-dummy-*.deb')):
                invoke_for_output(
                    'sudo gdebi --non-interactive {deb}'.format(deb=deb), expected_exit_code=0)
            for path in ('/tmp/dummy/tool1/info.txt', '/tmp/dummy/tool2/info.txt'):
                with open(path, 'r') as info_file:
                    assert info_file.readline() == 'This is a dummy toolchain.'

    def test_install_toolchain_with_broken_dependency_fails(self):
        with prepare_template(get_test_data('toolchain_definition_template.yaml'),
                              URL1=get_toolchain_test_data('tgz_archive.tgz'),
                              NAME1='zenterio-tgz-archive.', DEPENDS1='does-not-exist',
                              URL2=get_toolchain_test_data('toolchain_dir'),
                              NAME2='zenterio-toolchain-dir') as definition_file:
            command = 'zdeb-packer --verbose toolchain-list --file {file}'.format(
                file=definition_file)
            invoke_for_output(command, cwd=self.test_root)
            expected_deb = glob.glob(os.path.join(self.test_root, 'zenterio-tgz-archive*.deb'))[0]
            self.assert_file_exists(expected_deb)
            stdout = invoke_for_output(
                'sudo gdebi --non-interactive {deb}'.format(deb=expected_deb), expected_exit_code=1)
            self.assertIn('Dependency is not satisfiable: does-not-exist', stdout)
