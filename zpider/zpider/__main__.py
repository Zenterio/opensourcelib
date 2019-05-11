import logging
import sys

from zaf.application.application import Application, ApplicationConfiguration

from zpider import __version__

logger = logging.root


def main():

    exit_code = 1
    try:
        configuration = ApplicationConfiguration(
            'zpider', entrypoint='zpider', cli=True, version=__version__, root_package='zpider')
        exit_code = Application(
            configuration, entry_points=['zaf.addons', 'zpider.addons',
                                         'zpider.local_addons']).run()
    except Exception as e:
        if logger.hasHandlers():
            logger.debug(str(e), exc_info=True)
            logger.error(str(e))
        else:
            logger.error(str(e), exc_info=True)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
