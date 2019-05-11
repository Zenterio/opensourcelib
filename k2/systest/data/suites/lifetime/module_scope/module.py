from zaf.component.decorator import component, requires


@component(scope='module')
def my_module_component():
    print('my_module_component created')


@requires(c=my_module_component)
def test_something(c):
    print('test_something called')


@requires(c=my_module_component)
def test_something_else(c):
    print('test_something_else called')
