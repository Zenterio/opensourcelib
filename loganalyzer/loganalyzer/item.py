"""
When doing log analysis, the parser is looking for items in the log.

An item has a definition (ItemDefinition) and any identification of an item in
a log, matching a definition  results in an instance (ItemInstance) being created.
"""

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Collector(list):

    def add(self, item):
        """Add an item to the collector."""
        logger.debug('Collector: Added item (item={item})'.format(item=item))
        self.append(item)


class ItemDefinition():

    definition_id = 0

    def __init__(
            self, markers, invalidators, title=None, item_id=None, description=None, watchers=None):
        self.markers = markers
        self.invalidators = invalidators
        self.definition_id = self.get_definition_id()
        self.title = title
        self.id = item_id
        self.description = description
        self.watchers = [] if watchers is None else watchers

    def __str__(self, *args, **kwargs):
        return super().__str__()

    @classmethod
    def get_definition_id(cls):
        cls.definition_id += 1
        return cls.definition_id


class ItemInstance():

    def __init__(self, definition):
        self.definition = definition
        self.matches = [None] * len(definition.markers)
        self.invalidators = [None] * len(definition.invalidators)

    def set_match(self, marker_index, logmatch):
        logger.debug(
            'ItemInstance: set_match (instance={self}, index={index}, logmatch={match})'.format(
                self=self, index=marker_index, match=logmatch))
        self.matches[marker_index] = logmatch

    def set_invalid(self, invalidator_index, logmatch):
        logger.debug(
            'ItemInstance: set_invalid (instance={self}, index={index}, logmatch={match})'.format(
                self=self, index=invalidator_index, match=logmatch))
        self.invalidators[invalidator_index] = logmatch

    def is_complete(self):
        return all(self.matches)

    def is_invalid(self):
        if len(self.invalidators) == 0:
            return False
        return all(self.invalidators)


class LogData():

    def __init__(self, index, content):
        self.index = index
        self.content = content

    def __str__(self, *args, **kwargs):
        return '{index}:{content}'.format(index=self.index, content=self.content)

    def __eq__(self, other):
        if other is None:
            return False
        return self.index == other.index and self.content == other.content

    def __ne__(self, other):
        return not self.__eq__(other)


class LogMatch():

    def __init__(self, data, match):
        self.data = data
        self.match = match

    def __str__(self, *args, **kwargs):
        mstr = ', match: {match}'.format(
            match=self.match.group(0)) if self.match is not None else ''
        return '{data}{match}'.format(data=self.data, match=mstr)

    def __eq__(self, other):
        if other is None:
            return False

        match_eq = False
        if self.match is None and other.match is None:
            match_eq = True
        elif self.match is not None and other.match is not None:
            if self.match.group(0) == other.match.group(0):
                match_eq = True

        return match_eq and self.data == other.data

    def __ne__(self, other):
        return not self.__eq__(other)
