from zaf.messages.message import EndpointId, MessageId

MONITOR_ENDPOINT = EndpointId('monitor', """\
    The K2 monitor addon endpoint.
    """)

PERFORM_MEASUREMENT = MessageId(
    'PERFORM_MEASUREMENT', """
    Request that a monitor performs its measurements.

    data: None
    """)
