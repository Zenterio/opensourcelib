import logging
import sys
import threading
import traceback

from zaf import __version__
from zaf.application import AFTER_COMMAND, APPLICATION_CHANGELOG_TYPE, APPLICATION_CONTEXT, \
    APPLICATION_ENDPOINT, APPLICATION_NAME, APPLICATION_ROOT, APPLICATION_VERSION, BEFORE_COMMAND, \
    CWD, ENTRYPOINT_NAME, MESSAGEBUS_TIMEOUT
from zaf.application.context import ApplicationContext
from zaf.application.metadata import ZafMetadata
from zaf.builtin.changelog import ChangeLogType
from zaf.component.decorator import component
from zaf.component.factory import Factory
from zaf.component.manager import ComponentManager
from zaf.config.manager import ConfigManager
from zaf.config.options import ConfigOption
from zaf.extensions import EXTENSION_ENABLED
from zaf.extensions.loader import ExtensionLoader
from zaf.extensions.manager import ExtensionManager
from zaf.messages.messagebus import MessageBus, MessageBusTimeout

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ApplicationConfiguration(object):

    def __init__(
            self,
            name,
            entrypoint=None,
            cli=True,
            version=None,
            root_package=None,
            application_context=ApplicationContext.STANDALONE,
            changelog_type=ChangeLogType.NONE):
        self.name = name
        self.entrypoint = entrypoint if entrypoint is not None else name
        self.cli = cli
        self.version = version if version else __version__
        self.root_package = root_package if root_package is not None else name
        self.application_context = application_context
        self.changelog_type = changelog_type

    def apply_configuration(self, config_manager):
        config_manager.set(APPLICATION_NAME, self.name, 1, 'Application')
        config_manager.set(APPLICATION_ROOT, self.root_package, 1, 'Application')
        config_manager.set(ENTRYPOINT_NAME, self.entrypoint, 1, 'Application')
        config_manager.set(APPLICATION_VERSION, self.version, 1, 'Application')
        config_manager.set(APPLICATION_CONTEXT, self.application_context.name, 1, 'Application')
        config_manager.set(APPLICATION_CHANGELOG_TYPE, self.changelog_type.name, 1, 'Application')

        if not self.cli:
            config_manager.set(EXTENSION_ENABLED, False, 102, 'Application', entity='click')


class Application(object):

    def __init__(
            self,
            application_config,
            entry_points=['zaf.addons', 'zaf.local_addons'],
            signalhandler=None):
        root_logger = logging.getLogger()
        # Default config for rootlogger to not spam until logger is correctly configured
        root_logger.setLevel(logging.INFO)

        self.app_config = application_config
        self.signalhandler = signalhandler
        self.entry_points = entry_points
        self.extension_manager = ExtensionManager()
        self.component_manager = ComponentManager()
        self.component_factory = Factory(self.component_manager)
        self.session_scope = self.component_factory.enter_scope('session')
        self.messagebus = MessageBus(self.component_factory, self.session_scope)
        self.messagebus.define_endpoints_and_messages(
            {
                APPLICATION_ENDPOINT: [BEFORE_COMMAND, AFTER_COMMAND]
            })
        self.config = ConfigManager()
        self.command = None
        self._exit_code = 1
        self.app_config.apply_configuration(self.config)

        @component(name='MessageBus', scope='session')
        def messagebus():
            """
            Access the message bus.

            The message bus can be used to register dispatchers to specific
            endpoints, message_ids and entities and to send requests and events
            to the registered dispatchers.
            """
            return self.messagebus

        @component(name='ComponentFactory', scope='session')
        def component_factory():
            """
            Access the component factory.

            The component factory can be used to call callables inside a scope
            and have the correct components instantiated in the scope.
            """
            return self.component_factory

        @component(name='ComponentManager', scope='session')
        def component_manager():
            """
            Access the component manager.

            The component manager can be used to find out what components are
            available.
            """
            return self.component_manager

        @component(name='Config', scope='session')
        def config():
            """
            Access the Config Manager.

            The Config components gives full access to all the config.
            """
            return self.config

        @component(name='ExtensionManager', scope='session')
        def extension_manager():
            """
            Access the extension manager.

            The extension manager can be used to find out what extensions are
            loaded.
            """
            return self.extension_manager

    def run(self):
        with self as instance:
            instance._exit_code = instance.execute_command()
        return instance._exit_code

    def setup(self):
        application_config_options = [
            ConfigOption(MESSAGEBUS_TIMEOUT, required=False),
            ConfigOption(CWD, required=True),
        ]
        loader = ExtensionLoader(
            self.extension_manager, self.config, self.messagebus, application_config_options,
            self.component_manager)
        self.command = loader.load_extensions(self.entry_points)

    def teardown(self):
        try:
            self.messagebus.wait_for_not_active(timeout=self.config.get(MESSAGEBUS_TIMEOUT))
        except MessageBusTimeout as e:
            logger.critical(
                'Waiting for messagebus to be inactive timed out,'
                ' shutting down anyway. State: {state}'.format(state=e))
        finally:
            logger.debug(
                'Dispatchers still registered to the messagebus: {dispatchers}'.format(
                    dispatchers=self.messagebus.get_dispatchers()))
            self.extension_manager.destroy()
            for th in threading.enumerate():
                try:
                    if th.name != 'MainThread':
                        logger.debug(th)
                        logger.debug(
                            '\n'.join(traceback.format_stack(sys._current_frames()[th.ident])))
                except KeyError:
                    logger.debug(th)

    def execute_command(self):
        logger.debug(
            'Executing command {command} for application {application} with version {version}'.
            format(
                command=self.command.name,
                application=self.app_config.name,
                version=self.app_config.version))
        self._activate_signalhandler()
        self.messagebus.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT, data=self.command.name)
        result = 0
        try:
            result = self.component_factory.call(self.command.callable, self.session_scope, self)
            return result if result is not None else 0
        finally:
            logger.debug(
                'Command {command} exited with exit code {result}'.format(
                    command=self.command.name, result=result).format(
                        command=self.command.name,
                        application=self.app_config.name,
                        version=self.app_config.version))

            self.component_factory.exit_scope(self.session_scope)
            self.messagebus.trigger_event(
                AFTER_COMMAND, APPLICATION_ENDPOINT, data=self.command.name)

    def gather_metadata(self, metadata_filter=None):
        return ZafMetadata(
            self.extension_manager.all_extensions, self.component_manager.get_components_info(),
            self.config, self.app_config.entrypoint, self.extension_manager, metadata_filter)

    def __enter__(self):
        try:
            self.setup()
        except Exception:
            self.__exit__(*sys.exc_info())
            raise
        return self

    def __exit__(self, *args):
        self.teardown()

    @property
    def exit_code(self):
        return self._exit_code

    def _activate_signalhandler(self):
        if self.signalhandler is not None:
            self.signalhandler.activate(self.messagebus)

    def _deactivate_signalhandler(self):
        if self.signalhandler is not None:
            self.signalhandler.deactivate()
