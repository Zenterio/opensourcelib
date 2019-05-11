from zaf.config.options import ConfigOptionId

ITERATIONS_OPTION = ConfigOptionId(
    name='iterations',
    description=(
        'Repeat the log output this many times. '
        'The log scope is rotated between each repetition.'),
    option_type=int,
    default=1)

ERRORS_OPTION = ConfigOptionId(
    name='errors',
    description=(
        'This many iterations will rotate their log scope with result "ERROR". '
        'Subsequent iterations will rotate their log scope with result "OK".'),
    option_type=int,
    default=0)
