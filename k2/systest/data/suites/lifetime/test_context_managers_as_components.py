from zaf.component.decorator import component, requires


@component
class ContextManager(object):

    data = 'ContextManager data'

    def __enter__(self):
        print('ContextManager enter')
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        print('ContextManager exit')


@requires(c=ContextManager)
def test_my_feature(c):
    print('got data {data}'.format(data=c.data))
