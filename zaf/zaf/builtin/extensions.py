"""
Provides the *extensions* command.

The extensions command can show all available extensions and information related
to the extensions such as the endpoints, messages.
"""
from collections import OrderedDict
from textwrap import dedent

from zaf.application import ApplicationContext
from zaf.commands import TARGET_COMMAND
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import ExtensionType, FrameworkExtension
from zaf.utils.jinja import render_template


def list_extensions(core):
    """
    List information about enabled extensions.

    Example to show all command extensions for the run command::

        zaf extensions --target-command run

    Example to also include framework extensions::

        zaf extensions --target-command run --include-framework true
    """
    include_framework = core.config.get(INCLUDE_FRAMEWORK)
    extensions = OrderedDict(
        [
            (extension, endpoints_and_messages)
            for extension, endpoints_and_messages in core.extension_manager.
            get_extensions_endpoints_and_messages(core.config.get(TARGET_COMMAND)).items()
            if include_framework
            or extension.extension_class.extension_type == ExtensionType.COMMAND
        ])
    print(format_result(extensions))
    return 0


def format_result(extensions):
    template_string = dedent(
        """\
        {%- for extension, endpoints_and_messages in extensions.items() %}
        {{extension.name}} ({{extension.extension_class.load_order}})
          {%- for line in extension.description.strip().splitlines() %}
          {{line}}
          {%- endfor %}
          {%- if endpoints_and_messages %}

          endpoints
            {%- for endpoint, messages in endpoints_and_messages.items() %}
            {{endpoint.name}}
              {%- for message in messages %}
              {{message.name}}
              {%- endfor %}
            {%- endfor %}
          {%- endif %}
        {% endfor %}
        """)
    return render_template(template_string, extensions=extensions)


INCLUDE_FRAMEWORK = ConfigOptionId(
    name='include.framework',
    description='Include framework extensions from list',
    option_type=bool,
    default=True,
    namespace='extensions',
    short_alias=True)

EXTENSIONS_COMMAND = CommandId(
    'extensions',
    list_extensions.__doc__,
    list_extensions,
    config_options=[
        ConfigOption(TARGET_COMMAND, required=True),
        ConfigOption(INCLUDE_FRAMEWORK, required=True)
    ],
    application_contexts=ApplicationContext.EXTENDABLE)


@FrameworkExtension(name='extensionscommand', commands=[EXTENSIONS_COMMAND])
class ExtensionsCommand(object):
    """Provides the extensions command."""

    def __init__(self, config, instances):
        pass
