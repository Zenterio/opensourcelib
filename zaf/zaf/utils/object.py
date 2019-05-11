"""Utilities for interacting with Python objects and types."""


class TypeComparator(object):

    def __init__(self, type):
        self._type = type

    def __eq__(self, other):
        return isinstance(other, self._type)
