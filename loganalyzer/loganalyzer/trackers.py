"""
The tracker is responsible for managing instances that are in the process of being created.

Different trackers are available to give different behavior.

See also item for additional information.
"""

import logging

from .item import ItemInstance, LogMatch

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SingleTracker():
    """
    Tracks only a single instance of the item.

    Newer matches overwrite previous matches, keeping the same instance.
    Only when an item is fully instantiated will it start tracking a new instance.
    """

    def __init__(self, definitions):
        self.definitions = definitions
        self.instances = [None] * len(definitions)

    def analyze(self, data, collector):
        for definition_index, definition in enumerate(self.definitions):
            instance = self.get_item_instance(definition_index)
            for invalidator_index, invalidator in enumerate(definition.invalidators):
                match = invalidator.search(data.content)
                if match:
                    instance.set_invalid(invalidator_index, LogMatch(data, match))
            for marker_index, marker in enumerate(definition.markers):
                match = marker.search(data.content)
                if match:
                    instance.set_match(marker_index, LogMatch(data, match))
            self.evaluate_instance(definition_index, instance, collector)

        nr_of_started_items = sum(x is not None for x in self.instances)
        logger.debug(
            'SingleTracker: analyze, number of started items (count={count})'.format(
                count=nr_of_started_items))

    def evaluate_instance(self, definition_index, instance, collector):
        if instance.is_invalid():
            self.reset_instance(definition_index)
            logger.debug(
                'SingleTracker: evaluate, instance invalidated (instance={instance})'.format(
                    instance=instance))
        elif instance.is_complete():
            collector.add(instance)
            self.reset_instance(definition_index)
            logger.debug(
                'SingleTracker: evaluate, instance completed (instance={instance})'.format(
                    instance=instance))
        else:
            logger.debug(
                'SingleTracker: evaluate, instance incomplete (instance={instance})'.format(
                    instance=instance))

    def get_new_item_instance(self, definition):
        instance = ItemInstance(definition)
        logger.debug(
            'SingleTracker: Started new instance'
            '(definition={definition}, instance={inst}, id={id})'.format(
                definition=definition, inst=instance, id=definition.definition_id))
        return instance

    def get_item_instance(self, definition_index):
        instance = self.instances[definition_index]
        if instance is None:
            instance = self.get_new_item_instance(self.definitions[definition_index])
            self.instances[definition_index] = instance
        return instance

    def reset_instance(self, definition_index):
        self.instances[definition_index] = None
