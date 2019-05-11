from collections import defaultdict


class DuplicateOptionException(Exception):
    pass


def check_for_ambiguous_duplicates(prog_name, framework_config_options, command_config_options):
    """
    Check all options for ambiguous duplicates on command line.

    The cli options for all framework and command config options are calculated and ambiguous
    duplicates causes a raised exception that will be reported to the user.
    The cli options for a flag with both short_name and short_alias will  be for example
    ['-f', '--flag', '--no-flag', '--namespace-flag', '--no-namespace-flag'].

    It's not allowed to share the same cli option between different framework options.
    It's not allowed to share the same cli option between framework options and command options.
    It's not allowed to share the same cli option between command options on the same command.

    :param prog_name: The name of the program, only used for reporting errors
    :param framework_config_options: List of all known framework config options
    :param command_config_options: Dict from command to list of command config options
    :raises: DuplicateOptionException if an ambiguous cli option is encountered
    """

    used_framework_option_names = defaultdict(set)

    _check_for_duplicate_framework_option_names(
        prog_name, framework_config_options, used_framework_option_names)

    for command, command_options in command_config_options.items():
        _check_commands_for_duplicate_option_names(
            prog_name, command, command_options, used_framework_option_names)


def _check_for_duplicate_framework_option_names(
        prog_name, framework_config_options, used_framework_option_names):
    for option_id in {option.option_id for option in framework_config_options}:
        for cli_option in _list_cli_options(option_id):
            used_framework_option_names[cli_option].add(option_id)

            if len(used_framework_option_names[cli_option]) > 1:
                option1, option2 = tuple(
                    sorted(used_framework_option_names[cli_option], key=lambda o: o.key))
                msg = (
                    "Duplicate command line option '{cli_option}' on top level '{prog_name}' command, "
                    "for options '{option1}' and '{option2}'").format(
                        cli_option=cli_option,
                        prog_name=prog_name,
                        option1=option1.key,
                        option2=option2.key,
                    )

                raise DuplicateOptionException(msg)


def _check_commands_for_duplicate_option_names(
        prog_name, command, command_options, used_framework_option_names):
    used_command_option_names = defaultdict(set)

    for option_id in {option.option_id for option in command_options}:
        for cli_option in _list_cli_options(option_id):
            used_command_option_names[cli_option].add(option_id)

            _check_for_duplicate_command_and_framework_option(
                prog_name, command.name, used_framework_option_names, cli_option, option_id.key)

            _check_for_duplicate_command_option_names(
                used_command_option_names, cli_option, command.name)


def _check_for_duplicate_command_and_framework_option(
        prog_name, command_name, used_framework_option_names, cli_option, option_key):
    if used_framework_option_names[cli_option]:
        msg = (
            "Duplicate command line option '{cli_option}' between command '{command}' "
            "and top level '{prog_name}' command, "
            "for options '{option1}' and '{option2}'").format(
                cli_option=cli_option,
                command=command_name,
                prog_name=prog_name,
                option1=list(used_framework_option_names[cli_option])[0].key,
                option2=option_key)

        raise DuplicateOptionException(msg)


def _check_for_duplicate_command_option_names(used_command_option_names, cli_option, command_name):
    if len(used_command_option_names[cli_option]) > 1:
        option1, option2 = tuple(sorted(used_command_option_names[cli_option], key=lambda o: o.key))
        msg = (
            "Duplicate command line option '{cli_option}' on command '{command}', "
            "for options '{option1}' and '{option2}'").format(
                cli_option=cli_option,
                command=command_name,
                option1=option1.key,
                option2=option2.key,
            )

        raise DuplicateOptionException(msg)


def _list_cli_options(option_id):
    """List all cli options for a ConfigOptionId."""
    _, cli_options = option_id.cli_options('entity' if option_id.at else None)
    for cli_option in cli_options:
        for actual_cli_option in cli_option.split('/'):
            yield actual_cli_option
