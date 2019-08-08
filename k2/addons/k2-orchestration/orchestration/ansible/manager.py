"""
TODO: Write a module docstring for the 'orchestration' addon.

Interact with orchestration tools

Interact with orchestation, provisioning and configuration automation tools such as Puppet and SaltStack.


This text will be added to the extensions chapter of the K2 user guide.
"""

import logging

from zaf.component.decorator import component
from zaf.component.util import add_cans
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, ExtensionConfig, \
    FrameworkExtension, get_logger_name

from k2.cmd.run import PRE_TEST_RUN, RUN_COMMAND
from k2.sut import SUT
from orchestration.ansible import ANSIBLE_BACKEND, ANSIBLE_CONFIG_FILE, ANSIBLE_CONFIGS, \
    ANSIBLE_ENABLED, ANSIBLE_ENDPOINT, ANSIBLE_EXTRA_VARS, ANSIBLE_LOG_DIR, ANSIBLE_NODE, \
    ANSIBLE_NODES, ANSIBLE_PLAYBOOK, ANSIBLE_REMOTE_USER, ANSIBLE_SKIP_PLAYBOOK, \
    SUT_ANSIBLE_TEST_NODE
from orchestration.ansible.config import AnsibleConfig

logger = logging.getLogger(get_logger_name('k2', 'ansible'))
logger.addHandler(logging.NullHandler())


def get_backend(backend, ansible_config):
    if backend == 'docker':
        from .backends.docker import DockerBackend
        return DockerBackend(ansible_config)
    else:
        raise Exception('Unknown backend {backend}'.format(backend=backend))


@CommandExtension(
    name='ansible',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT_ANSIBLE_TEST_NODE, required=True),
        ConfigOption(SUT, required=False, instantiate_on=True),
    ],
    groups=['orchestation'],
    endpoints_and_messages={})
class AnsibleAddSutCansExtension(AbstractExtension):
    """Extension that adds additional cans on SUTs configured as ansible test nodes."""

    def __init__(self, config, instances):
        self._entity = instances[SUT]
        self._enabled = config.get(SUT_ANSIBLE_TEST_NODE)

    def register_components(self, component_manager):
        if self._enabled is True:
            sut = component_manager.get_unique_class_for_entity(self._entity)
            add_cans(sut, ['ansibletestnode'])
            logger.debug('Adding can ansibletestnode to {entity}'.format(entity=self._entity))
        else:
            logger.debug('{entity} is not ansibletestnode'.format(entity=self._entity))


@CommandExtension(
    'ansible',
    extends=['sut'],
    config_options=[
        ConfigOption(ANSIBLE_NODES, required=False),
        ConfigOption(ANSIBLE_NODE, required=False),
        ConfigOption(ANSIBLE_ENABLED, required=True),
    ],
    groups=['orchestration'])
class AnsibleSutsConfig(AbstractExtension):
    """Defines ansible node options as command options."""
    pass


@FrameworkExtension('ansible', load_order=91, groups=['orchestration'])
class AnsibleSuts(AbstractExtension):
    """Interprets ansible node options to create suts.ids."""

    def get_config(self, config, requested_config_options, requested_command_config_options):
        if config.get(ANSIBLE_ENABLED, False):
            selected_nodes = config.get(ANSIBLE_NODE)

            if selected_nodes:
                config = {'suts.ids': selected_nodes}
            else:
                config = {'suts.ids': config.get(ANSIBLE_NODES)}
        else:
            config = {}

        return ExtensionConfig(config, priority=1, source='ansiblesuts')


@CommandExtension(
    name='ansible',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(ANSIBLE_ENABLED, required=True),
        ConfigOption(ANSIBLE_BACKEND, required=False),
        ConfigOption(ANSIBLE_CONFIG_FILE, required=False),
        ConfigOption(ANSIBLE_CONFIGS, required=False),
        ConfigOption(ANSIBLE_LOG_DIR, required=False),
        ConfigOption(ANSIBLE_PLAYBOOK, required=False),
        ConfigOption(ANSIBLE_REMOTE_USER, required=False),
        ConfigOption(ANSIBLE_EXTRA_VARS, required=False),
        ConfigOption(ANSIBLE_SKIP_PLAYBOOK, required=False),
    ],
    endpoints_and_messages={ANSIBLE_ENDPOINT: [PRE_TEST_RUN]},
    groups=['orchestration'],
    activate_on=[ANSIBLE_ENABLED])
class AnsibleManager(AbstractExtension):
    """
    Extension for testing ansible playbooks.

    The ansible extension supports multiple backends.
    """

    def __init__(self, config, instances):
        self._enabled = config.get(ANSIBLE_ENABLED)
        if self._enabled:
            self._ansible_config = AnsibleConfig(
                config.get(ANSIBLE_CONFIG_FILE),
                config.get(ANSIBLE_PLAYBOOK),
                log_dir=config.get(ANSIBLE_LOG_DIR),
                environmental_config=config.get(ANSIBLE_CONFIGS),
                remote_user=config.get(ANSIBLE_REMOTE_USER),
                extra_vars=config.get(ANSIBLE_EXTRA_VARS))
            self._backend_name = config.get(ANSIBLE_BACKEND)
            self._backend = get_backend(self._backend_name, self._ansible_config)

    def register_components(self, component_manager):
        if self._enabled:

            @component(
                name='AnsibleConfig',
                can=['ansiblebackend:{backend}'.format(backend=self._backend_name)],
                component_manager=component_manager)
            def ansible_config():
                return self._ansible_config

            self._backend.register_components(component_manager)
