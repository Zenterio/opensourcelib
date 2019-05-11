from zaf.component.decorator import component, requires


@component
def A():
    return 'A'


@component
def B():
    return 'B'


def test_that_implicitly_requires_A_and_B(A, B):
    print('test_that_implicitly_requires_A_and_B got component', A())
    print('test_that_implicitly_requires_A_and_B got component', B())


@requires(MyA='A', instance=False)
@requires(MyB='B', instance=False)
def test_that_explicitly_requires_A_and_B(MyA, MyB):
    print('test_that_explicitly_requires_A_and_B got component', MyA())
    print('test_that_explicitly_requires_A_and_B got component', MyB())


@requires(a=A)
@requires(b=B)
def test_that_requires_A_and_B_instances(a, b):
    print('test_that_requires_A_and_B_instances got component instance', a)
    print('test_that_requires_A_and_B_instances got component instance', b)
