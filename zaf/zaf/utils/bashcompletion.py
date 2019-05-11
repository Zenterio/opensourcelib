import os

from zaf.application import ApplicationContext
from zaf.config.options import ConfigOptionId


def is_bash_completion():
    """Return True if running bash-completion."""
    return os.getenv('COMP_WORDS') is not None


NOT_BASH_COMPLETION = ConfigOptionId(
    'bash.completion.not.in.progress',
    'Set to true if the current task is to perform bash completion',
    option_type=bool,
    default=not is_bash_completion(),
    application_contexts=ApplicationContext.INTERNAL)
