"""
Facilities for collecting metrics and generating reports.

Metric are created and accessed by sending requests to this addon.

Each metric is stored in a namespace, a dot-separated string indicating what the metric is about.
Metrics are either stored as series or as single values.

Metrics can be retreived either as raw data or rendered as a report.
Multiple different report renderers are available, ranging from text-only to graphical representations.

Registering Metrics
===================

Individual metrics are stored as instances of the Metrics class:

.. autoclass:: metrics.metrics.Metric
       :members: __init__

Metrics are registered by sending CREATE_METRIC events to the METRICS_ENDPOINT endpoint:

.. autofunction:: metrics.messages.create_series_metric
.. autofunction:: metrics.messages.create_single_value_metric


Collecting Metrics
==================

Metrics are grouped together in namespaces:

.. autoclass:: metrics.metrics.MetricsNamespace
       :members:

Metrics are collected by sending COLLECT_METRICS requests to the METRICS_ENDPOINT endpoint:

.. autofunction:: metrics.messages.collect_metrics


Metrics Reports
===============

Metrics report generation is initiated by sending GENERATE_METRICS_REPORT events to the METRICS_ENDPOINT endpoint.


Trouble Shooting Metrics Related Issues
=======================================

To make it easier to trouble-shoot metric related issues, it is possible to set
the configuration option metrics.writetologonexit: True, which will write the
stored metrics to the metric's log when the extension is destroyed.
"""

import logging
import re
from collections import OrderedDict
from operator import attrgetter
from pprint import saferepr

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name
from zaf.messages.decorator import sequential_dispatcher

from k2.utils.data import DataDefinition
from metrics import COLLECT_METRICS_REQUEST, CREATE_METRIC, GENERATE_METRICS_AGGREGATE, \
    GENERATE_METRICS_REPORT, METRICS_ENDPOINT, WRITE_TO_LOG_ON_EXIT

logger = logging.getLogger(get_logger_name('k2', 'metrics'))
logger.addHandler(logging.NullHandler())


class Metric(DataDefinition):
    """Storage for an individual metric measurement."""

    def __init__(self, timestamp, data, tags=None):
        """
        Create a new metric measurement.

        :param timestamp: When the measurement was made.
        :param data: The measurement.
        :param tags: List of tags associated with this metric (optional).
        """
        super().__init__(['timestamp', 'data', 'tags'])
        try:
            if tags is not None:
                iter(tags)
        except Exception:
            raise TypeError('tags must be iterable or None')
        self.timestamp = timestamp
        self.data = data
        self.tags = tags

    def __eq__(self, other):
        return (
            self.timestamp == other.timestamp and self.data == other.data
            and self.tags == other.tags)

    def __repr__(self):
        return 'Metric({timestamp}, {data}, {tags})'.format(
            timestamp=self.timestamp, data=self.data, tags=self.tags)


class MetricsNamespace(DataDefinition):
    """
    Storage for a collection of related metrics.

    Keeps track of what metric is associated with what namespace.

    Namespaces are stored in a tree structure, where new namespaces are
    automatically added using the dot operator.

    Example usage:

    .. code-block:: python

        >>> system_memory = MetricsNamespace()
        ...
        >>> # Make some measurements:
        >>> system_memory.free.store_series(...)
        >>> system_memory.used.store_series(...)
        ...
        >>> # Then access those measurements, like so:
        >>> system_memory       # Iterable containing the free and used namespaces
        >>> system_memory.free  # Iterable containing the metrics in the free namespace
        >>> system_memory.used  # Iterable containing the metrics in the used namespace

    Note that in the above example, three namespaces are created. The root node
    named "system_memory" and two leafs, "used" and "free". Only leaf nodes may
    contain metrics.

    Metrics are stored either as a series or as single-value.
    """

    def __init__(self, parent=None, name=None):
        self._children = OrderedDict()
        self._metrics = None
        self._name = name
        self._parent = parent

    @property
    def is_leaf(self):
        return not bool(self._children)

    @property
    def children(self):
        return self._children.values()

    @property
    def name(self):
        return self._name

    def __getattr__(self, name):
        if name not in self._children:
            namespace = MetricsNamespace(self, name)
            self._children[name] = namespace
            return namespace
        return self._children.get(name)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __iter__(self):
        try:
            if self.is_leaf and self._metrics is not None:
                if self._is_single_value():
                    yield self._metrics
                else:
                    yield from self._metrics
                raise StopIteration()
            else:
                for metric in self._children.values():
                    if isinstance(metric, MetricsNamespace):
                        yield metric
        except StopIteration:
            return

    def store_series(self, value):
        """
        Store a metric that is part of a series.

        Metrics that are part of a series are contained in a list. The list is
        created when the first metric in the series is stored. Subsequent metrics
        are appended to the list.

        :param value: The Metric instance to store.
        """
        if self._metrics is not None and self._is_single_value():
            raise ValueError('Will not override single-value metric with a series')
        self._raise_if_not_leaf()
        if self._metrics is None:
            self._metrics = []
        self._metrics.append(value)

    def store_single(self, value):
        """
        Store a metric that is a single value.

        A single-value metrics namespace contains a single metric. The value is
        overwritten each time a new metric is stored.

        :param value: The Metric instance to store.
        """
        if self._metrics and not self._is_single_value():
            raise ValueError('Will not override series metric with a single-value')
        self._raise_if_not_leaf()
        self._metrics = value

    def get_data(self):
        if not self.is_leaf:
            return OrderedDict(map(lambda child: (child._name, child.get_data()), self))
        data = [data.get_data() for data in self]
        return data[0] if len(data) == 1 else data

    def _raise_if_not_leaf(self):
        if not self.is_leaf:
            raise TypeError('Metrics can only be stored on leaf nodes')

    def _is_single_value(self):
        return isinstance(self._metrics, Metric)


class FlatMetricsNamespaceDataView(DataDefinition):
    """
    Provides a flat view of a metrics namespace.

    Example usage:

    .. code-block:: python

        >>> metrics = MetricsNamespace()
        ...
        >>> # Make some measurements:
        >>> metrics.system_memory.free.store_series(...)
        >>> metrics.system_memory.used.store_series(...)
        ...
        >>> system_memory_flat_data_view = FlatMetricsNamespaceDataView(metrics.system_memory)
        >>> system_memory_flat_data_view.get_data()
        {'system_memory.used': [...], 'system_memory.free': [...]}

    Any metadata such as timestamp or tags are stripped away, the resulting
    metrics lists contains only the data that was stored.
    """

    def __init__(self, namespace, key_filter=None, rename_regex=None, rename_to=''):
        self._namespace = namespace
        self._key_filter = key_filter
        if isinstance(rename_regex, str):
            self._rename_regex = re.compile(rename_regex)
        else:
            self._rename_regex = rename_regex
        self._rename_to = rename_to

    def get_data(self):
        import pandas

        flat_data = pandas.json_normalize(self._namespace.get_data()).to_dict(orient='list')
        flat_data = self._extend_keys_with_qualified_name(flat_data)

        if self._key_filter is not None:
            flat_data = {k: v for k, v in flat_data.items() if self._key_filter(k)}

        flat_data = self._rename_keys(flat_data, self._rename_regex, self._rename_to)

        # Single-value metrics are stored as {'namespace.nested_namespace.data': data}
        result = {k.replace('.data', ''): v for k, v in flat_data.items() if k.endswith('.data')}

        # Series metrics are stored as {'namespace.nested_namespace.data': [data1, data2, ...]}
        result.update(
            {
                k: list(map(lambda metric: metric['data'], v[0]))
                for k, v in flat_data.items() if isinstance(v[0], list)
            })

        return OrderedDict(sorted(result.items(), key=lambda t: t[0]))

    def _extend_keys_with_qualified_name(self, data):
        node = self._namespace
        prefix = ''
        while node is not None and node._name is not None:
            prefix = '.'.join((node._name, prefix))
            node = node._parent
        return {prefix + k: v for k, v in data.items()}

    def _rename_keys(self, data, rename_regex, rename_to):
        if rename_regex is not None:
            return {rename_regex.sub(rename_to, k): v for k, v in data.items()}
        else:
            return data


@FrameworkExtension(
    name='metrics',
    config_options=[ConfigOption(WRITE_TO_LOG_ON_EXIT, required=False)],
    endpoints_and_messages={
        METRICS_ENDPOINT: [
            CREATE_METRIC, COLLECT_METRICS_REQUEST, GENERATE_METRICS_REPORT,
            GENERATE_METRICS_AGGREGATE
        ]
    },
    groups=['metrics'],
)
class Metrics(AbstractExtension):
    """Facilities for storing metrics collected during a K2 run."""

    def __init__(self, config, instances):
        self._namespace = MetricsNamespace()
        self._write_to_log_on_exit = config.get(WRITE_TO_LOG_ON_EXIT, False)

    @sequential_dispatcher([CREATE_METRIC], [METRICS_ENDPOINT])
    def handle_store_metric(self, message):
        namespace = attrgetter(message.data.namespace)(self._namespace)
        metric = message.data.metric
        if message.data.series is True:
            logger.debug(
                'Storing series metric: {namespace} = {metric}'.format(
                    namespace=message.data.namespace, metric=metric))
            namespace.store_series(metric)
        else:
            logger.debug(
                'Storing single-value metric: {namespace} = {metric}'.format(
                    namespace=message.data.namespace, metric=metric))
            namespace.store_single(metric)

    @sequential_dispatcher([COLLECT_METRICS_REQUEST], [METRICS_ENDPOINT])
    def handle_collect_metrics(self, message):
        logger.debug('Collecting metrics: {namespace}'.format(namespace=message.data.namespace))
        return attrgetter(message.data.namespace)(self._namespace)

    def destroy(self):
        if self._write_to_log_on_exit:
            logger.debug('Metrics at time of destruction:')
            for k, v in FlatMetricsNamespaceDataView(self._namespace).get_data().items():
                logger.debug('{key}={value}'.format(key=k, value=saferepr(v)))
            logger.debug('Metrics Done')
