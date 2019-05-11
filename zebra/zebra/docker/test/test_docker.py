import unittest
from unittest.mock import ANY, MagicMock, patch

from zaf.config.manager import ConfigManager

from zebra.docker import CONTAINER_ROOT_DIR_OPTION, ENV_VARIABLES_OPTION, HOSTNAME_OPTION, \
    IMAGE_OPTION, IMAGE_OVERRIDE_OPTION, MOUNTS_OPTION, NETWORK_OPTION, PROJECT_DIR_NAME_OPTION, \
    PROJECT_DIR_OPTION, PULL_OPTION, REGISTRY_CACHE_OPTION, REGISTRY_OPTION, ROOT_DIR_OPTION, \
    ROOT_OPTION, TAG_OPTION, USE_REGISTRY_OPTION
from zebra.docker.docker import DockerRun
from zebra.docker.run import execute_interactive

from ..docker import DockerImageException, _docker_tag, determine_docker_pull, \
    determine_docker_run, determine_root_and_rel_project_dir_and_relative_cwd, \
    docker_image_exists_locally, find_project_dir, run_docker_pull
from ..dockerconfig import DockerConfig


class DetermineDockerCommands(unittest.TestCase):

    def test_determine_docker_run_command_returns_docker_if_env_var_not_set(self):

        def getenv(var_name):
            if var_name == 'OVERRIDE_RUN':
                return None

        with patch('os.getenv', side_effect=getenv):
            self.assertEqual(determine_docker_run(), '/usr/bin/docker')

    def test_determine_docker_run_command_returns_override_if_env_var_is_set(self):

        def getenv(var_name):
            if var_name == 'OVERRIDE_RUN':
                return 'override'

        with patch('os.getenv', side_effect=getenv):
            self.assertEqual(determine_docker_run(), 'override')

    def test_determine_docker_pull_command_returns_docker_if_env_var_not_set(self):

        def getenv(var_name):
            if var_name == 'OVERRIDE_PULL':
                return None

        with patch('os.getenv', side_effect=getenv):
            self.assertEqual(determine_docker_pull(), '/usr/bin/docker')

    def test_determine_docker_pull_command_returns_override_if_env_var_is_set(self):

        def getenv(var_name):
            if var_name == 'OVERRIDE_PULL':
                return 'override'

        with patch('os.getenv', side_effect=getenv):
            self.assertEqual(determine_docker_pull(), 'override')


class DockerImageExistsLocally(unittest.TestCase):

    def test_docker_image_exists_locally_returns_true_when_image_exists(self):
        image = 'image'
        with patch('subprocess.check_output', return_value=image):
            self.assertTrue(docker_image_exists_locally('docker', image))

    def test_docker_image_exists_locally_returns_false_when_image_does_not_exist(self):
        with patch('subprocess.check_output', return_value='something else'):
            self.assertFalse(docker_image_exists_locally('docker', 'something'))


class DetermineRootAndProjectDirAndRelativeCwd(unittest.TestCase):

    def test_determine_root_and_rel_cwd_when_make_project_dir_is_found_and_root_is_none(self):
        directory = '/root/a/b/c/d'

        def exists(path):
            return path == '/root/a/maketools/setup.mk'

        with patch('os.path.exists', side_effect=exists), \
                patch('os.getcwd', return_value=directory):
            self.assertEqual(
                determine_root_and_rel_project_dir_and_relative_cwd(), ('/root', 'a', 'b/c/d'))

    def test_determine_root_and_rel_cwd_when_make_project_dir_is_not_found_and_root_is_none(self):
        directory = '/root/a/b/c/d'

        with patch('os.path.exists', return_value=False), \
                patch('os.getcwd', return_value=directory):
            self.assertEqual(
                determine_root_and_rel_project_dir_and_relative_cwd(), ('/root/a/b/c', 'd', '.'))

    def test_root_is_always_parent_directory_of_project_dir_if_root_argument_is_none(self):
        with patch('os.getcwd', return_value='/root/a/b/c/d'):
            self.assertEqual(
                determine_root_and_rel_project_dir_and_relative_cwd(project_dir='/root/a/b/c/d'),
                ('/root/a/b/c', 'd', '.'))

        with patch('os.getcwd', return_value='/root/a/b/c/d'):
            self.assertEqual(
                determine_root_and_rel_project_dir_and_relative_cwd(project_dir='/root/a/b/c'),
                ('/root/a/b', 'c', 'd'))

        with patch('os.getcwd', return_value='/root/a/b/c/d'):
            self.assertEqual(
                determine_root_and_rel_project_dir_and_relative_cwd(project_dir='/root/a/b'),
                ('/root/a', 'b', 'c/d'))

    def test_both_root_and_project_dir_are_specified(self):
        with patch('os.getcwd', return_value='/root/a/b/c/d'):
            self.assertEqual(
                determine_root_and_rel_project_dir_and_relative_cwd(
                    root_dir='/root/a/b/c/d', project_dir='/root/a/b/c/d'),
                ('/root/a/b/c/d', '.', '.'))

        with patch('os.getcwd', return_value='/root/a/b/c/d'):
            self.assertEqual(
                determine_root_and_rel_project_dir_and_relative_cwd(
                    root_dir='/root/a', project_dir='/root/a/b/c'), ('/root/a', 'b/c', 'd'))

    def test_root_dir_is_not_parent_to_project_dir(self):
        with self.assertRaises(ValueError), \
                patch('os.getcwd', return_value='/root/a/b/c/d'):
            determine_root_and_rel_project_dir_and_relative_cwd(
                root_dir='/root/a/b/c/e', project_dir='/root/a/b/c/d')


class TestFindProjectDir(unittest.TestCase):

    def test_find_project_dir_exists_returns_project_dir(self):
        directory = '/root/a/b/c/d'

        def exists(path):
            return path == '/root/maketools/setup.mk'

        with patch('os.path.exists', side_effect=exists):
            self.assertEqual(find_project_dir(directory), '/root')

    def test_find_project_dir_does_not_exists_raises_exception(self):
        directory = '/root/a/b/c/d'

        with patch('os.path.exists', return_value=False):
            with self.assertRaises(ValueError):
                find_project_dir(directory)


class TestRunInDocker(unittest.TestCase):

    @staticmethod
    def _get_config(options={}):
        defaults = {
            IMAGE_OPTION: 'abs.u14',
            IMAGE_OVERRIDE_OPTION: None,
            TAG_OPTION: 'TAG',
            REGISTRY_OPTION: 'REGISTRY',
            USE_REGISTRY_OPTION: True,
            PULL_OPTION: False,
            ENV_VARIABLES_OPTION: [],
            MOUNTS_OPTION: [],
            HOSTNAME_OPTION: 'HOSTNAME',
            ROOT_OPTION: False,
            ROOT_DIR_OPTION: None,
            CONTAINER_ROOT_DIR_OPTION: '/zebra/workspace',
            PROJECT_DIR_OPTION: None,
            PROJECT_DIR_NAME_OPTION: None,
            NETWORK_OPTION: None,
        }
        for key, value in options.items():
            defaults[key] = value

        config = ConfigManager()
        for key, value in defaults.items():
            config.set(key, value)

        return DockerConfig(config)

    def patched_run_in_docker(self, cfg):
        with patch('zebra.docker.docker.assert_user_in_docker_group_or_sudo', return_value=True), \
                patch('zebra.docker.docker.run_docker_pull') as mock_pull, \
                patch('zebra.docker.docker.run_docker_run') as mock_run:
            DockerRun(cfg).run_in_docker(['CMD', 'ARG1'])
        return (mock_run, mock_pull)

    def test_registery_is_normally_included_in_image_name(self):
        cfg = self._get_config()
        mock_run, _ = self.patched_run_in_docker(cfg)
        mock_run.assert_called_with(
            ANY, 'REGISTRY/zenterio/abs.u14:TAG', ANY, ANY, ANY, execute_interactive, True)

    def test_registery_can_be_excluded_in_image_name(self):
        cfg = self._get_config({USE_REGISTRY_OPTION: False})
        mock_run, _ = self.patched_run_in_docker(cfg)
        mock_run.assert_called_with(
            ANY, 'zenterio/abs.u14:TAG', ANY, ANY, ANY, execute_interactive, True)

    def test_tag(self):
        cfg = self._get_config({TAG_OPTION: 'MYTAG'})
        mock_run, _ = self.patched_run_in_docker(cfg)
        mock_run.assert_called_with(
            ANY, 'REGISTRY/zenterio/abs.u14:MYTAG', ANY, ANY, ANY, execute_interactive, True)

    def test_registry_is_normally_pulled(self):
        cfg = self._get_config({PULL_OPTION: True})
        _, mock_pull = self.patched_run_in_docker(cfg)
        mock_pull.assert_called_with(ANY, 'REGISTRY/zenterio/abs.u14:TAG', 'REGISTRY', 'CACHE')

    def test_can_prevent_pulling(self):
        cfg = self._get_config({PULL_OPTION: False})
        _, mock_pull = self.patched_run_in_docker(cfg)
        mock_pull.assert_not_called()

    def test_network(self):
        cfg = self._get_config({NETWORK_OPTION: 'NETWORK'})
        mock_run, _ = self.patched_run_in_docker(cfg)
        flags = mock_run.call_args[0][2]
        self.assertIn('--network', flags)
        self.assertIn('NETWORK', flags)

    def test_image_override(self):
        cfg = self._get_config({IMAGE_OVERRIDE_OPTION: 'directory/image'})
        mock_run, _ = self.patched_run_in_docker(cfg)
        mock_run.assert_called_with(
            ANY, 'REGISTRY/directory/image:TAG', ANY, ANY, ANY, execute_interactive, True)


class TestDockerImageCaching(unittest.TestCase):

    @staticmethod
    def _process_mock(returncode=0):
        process = MagicMock()
        process.returncode = returncode
        return process

    @patch('subprocess.Popen')
    @patch('zebra.docker.docker._docker_tag')
    def test_cache_image_is_pulled_if_cache_valid(self, _docker_tag, Popen):
        Popen.return_value = self._process_mock()

        run_docker_pull('docker', 'registry/image', 'registry', 'cache')
        expected_command = ['docker', 'pull', 'cache/image']
        Popen.assert_called_with(
            expected_command, shell=ANY, stdout=ANY, stderr=ANY, universal_newlines=ANY)

    @patch('subprocess.Popen')
    @patch('zebra.docker.docker._docker_tag')
    @patch('zebra.docker.docker.determine_docker_tag')
    def test_pulled_cache_image_is_renamed_after_pulling_if_cache_valid(
            self, determine_docker_tag, _docker_tag, Popen):
        Popen.return_value = self._process_mock()
        determine_docker_tag.return_value = 'docker'

        run_docker_pull('docker', 'registry/image', 'registry', 'cache')

        _docker_tag.assert_called_with('docker', 'cache/image', 'registry/image')

    @patch('subprocess.Popen')
    @patch('zebra.docker.docker._docker_tag')
    def test_image_should_not_be_renamed_if_cache_not_valid(self, _docker_tag, Popen):
        Popen.return_value = self._process_mock()

        run_docker_pull('cmd', 'registry/image', 'registry', None)

        _docker_tag.assert_not_called()

    @patch('subprocess.Popen')
    def test_tag_raises_exception_if_docker_command_fails(self, Popen):
        Popen.return_value = self._process_mock(returncode=1)

        with self.assertRaises(DockerImageException):
            _docker_tag('docker', 'cached/image', 'default/image')

    @patch('subprocess.Popen')
    def test_well_formed_docker_tag_command(self, Popen):
        Popen.return_value = self._process_mock()

        _docker_tag('docker', 'cache/image', 'default/image')
        expected_command = ['docker', 'tag', 'cache/image', 'default/image']
        Popen.assert_called_with(
            expected_command, shell=ANY, stdout=ANY, stderr=ANY, universal_newlines=ANY)
