from zaf.component.decorator import component, requires


@component(scope='session')
def my_session_component():
    print('my_session_component setup')
    yield 'session'
    print('my_session_component teardown')


@component(scope='module')
def my_module_component():
    print('my_module_component setup')
    yield 'module'
    print('my_module_component teardown')


@component(scope='class')
def my_class_component():
    print('my_class_component setup')
    yield 'class'
    print('my_class_component teardown')


@component(scope='test')
def my_test_component():
    print('my_test_component setup')
    yield 'test'
    print('my_test_component teardown')


class TestMyFeature(object):

    @requires(s=my_session_component)
    @requires(m=my_module_component)
    @requires(c=my_class_component)
    @requires(t=my_test_component)
    def test_my_feature(self, s, m, c, t):
        assert s == 'session'
        assert m == 'module'
        assert c == 'class'
        assert t == 'test'
        print('test_my_feature called')
