from zaf.commands import COMMAND, COMMANDS
from zaf.config.options import ConfigOption, handle_duplicate_config_options
from zaf.extensions import ALL_EXTENSIONS, DISABLEABLE_EXTENSIONS, ENABLED_EXTENSIONS, \
    EXTENSION_ENABLED, EXTENSIONS_DEFAULT_ENABLED, PLUGINS_PATHS
from zaf.extensions.extension import ExtensionConfig


class ExtensionLoader(object):
    """
    Load extensions.

    Deals with reading the config and initializing the messagebus from the extensions.
    """

    # Load Order ranges
    ALWAYS_ENABLED_START = 1
    ALWAYS_ENABLED_END = 20
    PLUGIN_PATH_START = 1
    PLUGIN_PATH_END = 10
    DISABLE_START = 11
    DISABLE_END = 20
    REST_START = 21
    REST_END = 1000

    def __init__(
            self, extension_manager, config, messagebus, core_config_options, component_manager):
        self.extension_manager = extension_manager
        self.config = config
        self.messagebus = messagebus
        self.core_config_options = core_config_options
        self.component_manager = component_manager

    def load_extensions(self, entry_points=['zaf.addons']):
        """
        Load extensions in to the extension_manager.

        Populates the config and messagebus with information from the extensions.

        :return: the parsed command
        """
        main_config_options = self._initial_config_options()
        commands_with_config_options = {}

        self._find_addons(entry_points)
        self._enable_always_enabled_extensions()
        self._add_extensions_config_options(
            main_config_options, commands_with_config_options, self.ALWAYS_ENABLED_START,
            self.ALWAYS_ENABLED_END)
        self._initialize_framework_extensions(
            main_config_options, commands_with_config_options, self.PLUGIN_PATH_START,
            self.PLUGIN_PATH_END)

        self._find_plugins()
        self._add_extension_enabled_config_options(main_config_options)
        self._initialize_framework_extensions(
            main_config_options, commands_with_config_options, self.DISABLE_START, self.DISABLE_END)
        self._enable_rest_of_extensions()

        self._add_extensions_config_options(
            main_config_options, commands_with_config_options, self.REST_START)

        self._initialize_framework_extensions(
            main_config_options, commands_with_config_options, self.REST_START)

        self.config.log_config()

        command = self._select_command(commands_with_config_options.keys())

        if command is not None:
            self.messagebus.define_endpoints_and_messages(
                self.extension_manager.get_endpoints_and_messages(command))
            self.extension_manager.initialize_command_extensions(self.config, command)
            self.extension_manager.register_components(self.component_manager)
            self.extension_manager.register_dispatchers(self.messagebus)
            self.component_manager.log_components_info()
        else:
            raise Exception('Error: No extension selected the command')

        return command

    def _initial_config_options(self):
        """
        Define the initial config options.

        :return: list of config options
        """
        initial = [
            ConfigOption(PLUGINS_PATHS, required=False),
            ConfigOption(EXTENSIONS_DEFAULT_ENABLED, required=False)
        ]
        initial.extend(self.core_config_options)

        self.config.set_default_values([option.option_id for option in initial])
        return initial

    def _find_addons(self, entry_points):
        """Populate the extension manager with all addons."""
        for entry_point in entry_points:
            self.extension_manager.find_addons(entry_point)

    def _enable_always_enabled_extensions(self):
        """Enable addons with low load order (<21) that should always be enabled."""
        extensions = self.extension_manager.framework_extensions(
            load_order_start=self.ALWAYS_ENABLED_START,
            load_order_end=self.ALWAYS_ENABLED_END,
            only_enabled=False)

        for extension in extensions:
            self.config.set(EXTENSION_ENABLED, True, 101, 'core', entity=extension.name)
            self.extension_manager.enable_extension(extension)

    def _add_extensions_config_options(
            self,
            main_config_options,
            commands_with_config_options,
            load_order_start,
            load_order_end=1000):
        """
        Add config options and command config options for all extensions.

        Only extensions with load order between load_order_start and load_order_end are added.

        :param main_config_options: config options on the main command
        :param commands_with_config_options: config options for each subcommand
        :param load_order_start: the start load order
        :param load_order_end: the end load order
        """
        for extension in self.extension_manager.framework_extensions(load_order_start,
                                                                     load_order_end):
            extension_main_config_options = extension.config_options
            extension_main_config_options.extend(
                [
                    ConfigOption(option.option_id.include, required=False)
                    for option in extension_main_config_options if option.option_id.entity
                ])

            main_config_options.extend(extension_main_config_options)
            self.config.set_default_values(
                [option.option_id for option in extension_main_config_options])

            for command in extension.commands:
                command_config_options = list(command.config_options)
                command_config_options.extend(
                    [
                        ConfigOption(option.option_id.include, required=False)
                        for option in command_config_options if option.option_id.entity
                    ])

                commands_with_config_options[command] = command_config_options
                self.config.set_default_values(
                    [option.option_id for option in command_config_options])

        main_config_options[:] = handle_duplicate_config_options(main_config_options)
        for command in commands_with_config_options.keys():
            for command_extension in self.extension_manager.command_extensions(command):
                command_extension_config_options = command_extension.config_options
                command_extension_config_options.extend(
                    [
                        ConfigOption(option.option_id.include, required=False)
                        for option in command_extension_config_options if option.option_id.entity
                    ])
                commands_with_config_options[command].extend(command_extension_config_options)
                self.config.set_default_values(
                    [option.option_id for option in command_extension_config_options])

            commands_with_config_options[command][:] = handle_duplicate_config_options(
                commands_with_config_options[command])
        self.config.set(
            COMMANDS, sorted(command.name for command in commands_with_config_options.keys()))

    def _initialize_framework_extensions(
            self,
            main_config_options,
            commands_with_config_options,
            load_order_start=1,
            load_order_end=1000):
        """
        Initialize framework extensions.

        Calls get_config on each extension to populate the config manager with
        new config for all extensions with load order between load_order_start and load_order_end.

        :param main_config_options: the specified config options on the main command
        :param commands_with_config_options: the specified config option for each subcommand
        :param load_order_start: the start load order
        :param load_order_end: the end load order
        :return:
        """
        for extension in self.extension_manager.framework_extensions(
                load_order_start=load_order_start, load_order_end=load_order_end):

            extension_instances = self.extension_manager.initialize_framework_extension(
                extension, self.config)
            if hasattr(extension, 'get_config'):
                for extension_instance in extension_instances:
                    extension_config = extension_instance.get_config(
                        self.config, main_config_options, commands_with_config_options)

                    if isinstance(extension_config, ExtensionConfig):
                        extension_config = [extension_config]

                    for config in extension_config:
                        source = config.source if config.source else extension.name
                        self.config.update_config(config.config, config.priority, source)

    def _find_plugins(self):
        """
        Find and populates the extension manager with plugins.

        Sets the extension.all and extensions.disableable config values so that they can be used
        as entities for other config options.
        """
        for path in self.config.get(PLUGINS_PATHS):
            self.extension_manager.find_plugins(path)

        extension_names = {extension.name for extension in self.extension_manager.all_extensions}
        self.config.set(ALL_EXTENSIONS, extension_names, 101, 'core')

        disableable_extension_names = {
            extension.name
            for extension in self.extension_manager.all_extensions
            if extension not in self.extension_manager.enabled_extensions
        }

        self.config.set(DISABLEABLE_EXTENSIONS, disableable_extension_names, 101, 'core')

    def _add_extension_enabled_config_options(self, config_options):
        """
        Add config options to enable/disable disableable extensions.

        The default value is read from the extensions.default.enabled config value.

        :param config_options: the list of config options to add the created config options to
        """
        default_enabled = self.config.get(EXTENSIONS_DEFAULT_ENABLED)
        for extension in self.extension_manager.all_extensions:
            extension_enabled = default_enabled and extension.default_enabled
            self.config.set(EXTENSION_ENABLED, extension_enabled, 1, 'core', entity=extension.name)

        config_options.append(ConfigOption(EXTENSION_ENABLED, required=False))

    def _enable_rest_of_extensions(self):
        """Enable the rest of the extensions using if specified in the config."""
        replaced_extensions = set()
        enabled_extensions = []
        for extension in self.extension_manager.all_extensions:
            if (extension not in self.extension_manager.enabled_extensions
                    and self.config.get(EXTENSION_ENABLED, entity=extension.name)):
                replaced_extensions.update(extension.replaces)
                enabled_extensions.append(extension)
        for extension in enabled_extensions:
            if extension.name not in replaced_extensions:
                self.extension_manager.enable_extension(extension)
        self.config.set(
            ENABLED_EXTENSIONS, [ext.name for ext in self.extension_manager.enabled_extensions])

    def _select_command(self, commands):
        """
        Return the command_id from the command selected by one of the extensions.

        :param commands: iterable of all command_ids
        """
        command_name = self.config.get(COMMAND)
        for command in commands:
            if command.name == command_name:
                return command
