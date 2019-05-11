from zaf.component.decorator import component, requires

from k2.runner.exceptions import SkipException


@component
class SkipExceptionInInit(object):

    def __init__(self):
        raise SkipException('init')


@component
class SkipExceptionInEnter(object):

    def __enter__(self):
        raise SkipException('enter')

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@component
class SkipExceptionInExit(object):

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise SkipException('exit')


@requires(skip=SkipExceptionInInit)
def test_skipped_in_component_init(skip):
    pass


@requires(skip=SkipExceptionInEnter)
def test_skipped_in_component_enter(skip):
    pass


@requires(skip=SkipExceptionInExit)
def test_skipped_in_component_exit(skip):
    pass
