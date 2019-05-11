from k2.cmd.run import RUN_COMMAND

from zaf.extensions.extension import AbstractExtension, CommandExtension

from .zafappcomponent import ZafApp  # noqa


@CommandExtension('zafappcomponent', extends=[RUN_COMMAND])
class ZafAppComponent(AbstractExtension):
    pass
