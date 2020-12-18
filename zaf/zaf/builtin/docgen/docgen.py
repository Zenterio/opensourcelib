"""Generates documentation from information inside zaf."""
import os
import shutil
from collections import namedtuple

from zaf.application import APPLICATION_CONTEXT, APPLICATION_NAME, APPLICATION_ROOT, \
    APPLICATION_VERSION, ENTRYPOINT_NAME
from zaf.application.context import ApplicationContext
from zaf.application.metadata import MetadataFilter
from zaf.builtin.docgen import DOCGEN_COMMAND_ENDPOINT, GET_CUSTOM_DOC_FILES, GET_CUSTOM_DOCS, \
    GET_CUSTOM_LOGGING_DOCS, DocTemplate
from zaf.commands.command import CommandId
from zaf.component.decorator import requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Flag
from zaf.extensions.extension import AbstractExtension, CommandExtension, FrameworkExtension
from zaf.messages.decorator import callback_dispatcher
from zaf.utils.modulepaths import get_file_path_to_module

from .template import render_sphinx_template

DocFilter = namedtuple(
    'DocFilter', ['include_components', 'include_endpoints_and_messages', 'include_classes'])


@requires(changelog='ChangeLog')
@requires(messagebus='MessageBus')
def docgen(core, changelog, messagebus):
    """Generate documentation for the application."""
    doc_dir = core.config.get(DOC_DIR)
    include_components = core.config.get(INCLUDE_COMPONENTS)
    include_endpoints_and_messages = core.config.get(INCLUDE_ENDPOINTS_AND_MESSAGES)
    include_classes = core.config.get(INCLUDE_CLASSES)
    limit_extension_namespaces = core.config.get(LIMIT_EXTENSION_NAMESPACES)
    additional_extensions = core.config.get(ADDITIONAL_EXTENSIONS)
    include_hidden_commands = core.config.get(INCLUDE_HIDDEN_COMMANDS)
    include_hidden_options = core.config.get(INCLUDE_HIDDEN_OPTIONS)
    application_context = core.config.get(APPLICATION_CONTEXT)
    os.makedirs(doc_dir, exist_ok=True)

    custom_logging_items = copy_custom_files(
        doc_dir, request_custom_content(messagebus, GET_CUSTOM_LOGGING_DOCS))

    custom_docs = request_custom_content(messagebus, GET_CUSTOM_DOCS)

    copy_custom_files(doc_dir, request_custom_content(messagebus, GET_CUSTOM_DOC_FILES))

    template_variables = {
        'application_name': core.config.get(APPLICATION_NAME),
        'application_version': core.config.get(APPLICATION_VERSION),
        'application_dir': find_application_dir(core.config.get(APPLICATION_ROOT)),
        'entrypoint_name': core.config.get(ENTRYPOINT_NAME),
        'include_config_command': application_context == ApplicationContext.EXTENDABLE,
        'application_context': application_context.name,
        'custom_logging_items': custom_logging_items,
        'custom_index_entries': [os.path.splitext(doc.filename)[0] for doc in custom_docs],
        'plantuml_path': find_plant_uml(),
        'changelog': changelog.changelog,
        'include_components': include_components,
        'include_endpoints_and_messages': include_endpoints_and_messages,
    }

    generate_documentation(
        doc_dir,
        core.gather_metadata(
            MetadataFilter(
                application_context, include_hidden_commands, include_hidden_options,
                limit_extension_namespaces, additional_extensions)), changelog, template_variables,
        DocFilter(include_components, include_endpoints_and_messages, include_classes), custom_docs)

    with open(os.path.join(doc_dir, 'result'), 'w') as f:
        # used for make target
        f.write('ok')


def request_custom_content(messagebus, message_id):
    custom_docs = []

    for future in messagebus.send_request(message_id).as_completed():
        docs = future.result()
        custom_docs.extend(docs)
    return custom_docs


def find_plant_uml():
    return os.path.join(get_file_path_to_module('zaf.builtin.docgen'), 'tools/plantuml.jar')


def find_application_dir(application_root):
    return os.path.dirname(get_file_path_to_module(application_root))


def generate_documentation(
        doc_dir, metadata, changelog, template_variables, doc_filter, custom_docs):

    for doc_template in custom_docs:
        generate_custom_doc(
            doc_dir,
            doc_template.filename,
            metadata,
            template_variables,
            doc_filter,
            package=doc_template.package,
            template_dir=doc_template.template_dir)

    generate_file(doc_dir, 'conf.py', metadata, template_variables, doc_filter)

    generate_directory(
        doc_dir, 'extension', metadata.extensions, metadata, template_variables, doc_filter)
    generate_list_file(
        doc_dir, 'extension', metadata.extensions, metadata, template_variables, doc_filter)
    generate_directory(
        doc_dir, 'command', metadata.commands, metadata, template_variables, doc_filter)
    generate_list_file(
        doc_dir, 'command', metadata.commands, metadata, template_variables, doc_filter)
    generate_file(doc_dir, 'index.rst', metadata, template_variables, doc_filter)
    generate_file(doc_dir, 'logging.rst', metadata, template_variables, doc_filter)
    generate_file(doc_dir, 'configuration.rst', metadata, template_variables, doc_filter)

    if doc_filter.include_components:
        generate_file(doc_dir, 'components.rst', metadata, template_variables, doc_filter)
        generate_directory(
            doc_dir, 'component', metadata.components, metadata, template_variables, doc_filter)
        generate_list_file(
            doc_dir, 'component', metadata.components, metadata, template_variables, doc_filter)
    generate_list_file(
        doc_dir, 'config_option_id', metadata.config_option_ids, metadata, template_variables,
        doc_filter)
    if doc_filter.include_endpoints_and_messages:
        generate_file(doc_dir, 'messages.rst', metadata, template_variables, doc_filter)
        generate_list_file(
            doc_dir, 'endpoint', metadata.endpoints, metadata, template_variables, doc_filter)
        generate_list_file(
            doc_dir, 'message', metadata.messages, metadata, template_variables, doc_filter)
    if changelog.changelog:
        generate_changelog(doc_dir, changelog.changelog)


def generate_directory(doc_dir, item_type, items, metadata, template_variables, doc_filter):
    dir = os.path.join(doc_dir, '{type}s'.format(type=item_type))
    os.makedirs(dir, exist_ok=True)
    for item in items:
        variables = {
            item_type: item,
            'metadata': metadata,
            'filter': doc_filter,
        }
        variables.update(template_variables)
        output = render_sphinx_template('{type}.rst'.format(type=item_type), **variables)
        with open(file_path(dir, '{name}.rst'.format(name=item.name)), 'w') as f:
            f.write(output)


def generate_list_file(doc_dir, item_type, items, metadata, template_variables, doc_filter):
    file_name = '{type}_list.rst'.format(type=item_type)
    with open(file_path(doc_dir, file_name), 'w') as f:
        variables = {
            '{type}s'.format(type=item_type): items,
            'metadata': metadata,
            'filter': doc_filter,
        }
        variables.update(template_variables)
        output = render_sphinx_template(file_name, **variables)
        f.write(output)


def generate_file(doc_dir, file_name, metadata, template_variables, doc_filter):
    with open(file_path(doc_dir, file_name), 'w') as f:
        variables = {
            'metadata': metadata,
            'filter': doc_filter,
        }
        variables.update(template_variables)
        output = render_sphinx_template(file_name, **variables)
        f.write(output)


def generate_custom_doc(
        doc_dir, file_name, metadata, template_variables, doc_filter, package, template_dir):
    with open(file_path(doc_dir, file_name), 'w') as f:
        variables = {
            'metadata': metadata,
            'filter': doc_filter,
        }
        variables.update(template_variables)
        output = render_sphinx_template(
            file_name, package=package, template_dir=template_dir, **variables)
        f.write(output)


def generate_changelog(doc_dir, changelog):
    file_name = 'changelog.rst'
    with open(file_path(doc_dir, file_name), 'w') as f:
        output = render_sphinx_template(file_name, changelog=changelog)
        f.write(output)


def copy_custom_files(doc_dir, custom_docs):
    paths = []
    for file in custom_docs:
        path = os.path.join(get_file_path_to_module(file.package), file.template_dir, file.filename)
        shutil.copy(path, doc_dir)
        paths.append(os.path.basename(path))
    return paths


def file_path(dir, name):
    return os.path.join(dir, name.replace(' ', '_'))


DOC_DIR = ConfigOptionId(
    'doc.dir',
    'Directory to store generated documentation in',
    default='${output.dir}/docs',
    namespace='docgen',
    short_alias=True)

LIMIT_EXTENSION_NAMESPACES = ConfigOptionId(
    'limit.extension.namespaces',
    'If given extensions will only be included if they match the namespaces.',
    multiple=True,
    namespace='docgen',
    short_alias=True)

ADDITIONAL_EXTENSIONS = ConfigOptionId(
    'additional.extensions',
    "Include additional extensions that don't match the given namespaces.",
    multiple=True,
    namespace='docgen',
    short_alias=True)

INCLUDE_COMPONENTS = ConfigOptionId(
    'include.components',
    'Include components in the generated documentation.',
    option_type=Flag(),
    default=True,
    namespace='docgen',
    short_alias=True)

INCLUDE_ENDPOINTS_AND_MESSAGES = ConfigOptionId(
    'include.endpoints.and.messages',
    'Include endpoints and messages in the generated documentation.',
    option_type=Flag(),
    default=True,
    namespace='docgen',
    short_alias=True)

INCLUDE_CLASSES = ConfigOptionId(
    'include.classes',
    'Include classes in the generated documentation.',
    option_type=Flag(),
    default=True,
    namespace='docgen',
    short_alias=True)

INCLUDE_HIDDEN_COMMANDS = ConfigOptionId(
    'include.hidden.commands',
    'Include hidden commands in the generated documentation.',
    option_type=Flag(),
    default=True,
    namespace='docgen',
    short_alias=True)

INCLUDE_HIDDEN_OPTIONS = ConfigOptionId(
    'include.hidden.options',
    'Include hidden options in the generated documentation.',
    option_type=Flag(),
    default=True,
    namespace='docgen',
    short_alias=True)

DOCGEN_COMMAND = CommandId(
    'docgen',
    docgen.__doc__,
    docgen,
    config_options=[
        ConfigOption(DOC_DIR, required=True),
        ConfigOption(LIMIT_EXTENSION_NAMESPACES, required=False),
        ConfigOption(ADDITIONAL_EXTENSIONS, required=False),
        ConfigOption(INCLUDE_COMPONENTS, required=True),
        ConfigOption(INCLUDE_ENDPOINTS_AND_MESSAGES, required=True),
        ConfigOption(INCLUDE_CLASSES, required=True),
        ConfigOption(INCLUDE_HIDDEN_COMMANDS, required=True),
        ConfigOption(INCLUDE_HIDDEN_OPTIONS, required=True),
    ],
    hidden=True,
    uses=['changelog'],
)


@FrameworkExtension(
    name='docgencommand',
    commands=[DOCGEN_COMMAND],
    endpoints_and_messages={
        DOCGEN_COMMAND_ENDPOINT: [GET_CUSTOM_DOCS, GET_CUSTOM_DOC_FILES, GET_CUSTOM_LOGGING_DOCS]
    })
class DocGenCommand(object):
    """Provides the docgen command."""

    def __init__(self, config, instances):
        pass


@CommandExtension(
    name='zafdocs',
    extends=[DOCGEN_COMMAND],
)
class ZafCustomDocs(AbstractExtension):
    """Provides zaf specific docs that shouldn't be included in zaf based applications."""

    @callback_dispatcher([GET_CUSTOM_DOCS], priority=1000)
    @requires(config='Config')
    def get_custom_docs(self, message, config):
        if config.get(APPLICATION_NAME) == 'zaf':
            return [DocTemplate('zaf.builtin.docgen', 'templates', 'intro.rst')]
        else:
            return []
