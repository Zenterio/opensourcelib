from zaf.component.decorator import requires

from .module import my_session_component


@requires(c=my_session_component, scope='session')
def test_c(c):
    print('test_c called')
