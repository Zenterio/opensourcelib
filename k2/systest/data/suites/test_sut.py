from zaf.component.decorator import component, requires


@component(name='Comp')
@requires(sut='Sut', can=['a'])
def can_a(sut):
    print('a')


@component(name='Comp')
@requires(sut='Sut', can=['b'])
def can_b(sut):
    print('b')


@requires(comp='Comp')
def test_cans(comp):
    pass
