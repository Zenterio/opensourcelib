"""Configures logging with reasonable defaults for K2 tests in an STB environment."""

import logging
import os
from collections import defaultdict

from zaf.builtin.logging import EXTENSION_LOG_LEVEL, LOG_DIR, LOG_FILE_DEBUG, LOG_FILE_FORMAT, \
    LOG_FILE_INFO, LOG_FILE_LEVEL, LOG_FILE_LOGGERS, LOG_FILE_PATH, LOG_FILE_ROTATE_SCOPE, \
    LOG_FILE_TYPE, LOG_FILE_WARNING, LOG_FILES, LOG_LEVEL
from zaf.commands import COMMAND
from zaf.config.options import ConfigOption
from zaf.extensions import ENABLED_EXTENSIONS
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension, \
    get_logger_name

from . import LOGDEFAULTS_ENABLED

logger = logging.getLogger(get_logger_name('k2', 'logdefaults'))
logger.addHandler(logging.NullHandler())


@FrameworkExtension(
    name='logdefaults',
    load_order=99,
    config_options=[
        ConfigOption(ENABLED_EXTENSIONS, required=True),
        ConfigOption(LOG_DIR, required=True),
        ConfigOption(LOGDEFAULTS_ENABLED, required=True)
    ],
    groups=['logging'])
class LogDefaults(AbstractExtension):
    """Implements the defaults."""

    def __init__(self, config, instances):
        self.priority = 10

    def get_config(self, config, requested_config_options, requested_command_config_options):
        extension_configs = defaultdict(list)
        if config.get(COMMAND) == 'run' and config.get(LOGDEFAULTS_ENABLED) is True:

            for extension in config.get(ENABLED_EXTENSIONS):
                level = 'warning'
                if extension in ['testrunner']:
                    level = 'info'

                file_path = os.path.join('extensions', '{ext}.log'.format(ext=extension))
                self._log_file_config(config, extension, file_path, extension_configs)
                ext_level_config_name = '.'.join(['ext', extension, EXTENSION_LOG_LEVEL.name])
                extension_configs[ext_level_config_name] = level

            self._log_file_config(config, 'all', 'all.log', extension_configs, '')
            self._log_file_config(
                config, 'alljsonl', 'all.jsonl', extension_configs, '', filetype='json')
            self._log_file_config(
                config, 'allinfo', 'all_info.log', extension_configs, '', level='info')
            self._log_file_config(
                config, 'messages', 'messages.log', extension_configs, 'zaf.messages')
            self._log_file_config(
                config,
                'config',
                'config.log',
                extension_configs,
                'zaf.config.manager',
                format='%(message)s')
            self._log_file_config(
                config, 'extensions', 'extensions.log', extension_configs, 'zaf.extensions')
            self._log_file_config(
                config, 'components', 'components.log', extension_configs, 'zaf.component')

            self._log_file_config(
                config,
                'testcase.log',
                'testcase.log',
                extension_configs,
                'testcase',
                additional_logger_levels={
                    'info': ['k2.extension.testrunner']
                })

            extension_configs[LOG_LEVEL.name] = 'warning'

            self._setup_testrun_directory(extension_configs, 'debug')

        return ExtensionConfig(extension_configs, priority=self.priority)

    def _get_config_name(self, extension, configoption):
        return '.'.join([LOG_FILES.namespace, extension, configoption.name])

    def _log_file_config(
            self,
            config,
            file_id,
            file_path,
            extension_configs,
            logger_name=None,
            level='debug',
            format=None,
            additional_logger_levels={},
            filetype='text'):

        if logger_name is None:
            logger_name = get_logger_name('k2', file_id)
        log_file_config_name = '.'.join([LOG_FILES.namespace, LOG_FILES.name])
        log_file_path_config_name = self._get_config_name(file_id, LOG_FILE_PATH)
        log_file_loggers_config_name = self._get_config_name(file_id, LOG_FILE_LOGGERS)
        log_file_level_config_name = self._get_config_name(file_id, LOG_FILE_LEVEL)
        log_file_format_config_name = self._get_config_name(file_id, LOG_FILE_FORMAT)
        log_file_debug_config_name = self._get_config_name(file_id, LOG_FILE_DEBUG)
        log_file_info_config_name = self._get_config_name(file_id, LOG_FILE_INFO)
        log_file_warning_config_name = self._get_config_name(file_id, LOG_FILE_WARNING)
        log_file_type_config_name = self._get_config_name(file_id, LOG_FILE_TYPE)

        extension_configs[log_file_config_name].append(file_id)
        extension_configs[log_file_path_config_name] = os.path.join(config.get(LOG_DIR), file_path)
        extension_configs[log_file_loggers_config_name].append(logger_name)
        extension_configs[log_file_level_config_name] = level

        extension_configs[log_file_debug_config_name].extend(
            additional_logger_levels.get('debug', []))
        extension_configs[log_file_info_config_name].extend(
            additional_logger_levels.get('info', []))
        extension_configs[log_file_warning_config_name].extend(
            additional_logger_levels.get('warning', []))

        extension_configs[log_file_type_config_name] = filetype

        if format is not None:
            extension_configs[log_file_format_config_name] = format

    def _setup_testrun_directory(self, extension_configs, default_level):
        log_file_name = 'testrun'
        log_file_config_name = '.'.join([LOG_FILES.namespace, LOG_FILES.name])
        log_file_path_config_name = self._get_config_name(log_file_name, LOG_FILE_PATH)
        log_file_rotate_scope = self._get_config_name(log_file_name, LOG_FILE_ROTATE_SCOPE)
        log_file_loggers_config_name = self._get_config_name(log_file_name, LOG_FILE_LOGGERS)
        log_file_level_config_name = self._get_config_name(log_file_name, LOG_FILE_LEVEL)

        extension_configs[log_file_config_name].append(log_file_name)
        extension_configs[log_file_path_config_name] = '${log.dir}/testrun/{scope}.log'
        extension_configs[log_file_rotate_scope] = 'testcase'

        extension_configs[log_file_loggers_config_name] = ['']
        extension_configs[log_file_level_config_name] = default_level
