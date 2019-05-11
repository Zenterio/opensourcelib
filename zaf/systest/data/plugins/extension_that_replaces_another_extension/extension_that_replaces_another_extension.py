from zaf.extensions.extension import FrameworkExtension


@FrameworkExtension(
    name='extensionthatreplacesanotherextension',
    replaces=['extensionthatgetsreplaced'],
)
class ExtensionThatReplacesAnotherExtension(object):

    def __init__(self, config, instances):
        print('extension that replaces another extension was enabled')


@FrameworkExtension(name='extensionthatgetsreplaced')
class ExtensionThatGetsReplaced(object):

    def __init__(self, config, instances):
        print('extension that gets replaced was enabled')
