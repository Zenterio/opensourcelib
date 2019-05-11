from zaf.extensions.extension import AbstractExtension, FrameworkExtension


@FrameworkExtension('canbeinitialized21', load_order=21)
class CanBeInitialized21(AbstractExtension):

    def __init__(self, config, instances):
        print('CanBeInitialized21 init')

    def destroy(self):
        print('CanBeInitialized21 destroy')


@FrameworkExtension('cannotbeinitialized22', load_order=22)
class CanNotBeInitialized22(AbstractExtension):

    def __init__(self, config, instances):
        print('CanNotBeInitialized22 init')
        raise Exception()

    def destroy(self):
        print('CanNotBeInitialized22 destroy')


@FrameworkExtension('canbeinitialized23', load_order=23)
class CanBeInitialized23(AbstractExtension):

    def __init__(self, config, instances):
        print('CanBeInitialized23 init')

    def destroy(self):
        print('CanBeInitialized23 destroy')
