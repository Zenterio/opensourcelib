"""
The click extension is implemented as a general config providing framework extension.

It parses the command line using the `click <http://click.pocoo.org/>`_ package.

The implementation is spread out over multiple classes with different load order that deals with
different parts of the command line.

All config provided by the click extension has priority 100 to make it possible to override any config
from the command line.
"""

import logging
import re
import sys

import click

from zaf.application import APPLICATION_CONTEXT, APPLICATION_VERSION, ENTRYPOINT_NAME
from zaf.builtin.click.check_duplicates import check_for_ambiguous_duplicates
from zaf.commands import COMMAND
from zaf.config.options import ConfigOption
from zaf.config.types import Choice, ConfigChoice, Count, Entity, Flag, GlobPattern, Path
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension, \
    get_logger_name
from zaf.utils.bashcompletion import is_bash_completion

logger = logging.getLogger(get_logger_name('zaf', 'click'))
logger.addHandler(logging.NullHandler())

CLICK_CONFIG_PRIORITY = 100
IS_BASH_COMPLETION = is_bash_completion()

HELP_OPTIONS = ['-h', '--help', '--full-help']
FULL_HELP_OPTIONS = ['--full-help']
VERSION_OPTIONS = ['--version']


@FrameworkExtension(
    name='click', load_order=1, config_options=[ConfigOption(ENTRYPOINT_NAME, required=True)])
class ClickInitPluginPath(AbstractExtension):
    """Parses command line for initial config options."""

    def __init__(self, config, instances):

        # Make click parsing work for bashcomplete
        # We need to be able to parse sys.argv but when using bashcomplete it is empty
        # and all variables are stored in COMP_WORDS
        if IS_BASH_COMPLETION:
            from click.parser import split_arg_string
            import os
            sys.argv = split_arg_string(os.getenv('COMP_WORDS'))

    def get_config(self, config, requested_config_options, requested_command_config_options):
        prog_name = config.get(ENTRYPOINT_NAME, 'zaf')
        check_for_ambiguous_duplicates(
            prog_name, requested_config_options, requested_command_config_options)
        return ExtensionConfig(
            parse_partial(config, prog_name, requested_config_options),
            priority=CLICK_CONFIG_PRIORITY)


@FrameworkExtension(
    name='click', load_order=11, config_options=[ConfigOption(ENTRYPOINT_NAME, required=True)])
class ClickInitExtensions(AbstractExtension):
    """Parses command line for disabling of extensions."""

    def get_config(self, config, requested_config_options, requested_command_config_options):
        prog_name = config.get(ENTRYPOINT_NAME, 'zaf')
        check_for_ambiguous_duplicates(
            prog_name, requested_config_options, requested_command_config_options)
        return ExtensionConfig(
            parse_partial(config, prog_name, requested_config_options),
            priority=CLICK_CONFIG_PRIORITY)


@FrameworkExtension(
    name='click', load_order=21, config_options=[ConfigOption(ENTRYPOINT_NAME, required=True)])
class ClickExtensionOptions(AbstractExtension):
    """Parses complete command line."""

    def get_config(self, config, requested_config_options, requested_command_config_options):
        prog_name = config.get(ENTRYPOINT_NAME, 'zaf')
        check_for_ambiguous_duplicates(
            prog_name, requested_config_options, requested_command_config_options)
        return ExtensionConfig(
            parse_partial(config, prog_name, requested_config_options),
            priority=CLICK_CONFIG_PRIORITY)


def parse_partial(config, name, requested_config_options):
    application_context = config.get(APPLICATION_CONTEXT)

    click_config, click_options = try_to_parse_config_options(
        config,
        name,
        get_applicable_options(requested_config_options, application_context),
        ignore_hidden=False)
    defaults = {translate_param_to_config(option.name): option.default for option in click_options}
    filtered_config = filter_out_same_as_defaults(click_config, defaults)
    return filtered_config


class FullClickParseCli(AbstractExtension):
    """Base class for extensions parsing the complete command line."""

    def __init__(self, try_to_parse):
        self.try_to_parse = try_to_parse

    def get_config(self, config, requested_config_options, requested_command_config_options):
        application_context = config.get(APPLICATION_CONTEXT)
        ignore_hidden = any_option_in_sys_argv(FULL_HELP_OPTIONS) or IS_BASH_COMPLETION

        main_options = prepare_config_options(
            config,
            None,
            get_applicable_options(requested_config_options, application_context),
            ignore_hidden,
            disable_required=self.try_to_parse)
        main_defaults = {
            translate_param_to_config(option.name): option.default
            for option in main_options
        }
        prog_name = config.get(ENTRYPOINT_NAME, 'zaf')
        version = config.get(APPLICATION_VERSION)

        try:
            main_command = ClickCommandWithConfigOptions(
                config,
                command=None,
                all_commands=requested_command_config_options.keys(),
                command_config_options=requested_command_config_options,
                application_context=application_context,
                ignore_hidden=ignore_hidden,
                disable_required=self.try_to_parse,
                name=prog_name,
                params=main_options,
                context_settings={
                    'help_option_names': HELP_OPTIONS
                })
            click.version_option(version)(main_command)

            is_help_or_version = (
                any_option_in_sys_argv(HELP_OPTIONS) or any_option_in_sys_argv(VERSION_OPTIONS))

            if self.try_to_parse:
                args = [
                    arg for arg in sys.argv
                    if arg not in HELP_OPTIONS and arg not in VERSION_OPTIONS
                ][1:]
                try:
                    # Special call to main that tries to parse the command line
                    main_command.main(
                        args=args,
                        prog_name=prog_name,
                        standalone_mode=False,
                        allow_extra_args=True,
                        ignore_unknown_options=True)
                except click.exceptions.UsageError:
                    # Continuing and letting load order 100 parsing give a correct error message
                    # This can happen for example for zaf --help because there is no subcommand
                    return []
            else:
                main_command.main(standalone_mode=False, prog_name=prog_name, max_content_width=120)

                if is_help_or_version:
                    if (any_option_in_sys_argv(HELP_OPTIONS)
                            and not any_option_in_sys_argv(FULL_HELP_OPTIONS)):
                        print()
                        print('To see hidden commands and options use --full-help.')
                    sys.exit(0)

            click_config = main_command.created_config
            defaults = main_defaults.copy()

            command = main_command
            while type(command) == ClickCommandWithConfigOptions:
                defaults.update(command.command_defaults)
                click_config.update(command.created_config)
                command = command.executed_command

            click_config[COMMAND.name] = command.name
            filtered_config = filter_out_same_as_defaults(click_config, defaults)
            return ExtensionConfig(filtered_config, priority=CLICK_CONFIG_PRIORITY)
        except click.exceptions.ClickException as e:
            logger.debug(e.format_message(), exc_info=True)
            e.show(file=sys.stdout)
            exit(2)


@FrameworkExtension(
    name='click', load_order=90, config_options=[ConfigOption(ENTRYPOINT_NAME, required=True)])
class ClickTryParseCli(FullClickParseCli):
    """Provides early parsing of command parameters to be able to use them before load_order 100."""

    def __init__(self, config, instances):
        super().__init__(try_to_parse=True)


@FrameworkExtension(
    name='click', load_order=100, config_options=[ConfigOption(ENTRYPOINT_NAME, required=True)])
class ClickParseCli(FullClickParseCli):
    """Parses of command line and fails on missing required options."""

    def __init__(self, config, instances):
        super().__init__(try_to_parse=False)


class ClickCommandWithConfigOptions(click.MultiCommand):

    def __init__(
            self, config, command, all_commands, command_config_options, application_context,
            ignore_hidden, disable_required, *args, **kwargs):
        super().__init__(*args, no_args_is_help=False, **kwargs)
        self.config = config
        self._application_context = application_context
        self._command = command
        self._all_commands = list(get_applicable_commands(all_commands, self._application_context))
        self._command_config_options = command_config_options
        self._ignore_hidden = ignore_hidden
        self._disable_required = disable_required

    @property
    def sub_commands(self):
        return {
            command.name.lower(): command
            for command in self._all_commands if command.parent == self._command
        }

    def list_commands(self, ctx):
        return sorted(self.sub_commands.keys())

    def get_command(self, ctx, name):
        if name in self.sub_commands:
            sub_command = self.sub_commands[name]
            sub_command_config_options = self._command_config_options.get(sub_command, [])
            options = prepare_config_options(
                self.config, name,
                get_applicable_options(sub_command_config_options, self._application_context),
                self._ignore_hidden, self._disable_required)

            sub_sub_commands = [cmd for cmd in self._all_commands if cmd.parent == sub_command]

            if sub_sub_commands:
                return ClickCommandWithConfigOptions(
                    self.config,
                    command=sub_command,
                    all_commands=self._all_commands,
                    command_config_options=self._command_config_options,
                    application_context=self._application_context,
                    ignore_hidden=self._ignore_hidden,
                    disable_required=self._disable_required,
                    name=name,
                    params=options,
                    callback=click.pass_context(self.register_command))
            else:
                return click.Command(
                    name,
                    params=options,
                    help=sub_command.description,
                    hidden=not self._ignore_hidden and sub_command.hidden,
                    callback=click.pass_context(self.register_command),
                    context_settings={
                        'allow_extra_args': sub_command.allow_unknown_options,
                        'ignore_unknown_options': sub_command.allow_unknown_options
                    })

    def register_command(self, context, **kwargs):
        self.executed_command = context.command
        self.command_defaults = {
            translate_param_to_config(option.name): option.default
            for option in context.command.params
        }
        all_params = list(context.params.items()) + list(context.parent.params.items())
        self.created_config = {translate_param_to_config(key): value for key, value in all_params}


def filter_out_same_as_defaults(click_config, default_values):
    return {key: value for key, value in click_config.items() if value != default_values.get(key)}


def get_applicable_options(options, application_context):
    return [
        option for option in options
        if option.option_id.is_applicable_for_application(application_context)
    ]


def get_applicable_commands(commands, application_context):
    return [
        command for command in commands
        if command.is_applicable_for_application(application_context)
    ]


def any_option_in_sys_argv(options):
    return bool([arg for arg in sys.argv if arg in options])


def prepare_config_options(config, name, config_options, ignore_hidden, disable_required):
    entity_config_options = {
        config_option
        for config_option in config_options if config_option.option_id.entity
    }

    entity_options = {}
    if entity_config_options != config_options:
        entity_options, _ = try_to_parse_config_options(
            config, name, entity_config_options, ignore_hidden)

    return _create_options_from_config(
        config,
        config_options,
        ignore_hidden,
        entity_options=entity_options,
        disable_required=disable_required)


def try_to_parse_config_options(config, name, config_options, ignore_hidden):
    options = prepare_config_options(
        config, name, config_options, ignore_hidden, disable_required=True)
    args = [arg for arg in sys.argv if arg != '--help']
    try:
        context = click.Command(
            name, params=options).make_context(
                '', args, allow_extra_args=True, ignore_unknown_options=True)
        return {translate_param_to_config(key): value
                for key, value in context.params.items()}, options
    except Exception:
        return {}, options


def _create_options_from_config(
        config, config_options, ignore_hidden=False, entity_options={}, disable_required=False):
    """
    Create Click command options from the list of config options.

    Uses the loaded config to set default values.

    :param config: the config
    :param config_options: the config options to add to click
    :param disable_required: Makes all options not required to not fail early parsing
    :param entity_options: existing entity option values from pre parsing the command
    :return: list of click.Option
    """
    options = []
    for config_option in config_options:
        entity_option_id = config_option.option_id.at

        if entity_option_id is not None:
            default_entity = ['[{name}]'.format(name=entity_option_id.name)]

            entities = config.get(
                entity_option_id, additional_options=entity_options, default=default_entity)
            if not entity_option_id.multiple:
                entities = [entities]
        else:
            entities = [None]

        for entity in entities:
            options.append(
                _option_from_option_id(
                    config_option,
                    config,
                    ignore_hidden,
                    entity_name=entity,
                    disable_required=disable_required))

    return sorted(options, key=lambda o: o.name)


def _option_from_option_id(
        config_option, config, ignore_hidden, entity_name=None, disable_required=False):
    option_id = config_option.option_id
    default_value = option_id.default
    if option_id.at is None or entity_name is not None:
        default_value = config.get(
            option_id, default=default_value, entity=entity_name, transform=False)

    real_isidentifier = click.core.isidentifier
    try:
        click.core.isidentifier = lambda x: re.compile(r'^[a-zA-Z_\[\]][\[\]@#a-zA-Z0-9_]*$').search(x) is not None

        full_name, option_strings = option_id.cli_options(entity_name)

        if option_id.argument:
            # Arguments can not have default values in click so we deal with this by setting required to True
            # only if there is no default value
            required = config_option.required and (default_value is None or default_value == ())

            return click.Argument(
                option_strings,
                required=required and not disable_required,
                envvar='ZAF_{name}'.format(name=re.sub(r'[.-]', '_', full_name).upper()),
                type=_convert_to_click_type(option_id.type, config),
                nargs=-1 if option_id.multiple else 1)
        else:
            return click.Option(
                tuple(option_strings),
                required=config_option.required and not option_id.has_default
                and not disable_required,
                envvar='ZAF_{name}'.format(name=re.sub(r'[.-]', '_', full_name).upper()),
                default=default_value,
                show_default=option_id.has_default,
                type=_convert_to_click_type(option_id.type, config),
                is_flag=type(option_id.type) == Flag,
                multiple=option_id.multiple,
                hidden=not ignore_hidden and option_id.hidden,
                count=isinstance(option_id.type, Count),
                help=option_id.description,
            )

    finally:
        click.core.isidentifier = real_isidentifier


def translate_param_to_config(param_name):
    return re.sub(r'[@_-]', '.', param_name)


def _convert_to_click_type(option_type, config):
    """
    Convert a ZAF option type to the Click representation.

    :param option_type: the ZAF option type
    :param config: the config manager
    :return: the Click representation
    """
    if option_type in [str, int, float, bool]:
        return option_type
    elif type(option_type) == Path:
        return click.Path(exists=option_type.exists)
    elif type(option_type) == Choice:
        return click.Choice(option_type.choices)
    elif type(option_type) == ConfigChoice:
        return click.Choice(option_type.choices(config))
    elif type(option_type) == GlobPattern:
        return str
    elif type(option_type) == Flag:
        # Flag has type None because otherwise click will not correctly
        # match it to a bool_flag which has special behavior and allows for
        # default value and --no-{flag} syntax.
        return None
    elif type(option_type) == Count:
        return click.IntRange(option_type.min, option_type.max, clamp=True)
    elif type(option_type) == Entity:
        return str
    else:
        raise ValueError('Invalid option type {type}'.format(type=option_type))
