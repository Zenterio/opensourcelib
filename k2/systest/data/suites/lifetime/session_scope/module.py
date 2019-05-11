from zaf.component.decorator import component, requires


@component(scope='session')
def my_session_component():
    print('my_session_component created')


class TestMyFeature(object):

    @requires(c=my_session_component)
    def test_a(self, c):
        print('test_a called')


@requires(c=my_session_component)
def test_b(c):
    print('test_b called')
