"""Provides the *help* command that can open the user guide and dev guide in different formats."""
import importlib
import inspect
import subprocess
from os.path import exists, join

from zaf.application import APPLICATION_NAME, APPLICATION_ROOT
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Flag
from zaf.extensions.extension import FrameworkExtension


class MultipleTypes(Exception):
    pass


class NoPageFound(Exception):
    pass


class FailedToOpenHelp(Exception):
    pass


def help(core):
    """
    Open guides as HTML or PDF.

    The available guides are user_guide (ug) and dev_guide (dg).

    Examples to open specific guide::

        <main-command> help --html user-guide

        <main-command> help --pdf dev-guide

    Examples to open specific page in HTML user guide::

        <main-command> --component <component name>

        <main-command> --extension <extension name>

        <main-command> --command <command name>

        <main-command> <name to search for>

    """
    config = core.config
    application_name = config.get(APPLICATION_NAME)
    application_root = config.get(APPLICATION_ROOT)

    name = disambiguate_name(config.get(NAME).lower())
    root = get_doc_root(application_name, application_root)

    if config.get(PDF) and config.get(HTML):
        raise MultipleTypes(
            'Error: Multiple documentation types specified. Specify either --html or --pdf')
    elif config.get(PDF):
        if name == 'dev-guide':
            path = join(root, 'dev_guide', 'pdf', 'dev_guide.pdf')
        else:
            path = join(root, 'user_guide', 'pdf', 'user_guide.pdf')
    else:
        path = join(
            root,
            get_html_path(
                name, core.gather_metadata(), config.get(GUIDE), config.get(COMMAND),
                config.get(COMPONENT), config.get(EXTENSION)))

    path = path.replace(' ', '_')

    if config.get(PRINT_PATH):
        print(path)
    else:
        open_with_application(path)


def disambiguate_name(name):
    if name in ['dg', 'dev_guide', 'dev-guide']:
        return 'dev-guide'
    elif name in ['ug', 'user_guide', 'user-guide']:
        return 'user-guide'
    else:
        return name


def get_html_path(name, metadata, is_guide, is_command, is_component, is_extension):
    mapping = create_html_mapping(metadata)
    page_type = get_html_page_type(is_guide, is_command, is_component, is_extension)

    if page_type is not None:
        path = mapping[page_type].get(name)
        if path is None:
            raise NoPageFound(
                "No {page_type} found for name '{name}'".format(page_type=page_type, name=name))
        else:
            return path
    else:
        for page_type in mapping.keys():
            path = mapping[page_type].get(name)
            if path is not None:
                return path
        raise NoPageFound("No HTML page found for name '{name}'".format(name=name))


def get_html_page_type(is_guide, is_command, is_component, is_extension):
    if is_guide:
        return 'guide'
    elif is_command:
        return 'command'
    elif is_component:
        return 'component'
    elif is_extension:
        return 'extension'
    else:
        return None


def create_html_mapping(metadata):
    return {
        'guide': {
            'user-guide': join('user_guide', 'html', 'index.html'),
            'dev-guide': join('dev_guide', 'html', 'index.html'),
        },
        'command': {
            command.short_name.lower(): join(
                'user_guide', 'html', 'commands', '{name}.html'.format(name=command.name.lower()))
            for command in metadata.commands
        },
        'component': {
            component.callable_name.lower(): join(
                'user_guide', 'html', 'components', '{name}.html'.format(name=component.name))
            for component in metadata.components
        },
        'extension': {
            extension.name.lower(): join(
                'user_guide',
                'html',
                'extensions',
                '{name}.html'.format(name=extension.name.lower()))
            for extension in metadata.extensions
        },
    }


def open_with_application(filepath):
    try:
        subprocess.call(('xdg-open', filepath))
    except Exception as e:
        raise FailedToOpenHelp(
            "Failed when trying to use 'xdg-open' to open '{path}': {msg}".format(
                path=filepath, msg=str(e)))


def get_doc_root(application_name, application_root):
    path = inspect.getfile(importlib.import_module(application_root))

    zapplication_name = application_name
    if not application_name.startswith('z'):
        zapplication_name = 'z{application_name}'.format(application_name=application_name)

    if path.startswith(
            '/opt/venvs/zenterio-{zapplication_name}/'.format(zapplication_name=zapplication_name)):
        return '/opt/venvs/zenterio-{zapplication_name}/doc'.format(
            zapplication_name=zapplication_name)
    else:
        project_path = path.replace(
            '{application_root}/__init__.py'.format(application_root=application_root), '')

        new_style_doc_build_path = join(project_path, 'build/doc')

        if exists(new_style_doc_build_path):
            return new_style_doc_build_path
        else:
            return join(project_path, 'doc/build')


NAME = ConfigOptionId('name', 'Name to open', argument=True, namespace='help', short_alias=True)
HTML = ConfigOptionId(
    'html', 'Open HTML documentation', option_type=Flag(), namespace='help', short_alias=True)
PDF = ConfigOptionId(
    'pdf', 'Open PDF documentation', option_type=Flag(), namespace='help', short_alias=True)
GUIDE = ConfigOptionId(
    'guide',
    'Name should be interpreted as a guide',
    option_type=Flag(),
    namespace='help',
    short_alias=True)
COMPONENT = ConfigOptionId(
    'component',
    'Name should be interpreted as a component',
    option_type=Flag(),
    namespace='help',
    short_alias=True)
EXTENSION = ConfigOptionId(
    'extension',
    'Name should be interpreted as an extension',
    option_type=Flag(),
    namespace='help',
    short_alias=True)
COMMAND = ConfigOptionId(
    'command',
    'Name should be interpreted as a command',
    option_type=Flag(),
    namespace='help',
    short_alias=True)
PRINT_PATH = ConfigOptionId(
    'print.path',
    'Print the path to the documentation instead of opening it',
    option_type=Flag(),
    namespace='help',
    short_alias=True)

HELP_COMMAND = CommandId(
    'help',
    help.__doc__,
    help,
    config_options=[
        ConfigOption(NAME, required=True),
        ConfigOption(HTML, required=False),
        ConfigOption(PDF, required=False),
        ConfigOption(GUIDE, required=False),
        ConfigOption(COMPONENT, required=False),
        ConfigOption(EXTENSION, required=False),
        ConfigOption(COMMAND, required=False),
        ConfigOption(PRINT_PATH, required=False),
    ])


@FrameworkExtension(name='helpcommand', commands=[HELP_COMMAND])
class HelpCommand():
    """Provides the help command."""

    def __init__(self, config, instances):
        pass
