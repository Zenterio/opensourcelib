import logging
import sys

from systest.data.zafapp.zafapp import ZafAppStandalone

root_logger = logging.getLogger()
# Default config for rootlogger to not spam until logger is correctly configured
root_logger.setLevel(logging.INFO)


def main():
    exit_code = 1
    try:
        exit_code = ZafAppStandalone().run()
    except Exception as e:
        print(str(e))
        root_logger.warning(str(e), exc_info=True)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
