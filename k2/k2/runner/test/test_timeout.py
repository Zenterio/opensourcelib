import unittest

from ..timeout import get_timeout, timeout


class TestTimeoutDecorator(unittest.TestCase):

    def test_decorator_raises_type_error_if_called_without_any_argument(self):
        with self.assertRaises(TypeError):

            @timeout
            def my_function():
                pass

    def test_decorator_raises_type_error_if_applied_multiple_times(self):
        with self.assertRaises(TypeError):

            @timeout(1)
            @timeout(2)
            def my_function():
                pass

    def test_decorator_raises_value_error_if_a_false_value_is_provided(self):
        with self.assertRaises(ValueError):

            @timeout(-1)
            def my_function():
                pass

    def test_get_timeout_with_decorated_function(self):

        @timeout(1)
        def my_function():
            pass

        assert get_timeout(my_function) == 1

    def test_get_timeout_with_decorated_class(self):

        @timeout(1)
        class MyClass(object):

            def my_member_function(self):
                pass

            @timeout(2)
            def my_member_function_with_overriden_timeout(self):
                pass

        assert get_timeout(MyClass) == 1
        assert get_timeout(MyClass().my_member_function) == 1
        assert get_timeout(MyClass().my_member_function_with_overriden_timeout) == 2

    def test_get_timeout_with_undecorated_function(self):

        def my_function():
            pass

        assert get_timeout(my_function) is None

    def test_get_timeout_with_undecorated_class(self):

        class MyClass(object):

            def my_member_function(self):
                pass

        assert get_timeout(MyClass) is None
        assert get_timeout(MyClass().my_member_function) is None
