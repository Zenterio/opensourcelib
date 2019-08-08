import logging
import os

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.cmd.run import RUN_COMMAND
from zk2component import LOG_DIR_TESTS

logger = logging.getLogger(get_logger_name('k2', 'zk2component'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    'zk2component',
    extends=[RUN_COMMAND],
    config_options=[ConfigOption(LOG_DIR_TESTS, required=True)])
class Zk2Component(AbstractExtension):

    def __init__(self, config, instances):

        @component
        @requires(zk2='PyProc', args=['zk2'])
        @requires(context='TestContext')
        class Zk2(object):

            logdir_tests = config.get(LOG_DIR_TESTS)

            def __init__(self, zk2, config, context):
                self.zk2 = zk2
                self.config = config
                self.context = context

            def __call__(
                    self,
                    enabled_extensions,
                    command,
                    expected_exit_code=0,
                    wait=True,
                    file_logging=True,
                    timeout=20,
                    plugin_path=None):

                additional_extensions = [
                    'click',
                    'configurationvalidator',
                    'signalhandler',
                    'logger',
                    'output',
                ]
                if file_logging:
                    additional_extensions.extend(['filelogger', 'logdefaults'])

                extension_args = [
                    '--ext-{extension}@enabled true'.format(extension=extension)
                    for extension in enabled_extensions + additional_extensions
                ]

                file_logging_args = []
                if file_logging:
                    file_logging_args = [
                        '--log-file-ids',
                        'all',
                        '--log-file-all@path',
                        "'${log.dir}/all.log'",
                        '--log-file-all@log-level',
                        'debug',
                        '--log-file-all@loggers',
                        "''",
                    ]

                zk2_args = (
                    '--disable-default-config-files '
                    '--ext-output@enabled true '
                    '--ext-default-enabled false '
                    '{plugin_path}'
                    '{enabled_extensions} '
                    '--log-dir {logdir} '
                    '{filelog} '
                    '{command}').format(
                        plugin_path='--plugins-paths ' + plugin_path + ' '
                        if plugin_path is not None else '',
                        enabled_extensions=' '.join(extension_args),
                        command=command,
                        filelog='' if not file_logging else ' '.join(file_logging_args),
                        logdir=os.path.join(self.logdir_tests, self.context.filename_with_params))

                return self.zk2(
                    zk2_args, expected_exit_code=expected_exit_code, wait=wait, timeout=timeout)
