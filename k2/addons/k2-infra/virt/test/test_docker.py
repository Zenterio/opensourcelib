from collections import OrderedDict
from unittest import TestCase
from unittest.mock import Mock, patch

import docker
from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.component.scope import Scope
from zaf.config.manager import ConfigManager
from zaf.messages.message import EndpointId

from ..docker import DOCKER_IMAGE_PULL, DOCKER_IMAGE_REGISTRY, DOCKER_IMAGE_STOP_TIMEOUT, \
    DOCKER_IMAGES_ENVIRONMENT, DOCKER_IMAGES_HOSTNAME, DOCKER_IMAGES_IDS, \
    DOCKER_IMAGES_MOUNT_POINTS, DOCKER_IMAGES_NETWORK, DOCKER_IMAGES_REPOSITORY, \
    DOCKER_IMAGES_TAG, DOCKER_KEEP_RUNNING, SUT, SUT_DOCKER_CONTAINER_NAME, \
    SUT_DOCKER_IMAGE_ENVIRONMENT, SUT_DOCKER_IMAGE_HOSTNAME, SUT_DOCKER_IMAGE_ID, \
    SUT_DOCKER_IMAGE_MOUNT_POINTS, SUT_DOCKER_IMAGE_NETWORK, Docker, DockerContainerExec, \
    DockerContainerNode, DockerError, DockerExtension

MOCK_ENDPOINT = EndpointId('mock', 'Mock endpoint')


class TestDocker(TestCase):

    def setUp(self):
        self.client = Mock()
        self.docker = Docker(self.client)

    def test_logs_client_version_on_construction(self):
        self.client.version.assert_called_with()

    def test_accessing_the_client_property_performs_a_connectivity_check(self):
        self.assertEqual(self.docker.client, self.client)
        self.client.ping.assert_called_with()

    def test_accessing_the_client_property_raises_on_error(self):
        self.client.ping.side_effect = (docker.errors.APIError('error'), )
        with self.assertRaises(DockerError):
            self.docker.client

    def test_pull_a_specific_image_tag(self):
        self.docker.pull('my.registry.com/organization/image', 'v1')
        self.client.images.pull.assert_called_once_with(
            'my.registry.com/organization/image', tag='v1')

    def test_pull_assumes_latest_tag_if_none_is_specifiec(self):
        self.docker.pull('my.registry.com/organization/image')
        self.client.images.pull.assert_called_once_with(
            'my.registry.com/organization/image', tag='latest')

    def test_start_with_default_command(self):
        self.docker.start('my.registry.com/organization/image:latest')
        self.client.containers.run.assert_called_once_with(
            'my.registry.com/organization/image:latest',
            None,
            name=None,
            detach=True,
            auto_remove=True)

    def test_start_with_explicit_command(self):
        self.docker.start('my.registry.com/organization/image:latest', 'cat /etc/passwd')
        self.client.containers.run.assert_called_once_with(
            'my.registry.com/organization/image:latest',
            'cat /etc/passwd',
            name=None,
            detach=True,
            auto_remove=True)

    def test_start_with_some_arguments(self):
        self.docker.start('my.registry.com/organization/image:latest', a='a', b='b')
        args, kwargs = self.client.containers.run.call_args
        self.assertEqual(args, ('my.registry.com/organization/image:latest', None))
        self.assertEqual(kwargs['a'], 'a')
        self.assertEqual(kwargs['b'], 'b')
        self.assertEqual(kwargs['detach'], True)

    def test_container_stop(self):
        container = self.docker.start('image')
        container.stop(timeout=5)
        container._container.stop.assert_called_once_with(timeout=5)

    def test_container_exec(self):
        container = self.docker.start('image')
        container._container.exec_run.return_value = 0, (b'stdout', b'stderr')
        self.assertEqual(container.exec('command'), ('stdout', 'stderr', 0))
        container._container.exec_run.assert_called_once_with('command', demux=True)


class TestDockerContainerNode(TestCase):

    def test_maximum_config(self):
        config = ConfigManager()
        config.set(SUT, ['mysut'])
        config.set(SUT_DOCKER_IMAGE_ID, 'myimage', entity='mysut')
        config.set(DOCKER_IMAGES_IDS, ['myimage', 'myotherimage'])
        config.set(DOCKER_IMAGES_REPOSITORY, 'repository', entity='myimage')
        config.set(DOCKER_IMAGES_TAG, 'v1', entity='myimage')
        config.set(DOCKER_IMAGES_ENVIRONMENT, ['KEY=value'], entity='myimage')
        config.set(DOCKER_IMAGES_HOSTNAME, 'myhostname', entity='myimage')
        config.set(
            DOCKER_IMAGES_MOUNT_POINTS, [
                'type=tmpfs,target=/foo', 'type=volume,source=myvolume,target=/bar',
                'type=bind,source=/foo,target=/bar,readonly'
            ],
            entity='myimage')
        config.set(DOCKER_IMAGES_NETWORK, 'mynetwork', entity='myimage')

        config.set(DOCKER_IMAGES_REPOSITORY, 'otherrepository', entity='myotherimage')
        config.set(DOCKER_IMAGES_TAG, 'v2', entity='myotherimage')

        config.set(DOCKER_IMAGE_PULL, False)
        config.set(DOCKER_IMAGE_REGISTRY, 'registry/')
        config.set(DOCKER_IMAGE_STOP_TIMEOUT, 5)
        config.set(DOCKER_KEEP_RUNNING, True)

        with patch('virt.docker.Docker'):
            with _create_harness(config) as harness:
                harness.sut.entity = 'mysut'
                scope = Scope(name='myscope')
                node = harness.component_factory.call(DockerContainerNode, scope)

        self.assertEqual(node._image_entity, 'myimage')
        self.assertEqual(node._repository, 'repository')
        self.assertEqual(node._tag, 'v1')
        self.assertEqual(node._environment, {'KEY': 'value'})
        self.assertEqual(node._hostname, 'myhostname')
        self.assertEqual(node._mounts[0]['Source'], None)
        self.assertEqual(node._mounts[0]['Target'], '/foo')
        self.assertEqual(node._mounts[0]['Type'], 'tmpfs')
        self.assertEqual(node._mounts[0]['ReadOnly'], False)
        self.assertEqual(node._mounts[1]['Source'], 'myvolume')
        self.assertEqual(node._mounts[1]['Target'], '/bar')
        self.assertEqual(node._mounts[1]['Type'], 'volume')
        self.assertEqual(node._mounts[1]['ReadOnly'], False)
        self.assertEqual(node._mounts[2]['Source'], '/foo')
        self.assertEqual(node._mounts[2]['Target'], '/bar')
        self.assertEqual(node._mounts[2]['Type'], 'bind')
        self.assertEqual(node._mounts[2]['ReadOnly'], True)
        self.assertEqual(node._networkname, 'mynetwork')
        self.assertEqual(node._image_name, 'repository:v1')
        self.assertEqual(node._timeout, 5)
        self.assertFalse(node._pull)
        self.assertEqual(node._registry, 'registry/')
        self.assertTrue(node._keep_running)

    def test_atomic_sut_config_overrides_image_config(self):
        config = ConfigManager()
        config.set(SUT, ['mysut'])
        config.set(SUT_DOCKER_IMAGE_ID, 'myimage', entity='mysut')
        config.set(DOCKER_IMAGES_IDS, ['myimage'])
        config.set(DOCKER_IMAGES_REPOSITORY, 'repository', entity='myimage')
        config.set(DOCKER_IMAGES_TAG, 'v1', entity='myimage')
        config.set(DOCKER_IMAGES_HOSTNAME, 'myhostname', entity='myimage')
        config.set(DOCKER_IMAGES_NETWORK, 'mynetwork', entity='myimage')
        config.set(SUT_DOCKER_IMAGE_HOSTNAME, 'mysuthostname', entity='mysut')
        config.set(SUT_DOCKER_IMAGE_NETWORK, 'mysutnetwork', entity='mysut')

        with patch('virt.docker.Docker'):
            with _create_harness(config) as harness:
                harness.sut.entity = 'mysut'
                scope = Scope(name='myscope')
                node = harness.component_factory.call(DockerContainerNode, scope)

        self.assertEqual(node._image_entity, 'myimage')
        self.assertEqual(node._repository, 'repository')
        self.assertEqual(node._tag, 'v1')
        self.assertEqual(node._hostname, 'mysuthostname')
        self.assertEqual(node._networkname, 'mysutnetwork')

    def test_iterable_sut_config_extends_image_config(self):
        config = ConfigManager()
        config.set(SUT, ['mysut'])
        config.set(SUT_DOCKER_IMAGE_ID, 'myimage', entity='mysut')
        config.set(DOCKER_IMAGES_IDS, ['myimage'])
        config.set(DOCKER_IMAGES_REPOSITORY, 'repository', entity='myimage')
        config.set(DOCKER_IMAGES_TAG, 'v1', entity='myimage')
        config.set(DOCKER_IMAGES_ENVIRONMENT, ['KEY=value', 'A=a'], entity='myimage')
        config.set(DOCKER_IMAGES_MOUNT_POINTS, ['type=tmpfs,target=/foo'], entity='myimage')
        config.set(SUT_DOCKER_IMAGE_ENVIRONMENT, ['SUT_KEY=sut_value', 'A=b'], entity='mysut')
        config.set(SUT_DOCKER_IMAGE_MOUNT_POINTS, ['type=tmpfs,target=/bar'], entity='mysut')

        with patch('virt.docker.Docker'):
            with _create_harness(config) as harness:
                harness.sut.entity = 'mysut'
                scope = Scope(name='myscope')
                node = harness.component_factory.call(DockerContainerNode, scope)

        self.assertEqual(node._image_entity, 'myimage')
        self.assertEqual(node._repository, 'repository')
        self.assertEqual(node._tag, 'v1')
        self.assertEqual(
            node._environment, OrderedDict(
                [('SUT_KEY', 'sut_value'), ('A', 'b'), ('KEY', 'value')]))
        self.assertEqual(node._mounts[0]['Source'], None)
        self.assertEqual(node._mounts[0]['Target'], '/bar')
        self.assertEqual(node._mounts[0]['Type'], 'tmpfs')
        self.assertEqual(node._mounts[0]['ReadOnly'], False)
        self.assertEqual(node._mounts[1]['Source'], None)
        self.assertEqual(node._mounts[1]['Target'], '/foo')
        self.assertEqual(node._mounts[1]['Type'], 'tmpfs')
        self.assertEqual(node._mounts[1]['ReadOnly'], False)

    def test_minimum_config(self):
        config = ConfigManager()
        config.set(SUT, ['mysut'])
        config.set(SUT_DOCKER_IMAGE_ID, 'myimage', entity='mysut')
        config.set(DOCKER_IMAGES_IDS, ['myimage'])
        config.set(DOCKER_IMAGES_REPOSITORY, 'repository', entity='myimage')
        config.set(DOCKER_IMAGES_TAG, 'v1', entity='myimage')

        with patch('virt.docker.Docker'):
            with _create_harness(config) as harness:
                harness.sut.entity = 'mysut'
                scope = Scope(name='myscope')
                node = harness.component_factory.call(DockerContainerNode, scope)

        self.assertEqual(node._image_entity, 'myimage')
        self.assertEqual(node._repository, 'repository')
        self.assertEqual(node._tag, 'v1')
        self.assertEqual(node._hostname, None)
        self.assertEqual(node._image_name, 'repository:v1')
        self.assertEqual(node._timeout, 10)
        self.assertTrue(node._pull)
        self.assertFalse(node._keep_running)

    def test_default_containername(self):
        config = ConfigManager()
        config.set(SUT, ['mysut'])
        config.set(SUT_DOCKER_IMAGE_ID, 'myimage', entity='mysut')
        config.set(DOCKER_IMAGES_IDS, ['myimage'])
        config.set(DOCKER_IMAGES_REPOSITORY, 'repository', entity='myimage')
        config.set(DOCKER_IMAGES_TAG, 'v1', entity='myimage')

        with patch('virt.docker.Docker'):
            with _create_harness(config) as harness:
                harness.sut.entity = 'mysut'
                scope = Scope(name='myscope')
                node = harness.component_factory.call(DockerContainerNode, scope)

        self.assertIsNone(node.containername)

    def test_default_containername_keep_running(self):
        config = ConfigManager()
        config.set(SUT, ['mysut'])
        config.set(SUT_DOCKER_IMAGE_ID, 'myimage', entity='mysut')
        config.set(DOCKER_IMAGES_IDS, ['myimage'])
        config.set(DOCKER_IMAGES_REPOSITORY, 'repository', entity='myimage')
        config.set(DOCKER_IMAGES_TAG, 'v1', entity='myimage')
        config.set(DOCKER_KEEP_RUNNING, True)

        with patch('virt.docker.Docker'):
            with _create_harness(config) as harness:
                harness.sut.entity = 'mysut'
                scope = Scope(name='myscope')
                node = harness.component_factory.call(DockerContainerNode, scope)

        self.assertIn('k2.mysut.', node.containername)

    def test_sut_containername(self):
        config = ConfigManager()
        config.set(SUT, ['mysut'])
        config.set(SUT_DOCKER_IMAGE_ID, 'myimage', entity='mysut')
        config.set(DOCKER_IMAGES_IDS, ['myimage'])
        config.set(DOCKER_IMAGES_REPOSITORY, 'repository', entity='myimage')
        config.set(DOCKER_IMAGES_TAG, 'v1', entity='myimage')
        config.set(SUT_DOCKER_CONTAINER_NAME, 'mycontainer', entity='mysut')

        with patch('virt.docker.Docker'):
            with _create_harness(config) as harness:
                harness.sut.entity = 'mysut'
                scope = Scope(name='myscope')
                node = harness.component_factory.call(DockerContainerNode, scope)

        self.assertIn('mycontainer', node.containername)


class TestDockerContainerExec(TestCase):

    def test_throws_on_unexpected_exit_code(self):
        with _create_harness(ConfigManager()) as harness:
            scope = Scope(name='myscope')
            exec = harness.component_factory.call(DockerContainerExec, scope)
            harness.node._container.exec.return_value = ('stdout', 'stderr', 1)
            with self.assertRaises(DockerError):
                exec.send_line('command', expected_exit_code=0)

    def test_does_not_throw_on_expected_exit_code(self):
        with _create_harness(ConfigManager()) as harness:
            scope = Scope(name='myscope')
            exec = harness.component_factory.call(DockerContainerExec, scope)
            harness.node._container.exec.return_value = ('stdout', 'stderr', 1)
            exec.send_line('command', expected_exit_code=1)

    def test_without_extended_process_information(self):
        with _create_harness(ConfigManager()) as harness:
            scope = Scope(name='myscope')
            exec = harness.component_factory.call(DockerContainerExec, scope)
            harness.node._container.exec.return_value = ('stdout', 'stderr', 0)
            self.assertEqual(
                exec.send_line('command', extended_process_information=False), 'stdoutstderr')

    def test_with_extended_process_information(self):
        with _create_harness(ConfigManager()) as harness:
            scope = Scope(name='myscope')
            exec = harness.component_factory.call(DockerContainerExec, scope)
            harness.node._container.exec.return_value = ('stdout', 'stderr', 0)
            self.assertEqual(
                exec.send_line('command', extended_process_information=True),
                ('stdout', 'stderr', 0))


def _create_harness(config):
    sut = Mock()
    node = Mock()
    harness = ExtensionTestHarness(
        DockerExtension,
        entity='mysut',
        config=config,
        endpoints_and_messages={},
        components=[
            ComponentMock(name='Sut', mock=sut, can=['docker']),
            ComponentMock(name='Node', mock=node, can=['docker']),
        ])
    harness.sut = sut
    harness.node = node
    return harness
