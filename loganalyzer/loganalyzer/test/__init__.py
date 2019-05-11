import logging
import os

LOG_FILE_PATH = os.environ.get('LOG_ANALYZER_LOG_FILE', 'testloganalyzer.log')
DEBUG = bool(os.environ.get('LOG_ANALYZER_DEBUG', False))

if DEBUG:
    logging.basicConfig(
        format='%(asctime)s|%(levelname)s|%(name)s: %(message)s',
        level=logging.DEBUG,
        filename=LOG_FILE_PATH,
        filemode='w')
