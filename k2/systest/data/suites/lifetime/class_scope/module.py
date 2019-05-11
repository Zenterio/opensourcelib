from zaf.component.decorator import component, requires


@component(scope='class')
def my_class_component():
    print('my_class_component created')


class TestMyFeature(object):

    @requires(c=my_class_component)
    def test_a(self, c):
        print('test_a called')

    @requires(c=my_class_component)
    def test_b(self, c):
        print('test_b called')


class TestMyOtherFeature(object):

    @requires(c=my_class_component)
    def test_c(self, c):
        print('test_c called')
