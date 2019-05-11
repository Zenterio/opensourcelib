"""
Provides the *commands* command.

The commands command can be used to list all commands that are provided by the
loaded extensions in zaf.
"""
from textwrap import dedent

from zaf.application import ApplicationContext
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Flag
from zaf.extensions.extension import FrameworkExtension
from zaf.utils.jinja import render_template

_use_short_format = False


def command_list(core):
    """
    List the available commands provided by the loaded extensions.

    Example::

        zaf commands

    Example with short format::

        zaf commands --short
    """
    use_short_format = core.config.get(COMMANDS_SHORT)
    commands = core.extension_manager.get_commands()
    print(format_result(commands, use_short_format))
    return 0


def format_result(commands, use_short_format):
    if use_short_format:
        template_string = dedent(
            """\
            {%- for cmd in commands %}
            {{cmd.name}}
            {%- endfor %}
            """)
    else:
        template_string = dedent(
            """\
            {%- for cmd in commands %}
            {{cmd.name}}
              {%- for line in cmd.description.splitlines() %}
              {{line}}
              {%- endfor %}
            {% endfor %}
            """)
    return render_template(template_string, commands=commands)


COMMANDS_SHORT = ConfigOptionId(
    name='short',
    description='Short format (less information)',
    option_type=Flag(),
    default=False,
    namespace='commands',
    short_alias=True)

COMMANDS_COMMAND = CommandId(
    'commands',
    command_list.__doc__,
    command_list, [ConfigOption(COMMANDS_SHORT, required=False)],
    application_contexts=ApplicationContext.EXTENDABLE)


@FrameworkExtension(name='commandscommand', commands=[COMMANDS_COMMAND])
class CommandsCommand():
    """Provides the commands command."""

    def __init__(self, config, instances):
        pass
