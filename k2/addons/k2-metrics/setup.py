import os

from setuptools import find_packages, setup

setup(
    name='k2-metrics',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Collects metrics data and generates reports.',
    long_description=(
        ('Facilities for collecting metrics data and generating reports in various formats.')),
    maintainer='Zenterio AB',
    maintainer_email='engineering.services@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'numpy==1.13.3',
        'matplotlib==2.1.1',
        'pandas==0.20.1',
    ],
    entry_points={
        'k2.addons': [
            'metrics = metrics.metrics:Metrics',
            (
                'triggermetricsreportgenerationontestrunfinished = '
                'metrics.triggers:TriggerMetricsReportGenerationOnTestRunFinished'),
            (
                'triggermetricsaggreatesgenerationontestrunfinished = '
                'metrics.triggers:TriggerMetricsAggregatesGenerationOnTestRunFinished'),
            'metricsjsonreporter = metrics.reporters.json:MetricsJsonReporter',
            'metricscsvreporter = metrics.reporters.csv:MetricsCsvReporter',
            'metricstextreporter = metrics.reporters.text:MetricsTextReporter',
            'metricsgraphreporter = metrics.reporters.graph:MetricsGraphReporter',
            'metricsseriesaggregator = metrics.aggregators.series:MetricsSeriesAggregator',
        ],
    },
)
