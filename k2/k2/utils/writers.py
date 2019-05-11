"""Utilities for writing DataDefinitions to stream."""

import abc
import csv
import json
import os
import sys
from itertools import zip_longest


class AbstractWriter(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def write(self, data):
        pass

    @abc.abstractmethod
    def write_to_stream(self, data, stream):
        pass


class AbstractFileWriter(AbstractWriter):

    def __init__(self, path):
        """If the path is set to dash (-), stdout will be used."""
        self._path = path

    def write(self, data):
        if self._path == '-':
            self.write_to_stream(data, sys.stdout)
        else:
            self._create_directories()
            with open(self._path, 'w') as f:
                self.write_to_stream(data, f)

    def _create_directories(self):
        path_to_create = os.path.dirname(self._path)
        if path_to_create != '':
            os.makedirs(path_to_create, exist_ok=True)


class JsonWriter(AbstractFileWriter):

    def write_to_stream(self, data, stream):
        stream.write(json.dumps(data.get_data(), indent=4))


class CsvWriter(AbstractFileWriter):

    def write_to_stream(self, data, stream):
        keys = list(data.get_data().keys())
        values = list(data.get_data().values())
        writer = csv.writer(stream)
        writer.writerow(keys)
        try:
            for row in zip_longest(*values, fillvalue=''):
                writer.writerow(row)
        except TypeError:
            writer.writerow(values)


class SingleValueTextWriter(AbstractFileWriter):

    def write_to_stream(self, data, stream):
        d = data.get_data()
        keys = list(d.keys())
        width = max(map(len, keys))
        for key, value in d.items():
            if value is None:
                value = ''
            stream.write('{key: <{width}}: {value}\n'.format(key=key, value=value, width=width))
