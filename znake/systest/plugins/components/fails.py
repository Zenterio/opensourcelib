from zaf.component.decorator import requires, component

FAILS_PROJECT = 'systest/data/fails'


@requires(workspace='ProjectDirectory', args=[FAILS_PROJECT])
@requires(znake='Znake')
@component(name='ZnakeFails')
class ZnakeMinimal(object):

    def __init__(self, znake, workspace):
        self.znake = znake
        self.workspace = workspace

    def __call__(self, *args, **kwargs):
        return self.znake(*args, workspace=self.workspace, **kwargs)
