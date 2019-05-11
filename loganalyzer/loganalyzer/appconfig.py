"""Defines dedicated configuration objects on application level."""

import logging
import sys

import munch


class ConfigFactory():

    def __init__(self):
        self.log_attributes = ['verbose', 'quiet', 'logfile_path']

    def get_logconfig(self, argscfg):
        result = {}
        try:
            for attr in self.log_attributes:
                result[attr] = getattr(argscfg, attr)
        except KeyError:
            raise Exception(
                'Missing required attribute from master configuration object.'
                'This is an indication of a bug in the application.'
                ' (attribute={attr}'.format(attr=attr))
        return munch.munchify(result)


class ConfigureLogger():

    def configure_logger(self, logcfg):
        """
        Configure logging.

        Prints critical to stderr and info to file
        If verbose, warnings are written to stderr and debug to file
        If quiet, nothing to stderr
        """

        def get_setup_console(verbose):
            console_handler = logging.StreamHandler(stream=sys.stderr)
            console_handler.setLevel(logging.CRITICAL if not verbose else logging.INFO)
            console_formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(console_formatter)
            return console_handler

        def get_setup_logfile(logfile_path, verbose):
            logfile_handler = logging.FileHandler(logfile_path, mode='w', delay=True)
            logfile_handler.setLevel(logging.INFO if not verbose else logging.DEBUG)
            logfile_formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s: %(message)s')
            logfile_handler.setFormatter(logfile_formatter)
            return logfile_handler

        level = logging.INFO if not logcfg.verbose else logging.DEBUG
        handlers = []
        if not logcfg.quiet:
            handlers.append(get_setup_console(logcfg.verbose))
        if logcfg.logfile_path:
            handlers.append(get_setup_logfile(logcfg.logfile_path, logcfg.verbose))
        logging.basicConfig(level=level, handlers=handlers)
        logger = logging.getLogger(__name__)
        logger.debug('Logging configured (logcfg={config})'.format(config=logcfg))


def log_config(header, config):
    if len(config) == 0:
        return
    logger = logging.getLogger('config')
    logger.info(header)
    max_attr_len = max((len(attr) for attr in config.keys()))
    for attr, value in config.items():
        logger.info(
            '{attr:<{colwith}s}: {value}'.format(attr=attr, value=value, colwith=max_attr_len))
