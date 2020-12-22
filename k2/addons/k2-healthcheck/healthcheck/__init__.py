from zaf.messages.message import EndpointId, MessageId

HEALTH_CHECK_ENDPOINT = EndpointId(
    'healthcheck', """\
    The K2 health check addon endpoint.
    """)

PERFORM_HEALTH_CHECK = MessageId(
    'PERFORM_HEALTH_CHECK', """
    Tells subscribers to this message to run their health check

    data: None
    """)

PERFORM_HEALTH_CHECKS = MessageId(
    'PERFORM_HEALTH_CHECK', """
    Send to the healthcheck endpoint to trigger running all health checks

    data: None
    """)


class HealthCheckError(Exception):
    """Raise from a dispatcher for the PERFORM_HEALTH_CHECK request to indicate check failure."""
    pass
