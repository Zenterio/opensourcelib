import unittest
from unittest.mock import Mock, patch

from zaf.commands import COMMAND
from zaf.config.manager import ConfigManager

from k2.sut import SUT
from virt.docker import DOCKER_IMAGES_IDS, DOCKER_IMAGES_REPOSITORY, DOCKER_IMAGES_TAG, \
    SUT_DOCKER_CONTAINER_NAME, SUT_DOCKER_IMAGE_ID
from virt.docker_clean import FORCE, CleanDocker, clean_containers, clean_images


class TestDockerCleanContainers(unittest.TestCase):

    def test_clean_containers_does_not_do_anything_when_suts_does_not_can_docker(self):
        manager = Mock()
        manager.get_cans.return_value = []
        config = ConfigManager()
        config.set(SUT, ['sut1', 'sut2'])
        docker = Mock()

        with patch('virt.docker_clean.get_docker_client', return_value=docker), \
                patch('virt.docker_clean.get_container') as m:
            clean_containers(Mock(), manager, config)
            m.assert_not_called()

    def test_clean_containers_does_not_remove_non_existing_containers(self):
        manager, config, docker, container = configure_container_mocks(exists=False)

        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_containers(Mock(), manager, config), 0)
            container.remove.assert_not_called()

    def test_clean_containers_removes_existing_docker_containers(self):
        manager, config, docker, container = configure_container_mocks()

        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_containers(Mock(), manager, config), 0)
            container.remove.assert_called_with(force=False)

    def test_clean_containers_returns_exit_code_1_when_failed_to_remove_containers(self):
        manager, config, docker, container = configure_container_mocks()
        container.remove.side_effect = Exception

        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_containers(Mock(), manager, config), 1)
            container.remove.assert_called_with(force=False)

    def test_clean_containers_uses_force_flag_when_specified(self):
        manager, config, docker, container = configure_container_mocks(force=True)

        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_containers(Mock(), manager, config), 0)
            container.remove.assert_called_with(force=True)


def configure_container_mocks(entity='sut', container_name='name', force=False, exists=True):
    sut = Mock()
    sut.entity = entity
    manager = Mock()
    manager.get_cans.return_value = ['docker']
    manager.get_unique_class_for_entity.return_value = sut
    config = ConfigManager()
    config.set(SUT, [sut.entity])
    config.set(SUT_DOCKER_IMAGE_ID, 'image', entity=sut.entity)
    config.set(SUT_DOCKER_CONTAINER_NAME, container_name, entity=sut.entity)
    config.set(DOCKER_IMAGES_IDS, ['image'])
    config.set(FORCE, force)

    container = Mock()
    container.name = 'name'

    docker = Mock()
    if exists:
        docker.containers.list.return_value = [container]
    else:
        docker.containers.list.return_value = []

    return manager, config, docker, container


class TestDockerCleanImages(unittest.TestCase):

    def test_clean_images_does_nothing_if_no_image_exists(self):
        config, docker = configure_image_mocks(images={})

        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_images(Mock(), config), 0)
            docker.images.remove.assert_not_called()

    def test_clean_images_cleans_existing_images(self):
        config, docker = configure_image_mocks()

        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_images(Mock(), config), 0)
            docker.images.remove.assert_called_with('repo:tag', force=False)

    def test_clean_images_does_not_clean_images_that_does_not_exist(self):
        config, docker = configure_image_mocks(images={'image': ('repo', 'tag', False)})

        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_images(Mock(), config), 0)
            docker.images.remove.assert_not_called()

    def test_clean_images_gives_exit_code_1_when_failed_to_remove_image(self):
        config, docker = configure_image_mocks()

        docker.images.remove.side_effect = Exception
        with patch('virt.docker_clean.get_docker_client', return_value=docker):
            self.assertEqual(clean_images(Mock(), config), 1)


def configure_image_mocks(images={'image': ('repo', 'tag', True)}):
    config = ConfigManager()
    config.set(DOCKER_IMAGES_IDS, list(images.keys()))

    image_mocks = []
    for image, (repo, tag, exists) in images.items():
        config.set(DOCKER_IMAGES_REPOSITORY, repo, entity=image)
        config.set(DOCKER_IMAGES_TAG, tag, entity=image)

        if exists:
            mock = Mock()
            mock.tags = [':'.join([repo, tag])]
            image_mocks.append(mock)
    docker = Mock()

    docker.images.list.return_value = image_mocks
    return config, docker


class TestDockerCleanGetConfig(unittest.TestCase):

    def test_get_config_returns_empty_config_for_non_clean_commands(self):
        config = ConfigManager()
        config.set(COMMAND, 'notclean')
        clean_docker = CleanDocker(config, {})
        self.assertEqual(clean_docker.get_config(config, [], {}).config, {})

    def test_get_config_changes_log_level_when_cleancontainers_command(self):
        config = ConfigManager()
        config.set(COMMAND, 'cleancontainers')
        clean_docker = CleanDocker(config, {})
        self.assertEqual(clean_docker.get_config(config, [], {}).config, {'log.level': 'warning'})

    def test_get_config_changes_log_level_when_cleanimages_command(self):
        config = ConfigManager()
        config.set(COMMAND, 'cleanimages')
        clean_docker = CleanDocker(config, {})
        self.assertEqual(clean_docker.get_config(config, [], {}).config, {'log.level': 'warning'})
