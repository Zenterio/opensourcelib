"""
Provides the *endpoints* command.

The endpoints command can show all available endpoints for a specific command
and the messages that are defined for the endpoints.
"""

from textwrap import dedent

from zaf.application import ApplicationContext
from zaf.commands import TARGET_COMMAND
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption
from zaf.extensions.extension import FrameworkExtension
from zaf.utils.jinja import render_template


def endpoints(core):
    """
    Show endpoints and the messages defined for the endpoints.

    Example to show all endpoints and messages for the run command::

        zaf endpoints --target-command run
    """
    endpoints_and_messages = core.extension_manager.get_endpoints_and_messages(
        core.config.get(TARGET_COMMAND))
    print(format_result(endpoints_and_messages))
    return 0


def format_result(endpoints_and_messages):
    template_string = dedent(
        """\
            {%- for endpoint, messages in endpoints_and_messages.items() %}
            {{endpoint.name}}
              {%- for line in endpoint.description.strip().splitlines() %}
              {{line}}
              {%- endfor %}
              {%- if messages %}

              messages
                {%- for message in messages %}
                {{message.name}}
                {%- endfor %}
              {%- endif %}
            {% endfor %}
            """)
    return render_template(template_string, endpoints_and_messages=endpoints_and_messages)


ENDPOINTS_COMMAND = CommandId(
    'endpoints',
    endpoints.__doc__,
    endpoints,
    config_options=[ConfigOption(TARGET_COMMAND, required=True)],
    application_contexts=ApplicationContext.EXTENDABLE)


@FrameworkExtension('endpointscommand', commands=[ENDPOINTS_COMMAND])
class EndpointsCommand():
    """Provides the endpoints command."""

    def __init__(self, config, instances):
        pass
