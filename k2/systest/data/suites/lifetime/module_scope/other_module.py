from zaf.component.decorator import requires

from .module import my_module_component


@requires(c=my_module_component)
def test_something_entierly_different(c):
    print('test_something_entierly_different called')
