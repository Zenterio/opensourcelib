from zaf.config.options import ConfigOptionId
from zaf.config.types import Choice, Path

STR_OPTION = ConfigOptionId('str.option', 'description str.option', str)
INT_OPTION = ConfigOptionId('int.option', 'description int.option', int)
FLOAT_OPTION = ConfigOptionId('float.option', 'description float.option', float)
CHOICE_OPTION = ConfigOptionId(
    'choice.option', 'description choice.option', Choice(['a', 'b', 'c']))
PATH_OPTION = ConfigOptionId('path.option', 'description path.option', Path(exists=True))
BOOL_OPTION = ConfigOptionId('bool.option', 'description bool.option', bool)
