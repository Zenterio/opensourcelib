from collections import namedtuple
from textwrap import dedent

from zaf.application import ApplicationContext

InternalCommandId = namedtuple(
    'InternalCommandId', [
        'name', 'description', 'callable', 'config_options', 'uses', 'hidden',
        'application_contexts', 'parent', 'allow_unknown_options'
    ])


class CommandId(InternalCommandId):
    __slots__ = ()

    def __new__(
            cls,
            name,
            description,
            callable,
            config_options,
            uses=None,
            hidden=False,
            application_contexts=None,
            parent=None,
            allow_unknown_options=False):
        """
        Define a new CommandId.

        :param name: the name of the command
        :param description: description of the command
        :param callable: the callable called when the command is executed
        :param config_options: the configuration options for the command
        :param uses: the command capabilities the command uses. (The command
                     name is implicitly a command capability.)
        :param hidden: Hide the command from the normal help.
        :param application_contexts: One or more ApplicationContexts that this command should be available
                                     for. If not given then the command will be applicable for all contexts.
        :param parent: This is a sub command to this parent command.
        :param allow_unknown_options: If this is True the command line parsing should not fail if encountering
                                      unknown options.
        :return: new CommandId
        """
        uses = set(uses) if uses is not None else set()
        uses.add(name)

        if application_contexts is None:
            application_contexts = ()
        elif isinstance(application_contexts, ApplicationContext):
            application_contexts = (application_contexts, )
        else:
            application_contexts = tuple(application_contexts)

        return super().__new__(
            cls, name,
            dedent(description).strip(), callable, tuple(config_options), tuple(uses), hidden,
            application_contexts, parent, allow_unknown_options)

    def is_applicable_for_application(self, application_context):
        return not self.application_contexts or application_context in self.application_contexts
