from functools import lru_cache

from json_log_formatter import JSONFormatter


class CustomJSONFormatter(JSONFormatter):

    def json_record(self, message, extra, record):
        extra['message'] = message
        extra['ts'] = record.asctime
        extra['logger'] = record.name
        extra['level'] = record.levelname
        return extra


class Filter:

    def __init__(self, exclude_dict):
        self._exclude_dict = exclude_dict

    def filter(self, record):
        logger_name = record.name
        logger_level = record.levelno
        return self._filter_internal(logger_name, logger_level)

    @lru_cache(maxsize=5000)
    def _filter_internal(self, logger_name, logger_level):
        exclude = None
        while not exclude:
            exclude = self._exclude_dict.get(logger_name, None)
            split = logger_name.rsplit('.', 1)
            if len(split) == 2:
                logger_name = split[0]
            else:
                logger_name = ''
        if logger_level < exclude:
            return 0
        return 1


def combine_loggers(loggers):
    """
    Combine a list of loggers by removing child loggers that are covered by parent loggers.

    Root logger is considered a parent to all loggers.
    :param loggers: list of logger names
    :return: list of a minimal set of loggers that covers the same logging
    """
    loggers_to_keep = []
    remaining_loggers = set(loggers)
    for logger1 in sorted(loggers, key=len, reverse=True):
        remaining_loggers.remove(logger1)

        for logger2 in remaining_loggers:
            if logger2 == '' or logger1.startswith(logger2 + '.'):
                break
        else:
            loggers_to_keep.append(logger1)

    return loggers_to_keep
