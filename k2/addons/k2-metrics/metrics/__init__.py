from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

METRICS_ENDPOINT = EndpointId('metrics', """\
    The K2 metrics addon endpoint.
    """)

CREATE_METRIC = MessageId(
    'CREATE_METRIC', """
   Store a metric.

   data: A metrics.messages.RegisterMetric instance.
   """)

COLLECT_METRICS_REQUEST = MessageId(
    'COLLECT_METRICS_REQUEST', """
    Retreive metrics collected so far.

    data: A metrics.messages.CollectMetrics instance.
    """)

GENERATE_METRICS_AGGREGATE = MessageId(
    'GENERATE_METRICS_AGGREGATE', """
    Request that metrics aggregates are generated.

    data: None
    """)

GENERATE_METRICS_REPORT = MessageId(
    'GENERATE_METRICS_REPORT', """
    Request that metrics reports are generated.

    data: None
    """)

WRITE_TO_LOG_ON_EXIT = ConfigOptionId(
    'metrics.writetologonexit',
    'If set, writes all metrics to the log on debug level when the metrics extension is destroyed.',
    option_type=bool,
    default=False)
