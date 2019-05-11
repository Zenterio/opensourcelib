"""Extension providing the :ref:`command-zebra_shell` command."""
import logging

from zaf.commands.command import CommandId
from zaf.component.decorator import requires
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@requires(docker_run='DockerRun')
def shell(application, docker_run):
    """
    Start a shell inside a container.

    This will behave similar to running /bin/bash and will start a new shell but it will be running
    inside the container.
    Write 'exit' to exit the shell.
    """
    return docker_run.run_in_docker(['/bin/bash'], forward_signals=True)


SHELL_COMMAND = CommandId(
    'shell',
    shell.__doc__,
    shell,
    config_options=[],
)


@FrameworkExtension(
    'shellcommand',
    commands=[SHELL_COMMAND],
)
class ShellExtension(AbstractExtension):
    pass
