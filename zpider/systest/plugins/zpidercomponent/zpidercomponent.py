import getpass
import importlib
import inspect
import logging
import os

from k2.cmd.run import RUN_COMMAND
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Path
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'zpidercomponent'))
logger.addHandler(logging.NullHandler())

ZPIDER_LOGS_DIR = ConfigOptionId(
    'zpider.log.dir',
    'Directory to put the zpider log files in.',
    default='${output.dir}/logs/zpider',
    option_type=Path(exists=False))


@component(name='Data')
class Data(object):

    def __init__(self):
        self._systest_dir = os.path.dirname(inspect.getfile(importlib.import_module('systest')))
        self._data_dir = os.path.join(self._systest_dir, 'data')

    def file(self, rel_path):
        return os.path.join(self._data_dir, rel_path)


@CommandExtension(
    'zpidercomponent',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(ZPIDER_LOGS_DIR, required=True),
    ])
class ZpiderExtension(AbstractExtension):

    def __init__(self, config, instances):

        @component()
        @requires(zpider='PyProc', args=['zpider'])
        @requires(context='ComponentContext')
        class Zpider(object):

            zpider_logs_dir = os.path.abspath(config.get(ZPIDER_LOGS_DIR))
            root = getpass.getuser() == 'jenkins'

            def __init__(self, zpider, context):
                self.zpider = zpider
                self._test_name = context.callable_qualname

            def __call__(self, command, expected_exit_code=0, cwd=None, env=None, wait=True):

                file_logging_options = (
                    "--log-file-ids all --log-dir {log_dir} --log-file-all@path '${{log.dir}}/all.log' "
                    '--log-file-all@loggers zaf --log-file-all@log-level debug '
                ).format(log_dir=os.path.join(self.zpider_logs_dir, self._test_name))

                return self.zpider(
                    ('{root} {file_logging_options} {command}').format(
                        root='--root' if self.root else '',
                        file_logging_options=file_logging_options,
                        command=command),
                    expected_exit_code=expected_exit_code,
                    cwd=os.getcwd() if cwd is None else cwd,
                    wait=wait,
                    env=env)
