import logging
import re

from zaf.component.decorator import component, requires
from zaf.extensions.extension import get_logger_name

from .common import wait_for

logger = logging.getLogger(get_logger_name('k2', 'waitfor', 'file'))
logger.addHandler(logging.NullHandler())


@component()
@requires(exec='Exec')
class WaitForFile:

    def __init__(self, exec):
        self._exec = exec

    def wait_for_match(self, file, regex, timeout=60, poll_interval=1.0):
        """
        Wait for a match in the file and return Match object.

        :param file: The file to look in
        :param regex: The regex pattern to use
        :param timeout: the timeout in seconds
        :param poll_interval: the interval in seconds to use when polling the file
        :return: Match object
        :raises: TimeoutError if match is not found before timeout
        """
        compiled_regex = re.compile(regex)

        def check_content():
            try:
                file_content = self._exec.send_line(
                    "cat '{file}'".format(file=file), expected_exit_code=0)
            except Exception:
                logger.debug(
                    'Error occurred when checking content of file {file}'.format(file=file),
                    exc_info=True)
                return False

            return compiled_regex.search(file_content)

        return wait_for(check_content, timeout=timeout, poll_interval=poll_interval)
