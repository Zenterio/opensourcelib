from zaf.config.options import ConfigOptionId

JENKINS_START_TIMEOUT = ConfigOptionId(
    'jenkins.start.timeout',
    'The timeout in seconds to wait for Jenkins to start.',
    option_type=float,
    default=120.0,
)
