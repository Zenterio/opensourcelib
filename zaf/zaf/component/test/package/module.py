class AClass(object):

    def method(self):
        pass

    def other_method(self):
        pass


class AnotherClass(object):

    def method(self):
        pass


def a_function():
    pass


def another_function():
    pass


def get_local_function():

    def a_local_function():
        pass

    return a_local_function


def get_another_local_function():

    def another_local_function():
        pass

    return another_local_function
