from zaf.commands.command import CommandId
from zaf.extensions.extension import AbstractExtension, CommandExtension


def action():
    pass


TESTCOMMANDADDON_COMMAND = CommandId('testcommand', 'A command only used for testing', action, [])


@CommandExtension('testcommandaddon', extends=[TESTCOMMANDADDON_COMMAND])
class TestCommandAddon(AbstractExtension):

    def __init__(self, config, instances):
        pass
