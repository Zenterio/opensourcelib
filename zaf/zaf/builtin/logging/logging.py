"""
Provides the zaf logging functionality.

This is used to configure logging to the console.

The global log level can be set with the *log.level* config option
and then it's possible to configure the level for specific loggers
using the the *log.<level>* config options.

It's also possible to set the log level for specific extensions using
the *ext.<extension name>.log.level*

Example of config that sets global log level to info but sets *click* extension to debug and *zaf.application*
to warning::

    log.level: info
    ext.click.log.level: debug
    log.warning: [zaf.application]

"""
import logging
import sys

from zaf.application import APPLICATION_NAME
from zaf.builtin.logging.utils import Filter
from zaf.config.options import ConfigOption
from zaf.extensions import ENABLED_EXTENSIONS
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

from . import EXTENSION_LOG_LEVEL, LOG_DEBUG, LOG_DIR, LOG_ERROR, LOG_FORMAT, LOG_INFO, LOG_LEVEL, \
    LOG_LEVEL_OFF, LOG_WARNING

logger = logging.getLogger(get_logger_name('zaf', 'logger'))
logger.addHandler(logging.NullHandler())


@FrameworkExtension(
    name='logger',
    load_order=101,
    config_options=[
        ConfigOption(LOG_LEVEL, required=True),
        ConfigOption(LOG_DIR, required=True),
        ConfigOption(LOG_FORMAT, required=True),
        ConfigOption(LOG_DEBUG, required=False),
        ConfigOption(LOG_INFO, required=False),
        ConfigOption(LOG_WARNING, required=False),
        ConfigOption(LOG_ERROR, required=False),
        ConfigOption(APPLICATION_NAME, required=False),
        ConfigOption(ENABLED_EXTENSIONS, required=False),
        ConfigOption(EXTENSION_LOG_LEVEL, required=False),
    ],
    groups=['logging'])
class RootLogger(AbstractExtension):
    """Configures logging."""

    def __init__(self, config, instances):
        log_level = map_level(config.get(LOG_LEVEL))
        log_format = config.get(LOG_FORMAT)
        application_name = config.get(APPLICATION_NAME)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(log_format)
        exclude_dict = {}
        if log_level:
            exclude_dict[''] = log_level
        else:
            exclude_dict[''] = LOG_LEVEL_OFF

        for extension in config.get(ENABLED_EXTENSIONS, []):
            extension_log_level = config.get(EXTENSION_LOG_LEVEL, entity=extension)
            for name in {'zaf', application_name}:
                extension_logger = logging.getLogger(get_logger_name(name, extension))
                extension_logger.setLevel(logging.DEBUG)
                if extension_log_level:
                    exclude_dict[get_logger_name(name, extension)] = map_level(extension_log_level)

        for logger_name in config.get(LOG_ERROR):
            exclude_dict[logger_name] = logging.ERROR

        for logger_name in config.get(LOG_WARNING):
            exclude_dict[logger_name] = logging.WARNING

        for logger_name in config.get(LOG_INFO):
            exclude_dict[logger_name] = logging.INFO

        for logger_name in config.get(LOG_DEBUG):
            exclude_dict[logger_name] = logging.DEBUG

        ch = logging.StreamHandler(sys.stderr)
        ch.setFormatter(formatter)
        ch.addFilter(Filter(exclude_dict))
        root_logger.addHandler(ch)


def map_level(level):
    if level is None or level.upper() == 'GLOBAL':
        return None
    elif level.upper() == 'DEBUG':
        return logging.DEBUG
    elif level.upper() == 'INFO':
        return logging.INFO
    elif level.upper() == 'WARNING':
        return logging.WARNING
    elif level.upper() == 'ERROR':
        return logging.ERROR
    elif level.upper() == 'OFF':
        return LOG_LEVEL_OFF
    else:
        return None
