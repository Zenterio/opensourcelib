from zaf.config.options import ConfigOptionId

LOOP_DURATION = ConfigOptionId(
    'schedule.duration',
    (
        'Duration, specified as [[hh:]mm:]ss, to repeat already executed tests. '
        'Mutually exlusive with schedule.repeats'),
)

LOOP_REPEATS = ConfigOptionId(
    'schedule.repeats',
    (
        'Configures k2 to run specified tests several times. '
        'Mutually exclusive with schedule.duration'),
    option_type=int,
)
