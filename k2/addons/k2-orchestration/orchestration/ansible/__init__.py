from zaf.config.options import ConfigOptionId
from zaf.config.types import Choice, ConfigChoice, Flag, Path
from zaf.messages.message import EndpointId

from k2.sut import SUT

ANSIBLE_ENDPOINT = EndpointId('ansible', 'Ansible Manager')

ANSIBLE_ENABLED = ConfigOptionId(
    'ansible.enabled',
    'Should Ansible support be enabled',
    option_type=Flag(),
    default=False,
)

ANSIBLE_BACKEND = ConfigOptionId(
    'ansible.backend',
    'Backend to test against',
    option_type=Choice(['docker']),
    default='docker',
)

ANSIBLE_CONFIGS = ConfigOptionId(
    'ansible.configs',
    'KEY=value pairs of ansible config. The key should be the Ansible environment variable name of the config option.',
    option_type=str,
    multiple=True,
)

ANSIBLE_CONFIG_FILE = ConfigOptionId(
    'ansible.configfile',
    'Path to ansible.cfg',
    option_type=str,
)

ANSIBLE_LOG_DIR = ConfigOptionId(
    'ansible.log.dir',
    'Relative path to log directory of the ansible log',
    option_type=Path(exists=False),
    default='${log.dir}/ansible',
)

ANSIBLE_PLAYBOOK = ConfigOptionId(
    'ansible.playbook',
    'Relative path to Ansible playbook file',
    option_type=str,
)

ANSIBLE_REMOTE_USER = ConfigOptionId(
    'ansible.remoteuser',
    'Ansible remote user',
    option_type=str,
)

ANSIBLE_EXTRA_VARS = ConfigOptionId(
    'ansible.extravars', (
        'Ansible extra vars. Forwarded directly to ansible as --extra-vars.'
        ' See ansible documentation for supported formats'),
    option_type=str,
    multiple=True)

SUT_ANSIBLE_TEST_NODE = ConfigOptionId(
    'ansible.testnode',
    'Set to true to mark the SUT as a node that should be tested by ansible',
    at=SUT,
    option_type=Flag(),
    default=False,
)

ANSIBLE_NODES = ConfigOptionId(
    'ansible.nodes',
    'List of all ansible nodes.',
    multiple=True,
)

ANSIBLE_NODE = ConfigOptionId(
    'ansible.node',
    'Specify one or more nodes to run test cases for.',
    option_type=ConfigChoice(ANSIBLE_NODES),
    multiple=True,
)

ANSIBLE_SKIP_PLAYBOOK = ConfigOptionId(
    'ansible.skip.playbook',
    'If true the ansible playbook will not be run. '
    'This is good for iterating test case implementation on an already deployed system.',
    option_type=Flag(),
    default=False,
)

ANSIBLE_PARALLEL_RUNS = ConfigOptionId(
    'ansible.parallel.runs',
    'Configure the number of parallel Ansible runs. '
    'If not set the ansible runs will be performed when needed instead of before the test run.',
    option_type=int,
    default=None,
)
