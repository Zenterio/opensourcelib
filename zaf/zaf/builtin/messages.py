"""
Provides the *messages* command.

The messages command can be used to show all messages and endpoints related to
the message.
"""
from textwrap import dedent

from zaf.application import ApplicationContext
from zaf.commands import TARGET_COMMAND
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption
from zaf.extensions.extension import FrameworkExtension
from zaf.messages.messagebus import MessageBus
from zaf.utils.jinja import render_template


def messages(core):
    """
    List messages and the endpoints that are defined for the messages.

    Example to show all messages and endpoints for the run command::

        zaf messages --target-command run
    """
    messagebus = MessageBus(component_factory=None)
    messagebus.define_endpoints_and_messages(
        core.extension_manager.get_endpoints_and_messages(core.config.get(TARGET_COMMAND)))
    messages_with_endpoints = messagebus.get_defined_messages_and_endpoints()
    print(format_result(messages_with_endpoints))
    return 0


def format_result(messages_with_endpoints):
    template_string = dedent(
        """\
            {%- for message, endpoints in messages_with_endpoints.items() %}
            {{message.name}}
              {%- for line in message.description.strip().splitlines() %}
              {{line}}
              {%- endfor %}
              {%- if endpoints %}

              endpoints
                {%- for endpoint in endpoints %}
                {{endpoint.name}}
                {%- endfor %}
              {%- endif %}
            {% endfor %}
            """)
    return render_template(template_string, messages_with_endpoints=messages_with_endpoints)


MESSAGES_COMMAND = CommandId(
    'messages',
    messages.__doc__,
    messages,
    config_options=[ConfigOption(TARGET_COMMAND, required=True)],
    application_contexts=ApplicationContext.EXTENDABLE)


@FrameworkExtension(name='messagescommand', commands=[MESSAGES_COMMAND])
class MessagesCommand():
    """Provides the messages command."""

    def __init__(self, config, instances):
        pass
