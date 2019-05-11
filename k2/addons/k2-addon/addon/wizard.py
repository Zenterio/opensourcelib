"""Provides wizards for asking the user questions about their addon."""

import distutils.version
import email.utils
import os
import re
from textwrap import dedent

import k2


def _string_length_validator(min_length, max_length):
    """
    Validate that a string meets some length constraints.

    :return: a validator enforcing the constraints provided to this function.
    """

    def _validator(ns, value):
        string_length = len(value)
        if not string_length >= min_length or not string_length <= max_length:
            raise ValueError(
                'Must be between {min_length} and {max_length} characters'.format(
                    min_length=min_length, max_length=max_length))
        return value

    return _validator


def _setuptools_version_validator(ns, value):
    """
    Validate that a value is a valid setuptools version number.

    :return: the version number on success, raises ValueError on failure.
    """
    try:
        distutils.version.StrictVersion(value)
        return value
    except Exception as e:
        raise ValueError('Not a valid version: {version}'.format(version=value)) from e


def _email_validator(ns, value):
    """
    Validate that a string looks like a valid e-mail address.

    :return: the string on success, raises ValueError on failure.
    """
    if '@' not in value or email.utils.parseaddr(value) == ('', ''):
        raise ValueError(
            'Does not seem like a valid e-mail address: {address}'.format(address=value))
    return value


def _camel_case_validator(ns, value):
    """
    Validate that a string is written using camel case.

    :return: the string on success, raises value error on failure.
    """
    if not re.match(r'(?:[A-Z][a-z]+)+', value):
        raise ValueError('Does not seem like CamelCase: {value}'.format(value=value))
    return value


def _escape_single_quote_validator(ns, value):
    r"""
    Replace any occurances of ' in a string with \'.

    :return: the escaped string.
    """
    return value.replace("'", r"\\'")


def run_generic_addon_wizard():
    """Ask the user general questions needed to create any addon types."""
    import editor
    from pypsi import wizard
    from pypsi.completers import choice_completer

    package_name_step = wizard.WizardStep(
        'package_name',
        'package_name',
        validators=[
            wizard.required_validator,
            _string_length_validator(1, 200), wizard.lowercase_validator
        ],
        help='The name that this addon should be packaged as.')

    version_step = wizard.WizardStep(
        'version',
        'version',
        default='0.0.1',
        validators=[wizard.required_validator, _setuptools_version_validator],
        help=dedent(
            """
            The version of the addon.

            Often a simple scheme like a dot separated list of major version,
            minor version and patch number will suffice.

            For inspiration and suggestions about what options are available,
            please see PEP404: https://www.python.org/dev/peps/pep-0440/

            The version number shall be compatible with Python's setuptools.
            """))

    description_step = wizard.WizardStep(
        'description',
        'description',
        validators=[
            wizard.required_validator,
            _string_length_validator(1, 200), _escape_single_quote_validator
        ],
        help='A one-line summary of the addon.')

    long_description_step = wizard.WizardStep(
        'long_description',
        'long_description (press tab to launch editor)',
        validators=[wizard.required_validator, _escape_single_quote_validator],
        completer=lambda shell, path, prefix: [editor.edit().decode('UTF-8')],
        help='A more detailed description of the addon.')

    maintainer_step = wizard.WizardStep(
        'maintainer',
        'maintainer',
        validators=[wizard.required_validator,
                    _string_length_validator(1, 200)],
        help='Name of the person or group maintaining this addon.')

    maintainer_email_step = wizard.WizardStep(
        'maintainer_email',
        'maintainer_email',
        validators=[wizard.required_validator, _email_validator,
                    _string_length_validator(1, 200)],
        help='E-mail that can be used to reach the maintainer.')

    install_requires_step = wizard.WizardStep(
        'install_requires',
        'install_requires (may be empty)',
        help=dedent(
            """
            A comma-separated list of packages that this addon requires.

            Version requirements may be specified using Python logic operations.
            For instance the requirement of a specific version of a package may
            be expressed using the 'package==X.Y.Z' syntax.

            Specifying strict version dependencies should be avoided where
            possible, to avoid the difficult to resolve situation where multiple
            addons depend on different specific versions of the same package.

            If your addon requires a feature that was introduced in a specific
            version, a better solution would be to specify that the addon
            requires a version of the package that is greater than X.Y.Z, using
            the 'package>=X.Y.Z' syntax.

            When in doubt, it is best to leave the version information out.
            """))

    entrypoint_step = wizard.WizardStep(
        'entrypoint',
        'entrypoint (class name, use camelcase)',
        validators=[
            wizard.required_validator,
            _string_length_validator(1, 200), _camel_case_validator
        ],
        help=dedent(
            """
        Name the entrypoint for this addon.

        The entrypoint will be a class and should have a CamelCased name.

        For more information on naming conventions in K2, please see PEP-8:
        https://www.python.org/dev/peps/pep-0008/
        """))

    addon_path_step = wizard.WizardStep(
        'addon_path',
        'path to K2\'s addons root directory',
        validators=[wizard.directory_validator],
        completer=_path_completer,
        default=os.path.abspath(os.path.join(k2.__path__[0], '..', 'addons')),
        help='Path to the K2 addons directory where this addon should be created.')

    addon_type_step = wizard.WizardStep(
        'addon_type',
        'addon_type',
        validators=[wizard.required_validator,
                    wizard.choice_validator(['framework', 'command'])],
        completer=choice_completer(['framework', 'command'], case_sensitive=True),
        help=dedent(
            """
            Select what type of addon you wish to create.

            There are two choices: framework or command.

            Framework extensions have the ability to extend the functionality of
            the K2 framework. They have the ability to add commands or to
            provide new general functionality to the K2 core framework.

            Command extensions have the ability to extend specific commands.
            """))

    return _run_pypsi_wizard(
        wizard.PromptWizard(
            'Addon Creation',
            dedent(
                """
            This wizard will guide you through the creation of a K2 addon.

            Please answer the following questions about your K2 addon:
            """),
            steps=[
                addon_type_step,
                package_name_step,
                version_step,
                description_step,
                long_description_step,
                maintainer_step,
                maintainer_email_step,
                install_requires_step,
                entrypoint_step,
                addon_path_step,
            ]))


def run_command_extension_wizard(core):
    """Asks the user questions needed specifially when creating a command extension."""

    from pypsi import wizard
    from pypsi.completers import choice_completer

    available_commands = {
        command.name: command
        for command in core.extension_manager.get_commands()
    }

    command_step = wizard.WizardStep(
        'command',
        'command to extend',
        validators=[wizard.required_validator, lambda _, command: available_commands[command]],
        completer=choice_completer(available_commands.keys()),
        help='Name the command you would like to extend.')

    return _run_pypsi_wizard(
        wizard.PromptWizard(
            'Command Extension Creation',
            dedent(
                """
            This wizard will guide you through the creation of a K2 addon.

            Please answer the following questions about your K2 command extension:
            """),
            steps=[
                command_step,
            ]))


# Some pypsi workarounds:


def _run_pypsi_wizard(wizard):
    from pypsi import shell

    sh = shell.Shell()
    try:
        sh.set_readline_completer()
        return wizard.run(sh)
    finally:
        sh.reset_readline_completer()


def _path_completer(shell, path, prefix):
    from pypsi.completers import path_completer

    return path_completer(path[0])
