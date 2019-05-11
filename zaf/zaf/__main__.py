import logging
import sys

from zaf.application.application import Application, ApplicationConfiguration
from zaf.application.context import ApplicationContext
from zaf.builtin.changelog import ChangeLogType

logger = logging.getLogger()


def main():
    exit_code = 1
    try:
        configuration = ApplicationConfiguration(
            'zaf',
            cli=True,
            application_context=ApplicationContext.EXTENDABLE,
            changelog_type=ChangeLogType.ZNAKE)
        exit_code = Application(configuration).run()
    except Exception as e:
        if logger.hasHandlers():
            logger.debug(str(e), exc_info=True)
            logger.error(str(e))
        else:
            logger.error(str(e), exc_info=True)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
