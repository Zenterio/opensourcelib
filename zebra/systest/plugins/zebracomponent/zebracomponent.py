import logging
import os

from k2.cmd.run import RUN_COMMAND
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Path
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'zebracomponent'))
logger.addHandler(logging.NullHandler())

ZEBRA_LOGS_DIR = ConfigOptionId(
    'zebra.log.dir',
    'Directory to put the zebra log files in.',
    default='${output.dir}/logs/zebra',
    option_type=Path(exists=False))


@CommandExtension(
    'zebracomponent',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(ZEBRA_LOGS_DIR, required=True),
    ])
class ZebraExtension(AbstractExtension):

    def __init__(self, config, instances):

        @component()
        @requires(zebra='PyProc', args=['zebra'])
        @requires(context='ComponentContext')
        class Zebra(object):

            zebra_logs_dir = os.path.abspath(config.get(ZEBRA_LOGS_DIR))

            def __init__(self, zebra, context):
                self.zebra = zebra
                self._test_name = context.callable_qualname

            def __call__(
                    self,
                    command,
                    expected_exit_code=0,
                    override_run='/bin/echo',
                    override_pull='/bin/echo',
                    override_tag='/bin/echo',
                    cwd=None,
                    env=None,
                    wait=True):

                override_run_var = ''
                if override_run is not None:
                    override_run_var = 'OVERRIDE_RUN={override_run}'.format(
                        override_run=override_run)

                override_pull_var = ''
                if override_pull is not None:
                    override_pull_var = 'OVERRIDE_PULL={override_pull}'.format(
                        override_pull=override_pull)

                override_tag_var = ''
                if override_tag is not None:
                    override_tag_var = 'OVERRIDE_TAG={override_tag}'.format(
                        override_tag=override_tag)

                file_logging_options = (
                    "--log-file-ids all --log-dir {log_dir} --log-file-all@path '${{log.dir}}/all.log' "
                    "--log-file-all@loggers '' --log-file-all@log-level debug "
                ).format(log_dir=os.path.join(self.zebra_logs_dir, self._test_name))

                command_prefix = (
                    '{override_run_var} '
                    '{override_pull_var} '
                    '{override_tag_var} ').format(
                        override_run_var=override_run_var,
                        override_pull_var=override_pull_var,
                        override_tag_var=override_tag_var)

                return self.zebra(
                    '{file_logging_options} {command}'.format(
                        file_logging_options=file_logging_options, command=command),
                    expected_exit_code=expected_exit_code,
                    cwd=os.getcwd() if cwd is None else cwd,
                    wait=wait,
                    env=env,
                    command_prefix=command_prefix)
