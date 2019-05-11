from zaf.component.decorator import component, requires


@component(name='my_component', can=['A'])
def my_a_component():
    return 'A'


@component(name='my_component', can=['B'])
def my_b_component():
    return 'B'


@requires(c='my_component', can=['A'])
def test_need_a_component(c):
    print('test_need_a_component got a {type} component'.format(type=c))


@requires(c='my_component', can=['B'])
def test_need_b_component(c):
    print('test_need_b_component got a {type} component'.format(type=c))
