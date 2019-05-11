import logging
import sys

from zaf.application.application import Application, ApplicationConfiguration
from zaf.builtin.changelog import ChangeLogType

from zebra import __version__

logger = logging.getLogger('zebra')


def main():

    exit_code = 1
    try:
        configuration = ApplicationConfiguration(
            'zebra',
            entrypoint='zebra',
            cli=True,
            version=__version__,
            root_package='zebra',
            changelog_type=ChangeLogType.ZNAKE)
        exit_code = Application(configuration, entry_points=['zaf.addons', 'zebra.addons']).run()
    except Exception as e:
        if logger.hasHandlers():
            logger.debug(str(e), exc_info=True)
            logger.error(str(e))
        else:
            logger.error(str(e), exc_info=True)
    except KeyboardInterrupt as e:
        logger.debug(str(e), exc_info=True)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
