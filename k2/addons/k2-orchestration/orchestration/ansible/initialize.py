import logging
from textwrap import dedent

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher
from zaf.messages.dispatchers import ThreadPoolDispatcher
from zaf.messages.message import EndpointId, MessageId

from k2.cmd.run import INITIALIZE_SUT, POST_INITIALIZE_SUT
from k2.sut import SUT
from orchestration.ansible import SUT_ANSIBLE_TEST_NODE

from . import ANSIBLE_PARALLEL_RUNS

logger = logging.getLogger(get_logger_name('k2', 'initansible'))
logger.addHandler(logging.NullHandler())

INITIALIZE_ANSIBLE_SUTS_ENDPOINT = EndpointId(
    'INITIALIZE_ANSIBLE_SUTS_ENDPOINT', 'Endpoint for initializing Ansible Suts')

INITIALIZE_ANSIBLE_NODE = MessageId(
    'INITIALIZE_ANSIBLE_NODE',
    dedent(
        """\
    Trigger initiation of the Ansible node specified by the message entity.
    """))


@CommandExtension(
    name='ansible',
    extends=['sut'],
    config_options=[
        ConfigOption(SUT, required=False),
        ConfigOption(ANSIBLE_PARALLEL_RUNS, required=False),
        ConfigOption(SUT_ANSIBLE_TEST_NODE, required=False),
    ],
    endpoints_and_messages={INITIALIZE_ANSIBLE_SUTS_ENDPOINT: [INITIALIZE_ANSIBLE_NODE]},
    activate_on=[ANSIBLE_PARALLEL_RUNS])
class InitializeAnsibleSuts(AbstractExtension):
    """
    Handles initialization of Ansible suts before the test suite has started.

    This is activated by setting the :ref:`option-ansible.parallel.runs` option.
    If not activated the default functionality is to initialize the Ansible suts when
    they are needed by a test case.
    """

    def __init__(self, config, instances):
        self._futures = {}
        self._parallel_runs = config.get(ANSIBLE_PARALLEL_RUNS)
        self._suts = config.get(SUT)
        self._ansible_nodes = [
            node for node in config.get(SUT) if config.get(SUT_ANSIBLE_TEST_NODE, entity=node)
        ]

        self._dispatcher = None

    def register_dispatchers(self, messagebus):
        """
        Create a special ThreadPoolDispatcher that registers to all Ansible sut entities.

        This is needed because send_request when sent with an entity will not be received by
        dispatchers that are not explicitly registered with that entity.
        The reason we need send_request with the entity is that we depend on the fixate_on_entities
        functionality to get the correct component initialized.
        """

        # activate_on currently only applies to decorator dispatchers
        if self._parallel_runs:
            self._dispatcher = ThreadPoolDispatcher(
                messagebus, self.initialize_ansible_node, max_workers=self._parallel_runs)
            self._dispatcher.register(
                [INITIALIZE_ANSIBLE_NODE], [INITIALIZE_ANSIBLE_SUTS_ENDPOINT], self._ansible_nodes)

    def destroy(self):
        if self._dispatcher:
            self._dispatcher.destroy()

    @callback_dispatcher([INITIALIZE_SUT])
    @requires(messagebus='MessageBus')
    def initialize_sut(self, message, messagebus):
        """Trigger initialize sut in parallel on all Ansible nodes."""
        if message.entity in self._ansible_nodes:
            self._futures[message.entity] = messagebus.send_request(
                INITIALIZE_ANSIBLE_NODE, INITIALIZE_ANSIBLE_SUTS_ENDPOINT, entity=message.entity)

    @requires(node='AnsibleNode')
    def initialize_ansible_node(self, message, node):
        """Initialize the AnsibleNode component for the sut matching the message entity."""
        return node

    @callback_dispatcher([POST_INITIALIZE_SUT])
    def post_initialize(self, message):
        """
        Wait for initialize sut for the sut matching the message entity to be complete.

        Logs any error messages but doesn't leak the exception which will lead
        to the test run to continue for the other suts.
        """
        if message.entity in self._ansible_nodes:
            try:
                self._futures[message.entity].wait()[0].result()
            except Exception as e:
                msg = f'Error occurred when initializing {message.entity}: {str(e)}'
                logger.warning(msg)
                logger.debug(msg, exc_info=True)
