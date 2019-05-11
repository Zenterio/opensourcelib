from zaf.builtin.noop import NOOP_COMMAND
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from . import INSTANCES, MY_EXTENSION_ENDPOINT, MY_EXTENSION_MESSAGE


@CommandExtension(
    name='myextensionthatdefinesmessagesandendpoints',
    extends=[NOOP_COMMAND],
    endpoints_and_messages={
        MY_EXTENSION_ENDPOINT: [MY_EXTENSION_MESSAGE],
    },
)
class MyExtensionThatDefinesMessagesAndEndpoints(AbstractExtension):
    pass


@CommandExtension(
    name='myinstantiatedextensionthatdefinesmessagesandendpoints',
    extends=[NOOP_COMMAND],
    endpoints_and_messages={
        MY_EXTENSION_ENDPOINT: [MY_EXTENSION_MESSAGE],
    },
    config_options=[
        ConfigOption(INSTANCES, required=True, instantiate_on=True),
    ])
class MyInstantiatedExtensionThatDefinesMessagesAndEndpoints(AbstractExtension):
    pass
