from zaf.component.decorator import component, requires


@component(name='fail_on_enter')
def fail_on_enter():
    raise Exception('fail on enter')


@component(name='fail_on_exit')
def fail_on_exit():
    yield ''
    raise Exception('fail on exit')


@requires(c='fail_on_enter')
def test_fail_on_enter(c):
    assert False, 'should not run'


@requires(c='fail_on_exit')
def test_fail_on_exit(c):
    assert True


def test_after_fail():
    pass
