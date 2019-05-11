"""Extension providing the :ref:`command-zebra_make` command."""
import logging

from zaf.commands.command import CommandId
from zaf.component.decorator import requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension
from zaf.messages.message import EndpointId, MessageId

from zebra.docker import docker

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@requires(docker_run='DockerRun')
def make(application, docker_run):
    """
    Run make inside the container.

    The MAKE_ARGUMENTS variable will be forwarded to the make command.

    Example::

    \b
        zebra make -j8 <target>
        MAKE_ARGUMENTS='-j8' make <target>

    """
    make_arguments = application.config.get(MAKE_ARGUMENTS)
    make_command = docker.IMAGES[docker_run.docker_config.image].config.make_command
    application.messagebus.trigger_event(PRE_MAKE, MAKE_ENDPOINT, data=make_arguments)

    command_with_arguments = [make_command]
    command_with_arguments.extend(make_arguments)
    return docker_run.run_in_docker(command_with_arguments, forward_signals=False)


MAKE_ARGUMENTS = ConfigOptionId(
    'arguments',
    'The arguments to make.',
    multiple=True,
    namespace='make',
    argument=True,
)

MAKE_COMMAND = CommandId(
    'make',
    make.__doc__,
    make,
    config_options=[
        ConfigOption(MAKE_ARGUMENTS, required=True),
    ],
    allow_unknown_options=True,
)

MAKE_ENDPOINT = EndpointId('MAKE_ENDPOINT', 'Endpoint for the make command')
PRE_MAKE = MessageId('PRE_MAKE', 'Event triggered before make is executed.')


@FrameworkExtension(
    'makecommand', commands=[MAKE_COMMAND], endpoints_and_messages={
        MAKE_ENDPOINT: [PRE_MAKE]
    })
class MakeExtension(AbstractExtension):
    pass
