import os

from zaf.application import ApplicationContext
from zaf.config.options import ConfigOptionId, Path

OUTPUT_DIR = ConfigOptionId(
    'output.dir',
    'Path to output directory where reports and logs will be stored',
    option_type=Path(exists=False),
    default=os.path.join(os.getcwd(), 'output'),
    application_contexts=ApplicationContext.EXTENDABLE)
