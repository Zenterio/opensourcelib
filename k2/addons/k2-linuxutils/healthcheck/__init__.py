from zaf.messages.message import EndpointId, MessageId

PERFORM_HEALTH_CHECK = MessageId('PERFORM_HEALTH_CHECK', 'stub')

HEALTH_CHECK_ENDPOINT = EndpointId('healthcheck', 'stub')


class HealthCheckError(Exception):
    pass
