from zaf.config.options import Choice, ConfigOptionId

MULTIPLE_OPTION = ConfigOptionId(
    'multiple.option', 'description multiple.option', option_type=int, multiple=True)
DEFAULT_OPTION = ConfigOptionId('default.option', 'description default.option', default='default')
TRANSFORM_OPTION = ConfigOptionId(
    'transform.option', 'description transform.option', transform=lambda v: 'transformed ' + str(v))
TRANSFORM_CHOICE_OPTION = ConfigOptionId(
    'transform.choice.option',
    'description transform.choice.option',
    transform=lambda v: 'transformed ' + str(v),
    option_type=Choice(['A', 'B']),
    default='A')
