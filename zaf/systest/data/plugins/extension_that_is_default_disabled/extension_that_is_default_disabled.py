from zaf.extensions.extension import FrameworkExtension


@FrameworkExtension(
    name='extensionthatisdefaultdisabled',
    default_enabled=False,
)
class ExtensionThatIsDefaultDisabled(object):

    def __init__(self, config, instances):
        print('extension was enabled')
