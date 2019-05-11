import logging

from k2.cmd.run import RUN_COMMAND
from zaf.component.decorator import component, requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

logger = logging.getLogger(get_logger_name('zchangelog', 'zchangelogcomponent'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    'zchangelogcomponent',
    extends=[RUN_COMMAND],
)
class ZchangelogExtension(AbstractExtension):

    def __init__(self, config, instances):

        @component()
        @requires(zchangelog='PyProc', args=['zchangelog'])
        class Zchangelog(object):

            def __init__(self, zchangelog):
                self.zchangelog = zchangelog

            def __call__(self, command, expected_exit_code=0, wait_for_exit=True):

                zchangelog_command = ('-vv {command}').format(command=command)

                logger.info(
                    'Running zchangelog command: {command}'.format(command=zchangelog_command))
                return self.zchangelog(
                    zchangelog_command, expected_exit_code=expected_exit_code, wait=wait_for_exit)
