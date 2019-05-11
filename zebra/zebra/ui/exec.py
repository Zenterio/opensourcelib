"""Extension providing the :ref:`command-zebra_exec` command."""
import logging

from zaf.commands.command import CommandId
from zaf.component.decorator import requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@requires(docker_run='DockerRun')
def exec(application, docker_run):
    """
    Execute any command inside a container.

    ABS related environment variables will be forwarded and available inside the container.

    This is used to run any command with any arguments and also use bash syntax to use variables
    or other more advanced functionalities.
    The only limitation is that the command uses applications that are installed in or mounted
    into the container.

    \b
    Basic Usage
    ===========

    The simplest example::

        zebra exec <command>

    \b
    Variable Expansion
    ==================

    Variable expansion can be delayed to inside the container by wrapping the whole command in single quotes.

    Example that prints value of variable inside the container, in this case /zebra/workspace::

        zebra exec 'echo $PWD'

    Without the single quotes the variable will be expanded outside of the container,
    in this case the current working directory::

        zebra exec echo $PWD

    \b
    Complex Expressions
    ===================

    Here are some more complex examples::

    \b
        zebra exec ZBLD_CCACHE=y make P=product bootimage
        zebra exec "do something; do something else"
        zebra exec "do something || do something if that failed"

    """

    command_with_arguments = application.config.get(EXEC_COMMAND_WITH_ARGUMENTS)

    return docker_run.run_in_docker(command_with_arguments, forward_signals=False)


EXEC_COMMAND_WITH_ARGUMENTS = ConfigOptionId(
    'command.with.arguments',
    'The command to run.',
    multiple=True,
    namespace='exec',
    argument=True,
)

EXEC_COMMAND = CommandId(
    'exec',
    exec.__doc__,
    exec,
    config_options=[
        ConfigOption(EXEC_COMMAND_WITH_ARGUMENTS, required=True),
    ],
    allow_unknown_options=True,
)


@FrameworkExtension(
    'execcommand',
    commands=[EXEC_COMMAND],
)
class ExecExtension(AbstractExtension):
    pass
