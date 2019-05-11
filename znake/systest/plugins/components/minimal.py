from zaf.component.decorator import requires, component

MINIMAL_PROJECT = 'systest/data/minimal'


@requires(workspace='ProjectDirectory', args=[MINIMAL_PROJECT])
@requires(znake='Znake')
@component(name='ZnakeMinimal')
class ZnakeMinimal(object):

    def __init__(self, znake, workspace):
        self.znake = znake
        self.workspace = workspace

    def __call__(self, *args, **kwargs):
        return self.znake(*args, workspace=self.workspace, **kwargs)
