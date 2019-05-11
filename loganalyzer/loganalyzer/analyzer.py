"""Contains classes related to creating/instantiating via configuration."""

import logging

from .item import Collector, ItemDefinition
from .trackers import SingleTracker

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Analyzer():

    def __init__(self, trackers, collector):
        self.trackers = trackers
        self.collector = collector
        logger.debug('Analyzer: created')

    def analyze(self, data):
        for tracker in self.trackers:
            tracker.analyze(data, self.collector)

    def get_items(self):
        return self.collector


class AnalyzerFactory():

    def get_analyzer(self, config):
        logger.debug('AnalyzerFactory:get_analyzer (config={cfg})'.format(cfg=config))
        collector = Collector()
        definitions = self._create_definitions(config.definitions)
        trackers = [SingleTracker(definitions)]
        return Analyzer(trackers, collector)

    def _create_definitions(self, definitionsconfig):
        result = []
        for definition in definitionsconfig:
            result.append(
                ItemDefinition(
                    definition.markers, definition.invalidators, definition.title, definition.id,
                    definition.desc, definition.watchers))
        return result
