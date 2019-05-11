from zaf.component.decorator import component, requires


@component(scope='session')
def my_component():
    print('my_component created')


@requires(c=my_component, scope='test')
def test_my_feature(c):
    print('test_my_feature called')


@requires(c=my_component, scope='test')
def test_my_other_feature(c):
    print('test_my_other_feature called')
