"""The loganalyzer application."""

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LogAnalyzerApplication():

    def __init__(self, analyzer, datasource, *reporters):
        self.analyzer = analyzer
        self.datasource = datasource
        self.reporters = reporters

    def run(self):
        logger.info('Collecting data')
        for data in self.datasource.get_data():
            self.analyzer.analyze(data)
        items = self.analyzer.get_items()
        logger.info('Writing reports')
        for reporter in self.reporters:
            reporter.write_report(items)
        logger.info('Writing summaries')
        for reporter in self.reporters:
            reporter.write_summary(items)
