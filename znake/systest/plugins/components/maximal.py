from zaf.component.decorator import requires, component

MAXIMAL_PROJECT = 'systest/data/maximal'


@requires(workspace='ProjectDirectory', args=[MAXIMAL_PROJECT])
@requires(znake='Znake')
@component(name='ZnakeMaximal')
class ZnakeMinimal(object):

    def __init__(self, znake, workspace):
        self.znake = znake
        self.workspace = workspace

    def __call__(self, *args, **kwargs):
        return self.znake(*args, workspace=self.workspace, **kwargs)
