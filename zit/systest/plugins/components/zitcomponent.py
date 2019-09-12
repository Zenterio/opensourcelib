import logging
import os

from k2.cmd.run import RUN_COMMAND
from zaf.component.decorator import component, requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

logger = logging.getLogger(get_logger_name('zit', 'zitcomponent'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    'zitcomponent',
    extends=[RUN_COMMAND],
)
class ZitExtension(AbstractExtension):

    def __init__(self, config, instances):

        @component()
        @requires(zit='PyProc', args=['zit'])
        class Zit(object):

            def __init__(self, zit):
                self.zit = zit

            def __call__(
                    self, command, expected_exit_code=0, wait_for_exit=True, workspace=os.getcwd()):

                logger.info('Running zit command: {command}'.format(command=command))
                return self.zit(
                    command,
                    expected_exit_code=expected_exit_code,
                    wait=wait_for_exit,
                    cwd=workspace)
