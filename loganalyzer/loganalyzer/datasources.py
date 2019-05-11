"""
Contains different data source implementations.

The interface dictates that get_data() returns an iterable of
LogData objects
"""

import logging

from .item import LogData

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class DataSourceError(Exception):

    def __init__(self, msg, original_exception=None):
        super().__init__(type(self))
        self.msg = msg
        self.original_exception = original_exception

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class StreamDataSource():

    def __init__(self, stream):
        logger.debug('StreamDataSource: created')
        self.stream = stream

    def get_data(self):
        try:
            for index, line in enumerate(self.stream, start=1):
                yield LogData(index, line.rstrip())

        except UnicodeDecodeError as e:
            logger.error('StreamDataSource: get_data (error={err})'.format(err=e))
            raise DataSourceError('Error while processing data stream: {msg}'.format(msg=str(e)), e)
        except Exception as e:
            logger.error('StreamDataSource: get_data (error={err})'.format(err=e))
            raise DataSourceError('Error while processing data stream', e)


class FileDataSource(StreamDataSource):

    def __init__(self, path):
        logger.debug('FileDataSource: created')
        super().__init__(None)
        self.path = path

    def get_data(self):
        with open(self.path) as stream:
            self.stream = stream
            return super().get_data()
