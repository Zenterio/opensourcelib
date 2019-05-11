import glob
import logging
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import TestCase
from unittest.mock import ANY

from debpacker.common.test.utils import AssertFileExistsMixin, AssertFileRegexMixin, create_file, \
    get_toolchain_test_data
from debpacker.systest.utils import AssertCorrectToolchainMixin, install, invoke_for_output, \
    is_hard_link, uninstall

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ToolchainSystest(TestCase, AssertFileExistsMixin, AssertFileRegexMixin,
                       AssertCorrectToolchainMixin):

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
        uninstall('zenterio-archive-with-links')

    def test_create_toolchain_deb_package_from_local_archive(self):
        out_dir = os.path.join(self.test_root, 'out_dir')
        uri = get_toolchain_test_data('tgz_archive.tgz')
        install_path_1 = '/tmp/installation/path/tgz_archive'
        install_path_2 = '/tmp/installation/other/tgz_archive'
        link = '/tmp/installation/link'
        package_name = 'zenterio-tgz-archive'
        command = 'zdeb-packer -v toolchain --uri {uri} --output-dir {out} --workspace {workspace} ' \
                  '--installation-path {install_path_1} --installation-path {install_path_2} ' \
                  '--link {link} {install_path_1}/file --force' \
            .format(uri=uri, out=out_dir, workspace=self.test_root, install_path_1=install_path_1,
                    install_path_2=install_path_2, link=link)
        logger.debug(invoke_for_output(command))
        deb_path = glob.glob(os.path.join(out_dir,
                                          '{package}_*.deb'.format(package=package_name)))[0]
        self.assert_file_exists(deb_path)
        debian_dir = os.path.join(self.test_root, 'output', 'debian')
        self.assert_file_regex(
            os.path.join(debian_dir, 'changelog'),
            r'{package} \(1.0.0\) unstable; urgency=low'.format(package=package_name))
        self.assert_file_regex(
            os.path.join(debian_dir, 'control'), r'Source: {package}'.format(package=package_name))

        toolchain_files = list(
            map(lambda path: os.path.join(path, 'file'), [install_path_1, install_path_2]))
        toolchain_files.append(link)
        self.assert_correct_toolchain(
            deb_path, package_name, toolchain_files, 'This is the tgz archive.\n')

    def test_create_toolchain_deb_with_minimal_arguments(self):
        uri = get_toolchain_test_data('toolchain_dir')
        install_path = '/tmp/path/toolchain_dir/'
        package_name = 'zenterio-toolchain-dir'
        command = 'zdeb-packer toolchain --uri {uri} --installation-path {install_path}' \
            .format(uri=uri, install_path=install_path)
        with TemporaryDirectory() as cwd:
            logger.debug(invoke_for_output(command, cwd=cwd))
            deb_path = glob.glob(os.path.join(cwd,
                                              '{package}_*.deb'.format(package=package_name)))[0]
            self.assert_file_exists(deb_path)
            self.assert_correct_toolchain(
                deb_path, package_name, [os.path.join(install_path, 'file')],
                'This is the file in toolchain_dir.')

    def test_create_toolchain_existing_workspace(self):
        command = 'zdeb-packer toolchain --uri uri --installation-path path --workspace {path}'.format(
            path=self.test_root)
        output = invoke_for_output(command, expected_exit_code=1)
        self.assertRegex(output, r'Workspace ".*" already exists and force was not given')

    def test_create_toolchain_existing_outfile(self):
        with NamedTemporaryFile(dir=self.test_root) as existing_file:
            command = 'zdeb-packer toolchain --uri uri --installation-path path --output-dir {path}' \
                .format(path=existing_file.name)
            output = invoke_for_output(command, expected_exit_code=1)
            self.assertRegex(output, r'The output directory .* is a file not a directory')

    def test_create_dummy_toolchain(self):
        install_path = '/tmp/test/dummy_archive'
        archive = os.path.join(self.test_root, 'dummy_archive')
        with TemporaryDirectory() as workspace:
            command = 'zdeb-packer toolchain --uri {uri} --installation-path {install_path} ' \
                      '--workspace {workspace} --force --dummy' \
                      .format(uri=archive, install_path=install_path, workspace=workspace)
            invoke_for_output(command, cwd=self.test_root, expected_exit_code=0)
            info_file_path = os.path.join(workspace, 'output', 'dummy', 'info.txt')
            with open(info_file_path, 'r') as info_file:
                assert info_file.readline() == 'This is a dummy toolchain.'

    def test_create_toolchain_which_preserves_hardlinks(self):
        archive = os.path.join(self.test_root, 'archive_with_links')
        os.makedirs(archive)
        file = os.path.join(archive, 'file')
        create_file(file, 'content')
        os.link(file, os.path.join(archive, 'file_link'))
        install_path1 = '/tmp/test/archive_with_links'
        with TemporaryDirectory() as workspace:
            command = 'zdeb-packer toolchain --uri {uri} --installation-path {install_path1} ' \
                      '--workspace {workspace} --force' \
                .format(uri=archive, install_path1=install_path1, workspace=workspace)
            invoke_for_output(command, cwd=self.test_root, expected_exit_code=ANY)

            dir_for_files_in_package = os.path.join(
                workspace, 'output', 'debian', 'zenterio-archive-with-links', 'tmp', 'test')
            self.assertTrue(
                is_hard_link(
                    os.path.join(dir_for_files_in_package, 'archive_with_links', 'file'),
                    os.path.join(dir_for_files_in_package, 'archive_with_links', 'file_link')))

            install(glob.glob(os.path.join(self.test_root, '*.deb'))[0])
            self.assertTrue(
                is_hard_link(
                    os.path.join(install_path1, 'file'), os.path.join(install_path1, 'file_link')))

    def test_that_invalid_uri_gives_good_error_message(self):
        command = 'zdeb-packer toolchain --uri ftp://bad_url.se --installation-path /tmp/test '
        output = invoke_for_output(command, cwd=self.test_root, expected_exit_code=1)
        self.assertRegex(
            output,
            r'.*Problem with the connection while fetching the toolchains. Is the URI valid?')
