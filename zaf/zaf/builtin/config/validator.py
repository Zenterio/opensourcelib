"""
Validates the configuration.

zaf supports multiple different configuration option types. Some of these
types provide self-check functionality where the value of the option can be
sanity checked. This extension inspects the configuration gathered so-far
and applies these self-checks.

Due to the nature of extensions, only configuration loaded up until the
point where this extension is loaded can be inspected. As such, it is
recommended that this extension is loaded late, preferably last.
"""
from zaf.commands import COMMAND
from zaf.config.typechecker import ConfigOptionIdTypeChecker
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension


@FrameworkExtension(name='configurationvalidator', load_order=101)
class ConfigurationValidator(AbstractExtension):
    """Implementation of the validation."""

    def get_config(self, config, requested_config_options, requested_command_config_options):

        def get_option_ids_sorted_by_dependencies(options):
            """
            Get the option ids from the options and sort to give ids that others depend on first.

            The ordering is done so that entity options are validated first so that they
            can be used later on to retrieve the values for the "at"-options without
            triggering strange errors.
            """

            def order(option_id):
                if option_id.entity:
                    return -1
                else:
                    return 1

            return sorted((option.option_id for option in options), key=order)

        def find_command_options(command_name):
            for command, options in requested_command_config_options.items():
                if command.name == command_name:
                    return options

            return []

        checker = ConfigOptionIdTypeChecker(config)

        all_options = requested_config_options + find_command_options(config.get(COMMAND))
        for option_id in get_option_ids_sorted_by_dependencies(all_options):
            if option_id.at is not None:
                if option_id.at.multiple:
                    for entity in config.get(option_id.at):
                        value = config.get(option_id, entity=entity, transform=False)
                        checker.assert_type(option_id, value, entity)
                else:
                    entity = config.get(option_id.at)
                    value = config.get(option_id, entity=entity, transform=False)
                    checker.assert_type(option_id, value, entity)
            else:
                value = config.get(option_id, transform=False)
                checker.assert_type(option_id, value)

        return ExtensionConfig({}, priority=0)
