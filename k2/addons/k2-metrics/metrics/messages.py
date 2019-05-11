import functools
import time

from zaf.component.decorator import component, requires

from metrics import COLLECT_METRICS_REQUEST, CREATE_METRIC, METRICS_ENDPOINT
from metrics.metrics import Metric


class StoreMetric(object):

    def __init__(self, namespace, metric, tags=None, series=False):
        self.namespace = namespace
        self.metric = metric
        self.series = series


class CollectMetrics(object):

    def __init__(self, namespace, tags=None):
        self.namespace = namespace


def create_series_metric(messagebus, namespace, data, tags=None, timestamp=None):
    """
    Send a CREATE_METRIC request to the METRICS_ENDPOINT endpoint.

    The metric is stored as part of a series. Subsequent requests to store a
    metric in this namespace will be appended to the series.

    Series and single-value metrics are mutually exclusive in a given namespace.
    """
    return _create_metric(messagebus, namespace, data, True, tags=tags, timestamp=timestamp)


@requires(messagebus='MessageBus')
@component(name='CreateSeriesMetric')
def create_series_metric_component(messagebus):
    return functools.partial(create_series_metric, messagebus)


def create_single_value_metric(messagebus, namespace, data, tags=None, timestamp=None):
    """
    Send a CREATE_METRIC request to the METRICS_ENDPOINT endpoint.

    The metric is stored as a single value. Subsequent requests to store a
    metric in this namespace will override any existing metrics.

    Series and single-value metrics are mutually exclusive in a given namespace.
    """
    return _create_metric(messagebus, namespace, data, False, tags=tags, timestamp=timestamp)


@requires(messagebus='MessageBus')
@component(name='CreateSingleValueMetric')
def create_single_value_metric_component(messagebus):
    return functools.partial(create_single_value_metric, messagebus)


def collect_metrics(messagebus, namespace):
    """
    Send a COLLECT_METRICS request to the METRICS_ENDPOINT endpoint.

    :return: The requested metrics namespace.
    """
    return messagebus.send_request(
        COLLECT_METRICS_REQUEST, METRICS_ENDPOINT,
        data=CollectMetrics(namespace)).wait()[0].result()


def _create_metric(messagebus, namespace, data, series, tags=None, timestamp=None):
    if timestamp is None:
        timestamp = time.time()
    return messagebus.send_request(
        CREATE_METRIC,
        METRICS_ENDPOINT,
        data=StoreMetric(namespace, Metric(timestamp, data, tags), series=series))
