import threading
import unittest
from contextlib import contextmanager
from unittest.mock import MagicMock, Mock

from zaf.component.dependencygraph import ComponentDependencyError

from ..decorator import component, requires
from ..factory import ComponentContext, Factory, _InstanceId
from ..manager import ComponentManager, create_entity_map, create_registry
from ..scope import Scope


class TestFactory(unittest.TestCase):

    def setUp(self):
        self.component_manager = ComponentManager(create_registry(), create_entity_map())
        self.f = Factory(self.component_manager)
        self.scope = self.f.enter_scope('session')
        self.scope = self.f.enter_scope('module', self.scope)
        self.scope = self.f.enter_scope('class', self.scope)
        self.scope = self.f.enter_scope('test', self.scope)

    def test_call_with_no_requirements_is_equivalent_to_calling_a_function(self):
        m = MagicMock()
        m.__name__ = 'name'
        self.f.call(m, self.scope, 1, 2, a=3, b=4)
        m.assert_called_once_with(1, 2, a=3, b=4)

    def test_call_with_no_requirements_is_equivalent_to_instantiating_a_class(self):
        m = MagicMock(return_value=None)

        class MyClass(object):
            __init__ = m

        self.f.call(MyClass, self.scope, 1, 2, a=3, b=4)
        m.assert_called_once_with(1, 2, a=3, b=4)

    def test_require_a_single_component_using_name(self):
        m = MagicMock()
        m.__name__ = 'name'
        component(name='my_component')(m, component_manager=self.component_manager)

        @requires(c='my_component', instance=False)
        def my_function(c):
            c()

        self.f.call(my_function, self.scope)
        m.assert_called_once_with()

    def test_require_multiple_components_using_name(self):
        m1 = MagicMock()
        m2 = MagicMock()
        m1.__name__ = 'name1'
        m2.__name__ = 'name2'

        component(name='my_component')(m1, component_manager=self.component_manager)
        component(name='my_other_component')(m2, component_manager=self.component_manager)

        @requires(c1='my_component', instance=False)
        @requires(c2='my_other_component', instance=False)
        def my_function(c1, c2):
            c1()
            c2()

        self.f.call(my_function, self.scope)
        m1.assert_called_once_with()
        m2.assert_called_once_with()

    def test_requirement_is_mapped_to_the_expected_argument_name(self):
        m = MagicMock()
        m.__name__ = 'name'

        component(name='my_component')(m, component_manager=self.component_manager)
        component(name='my_other_component')(lambda: True, component_manager=self.component_manager)

        @requires(c1='my_component', instance=False)
        @requires(c2='my_other_component', instance=False)
        def my_function(c1, c2):
            c1()

        self.f.call(my_function, self.scope)
        m.assert_called_once_with()

    def test_component_function_can_require_other_component(self):
        m = Mock()
        m.__name__ = 'name'

        @component(component_manager=self.component_manager)
        def my_component():
            return m

        @component(component_manager=self.component_manager)
        @requires(my_component='my_component', instance=False)
        def my_other_component(my_component):
            return my_component()

        @requires(my_other_component='my_other_component')
        def my_function(my_other_component):
            my_other_component()

        self.f.call(my_function, self.scope)
        m.assert_called_once_with()

    def test_that_new_instances_of_transitive_component_are_created_for_each_sibling_scope(self):
        global number_of_instances
        number_of_instances = 0

        @component(component_manager=self.component_manager)
        def my_component():
            global number_of_instances
            number_of_instances += 1

        @requires(component=my_component)
        def my_function(component):
            pass

        session_scope = Scope('session', None, None)
        a_scope = Scope('a_scope', session_scope, None)
        b_scope = Scope('b_scope', session_scope, None)

        self.f.call(my_function, a_scope)
        self.f.call(my_function, b_scope)

        self.assertEqual(number_of_instances, 2)

    def test_that_same_instance_of_transitive_component_is_used_for_sibling_scopes_when_instantiated_on_parent_scope(
            self):  # noqa
        global number_of_instances
        number_of_instances = 0

        @component(scope='session', component_manager=self.component_manager)
        def my_component():
            global number_of_instances
            number_of_instances += 1

        @requires(component=my_component)
        def my_function(component):
            pass

        session_scope = Scope('session', None, None)
        a_scope = Scope('a_scope', session_scope, None)
        b_scope = Scope('b_scope', session_scope, None)

        self.f.call(my_function, a_scope)
        self.f.call(my_function, b_scope)

        self.assertEqual(number_of_instances, 1)

    def test_component_class_can_require_other_component(self):
        m = MagicMock()

        @component(component_manager=self.component_manager)
        def my_component():
            return m()

        @component(component_manager=self.component_manager)
        @requires(my_component='my_component', instance=False)
        class MyOtherComponent(object):

            def __init__(self, my_component):
                my_component()

        @requires(MyOtherComponent='MyOtherComponent')
        def my_function(MyOtherComponent):
            return MyOtherComponent

        c = self.f.call(my_function, self.scope)
        m.assert_called_once_with()
        self.assertIsInstance(c, MyOtherComponent)

    def test_call_accepts_extra_positional_arguments(self):
        m = MagicMock()

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        @requires(c='my_component', instance=False)
        def my_function(*args, **kwargs):
            m(*args, **kwargs)

        self.f.call(my_function, self.scope, 1)
        m.assert_called_once_with(1, c=my_component)

    def test_call_accepts_extra_keyword_arguments(self):
        m = MagicMock()

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        @requires(c='my_component', instance=False)
        def my_function(*args, **kwargs):
            m(*args, **kwargs)

        self.f.call(my_function, self.scope, my_keyword_argument=2)
        m.assert_called_once_with(c=my_component, my_keyword_argument=2)

    def test_explicit_requirements_take_precedence_over_implicit_requirements(self):

        @component(component_manager=self.component_manager)
        def my_component():
            return 3

        @requires(my_component='my_component')
        def my_function(my_component):
            return my_component

        self.assertEqual(self.f.call(my_function, self.scope), 3)

    def test_a_component_can_be_requested_by_reference(self):

        @component(component_manager=self.component_manager)
        def my_component():
            return 3

        @requires(my_component=my_component)
        def my_function(my_component):
            return my_component

        self.assertEqual(self.f.call(my_function, self.scope), 3)

    def test_raises_exception_if_explicit_requirement_can_not_be_found(self):

        @requires(x='y', instance=False)
        def my_function(x):
            pass

        with self.assertRaises(ComponentDependencyError):
            self.f.call(my_function, self.scope)

    def test_raises_exception_if_two_explicit_requirements_share_the_same_name(self):

        @component(component_manager=self.component_manager)
        def y():
            pass

        @requires(x='y', instance=False)
        @requires(x='y', instance=False)
        def my_function(x):
            pass

        with self.assertRaises(ComponentDependencyError):
            self.f.call(my_function, self.scope)

    def test_raises_exception_if_requirement_is_not_named_or_callable(self):

        @requires(x=(1, 2, 3), instance=False)
        def my_function(x):
            pass

        with self.assertRaises(ComponentDependencyError):
            self.f.call(my_function, self.scope)

    def test_can_pass_arguments_to_component(self):

        @component(component_manager=self.component_manager)
        def my_sum(*args):
            return sum(args)

        @requires(s=my_sum, args=[1, 2, 3])
        def test_sum(s):
            return s

        self.assertEqual(self.f.call(test_sum, self.scope), 6)

    def test_raises_exception_if_multiple_requirements_are_named_in_the_same_statement(self):

        @component(component_manager=self.component_manager)
        def a():
            pass

        @component(component_manager=self.component_manager)
        def b():
            pass

        with self.assertRaises(Exception):

            @requires(a=a, b=b, instance=False)
            def my_function():
                pass

    def test_component_with_session_default_scope(self):
        my_object = object()

        @component(scope='session', component_manager=self.component_manager)
        def my_component():
            return my_object

        @requires(c=my_component)
        def my_function(c):
            pass

        self.f.call(my_function, self.scope)
        self.assertIs(
            self.scope.parent.parent.parent.get_instance(_InstanceId(my_component)), my_object)

    def test_component_with_module_default_scope(self):
        my_object = object()

        @component(scope='module', component_manager=self.component_manager)
        def my_component():
            return my_object

        @requires(c=my_component)
        def my_function(c):
            pass

        self.f.call(my_function, self.scope)
        self.assertIs(self.scope.parent.parent.get_instance(_InstanceId(my_component)), my_object)

    def test_component_with_class_default_scope(self):
        my_object = object()

        @component(scope='class', component_manager=self.component_manager)
        def my_component():
            return my_object

        @requires(c=my_component)
        def my_function(c):
            pass

        self.f.call(my_function, self.scope)
        self.assertIs(self.scope.parent.get_instance(_InstanceId(my_component)), my_object)

    def test_component_with_test_default_scope(self):
        my_object = object()

        @component(scope='test', component_manager=self.component_manager)
        def my_component():
            return my_object

        @requires(c=my_component)
        def my_function(c):
            pass

        self.f.call(my_function, self.scope)
        self.assertIs(self.scope.get_instance(_InstanceId(my_component)), my_object)

    def test_component_with_no_scope_is_assigned_lowest_level_scope(self):
        my_object = object()

        @component(component_manager=self.component_manager)
        def my_component():
            return my_object

        @requires(c=my_component)
        def my_function(c):
            pass

        self.f.call(my_function, self.scope)
        self.assertIs(self.scope.get_instance(_InstanceId(my_component)), my_object)

    def test_requires_scope_overrides_default_component_scope(self):
        my_object = object()

        @component(scope='module', component_manager=self.component_manager)
        def my_component():
            return my_object

        @requires(c=my_component, scope='class')
        def my_function(c):
            pass

        self.f.call(my_function, self.scope)
        self.assertIs(self.scope.parent.get_instance(_InstanceId(my_component)), my_object)
        self.assertIs(
            self.scope.parent.parent.get_instance(_InstanceId(my_component)), Scope.NO_INSTANCE)

    def test_component_can_have_dependency_with_longer_lifetime(self):
        my_session_object = object()
        my_module_object = object()
        my_test_object = object()

        @component(scope='session', component_manager=self.component_manager)
        def my_session_component():
            return my_session_object

        @component(scope='module', component_manager=self.component_manager)
        @requires(session_component=my_session_component)
        def my_module_component(session_component):
            self.assertIs(session_component, my_session_object)
            return my_module_object

        @requires(module_component=my_module_component)
        def my_function(module_component):
            self.assertIs(module_component, my_module_object)
            return my_test_object

        self.assertIs(self.f.call(my_function, self.scope), my_test_object)

    def test_component_can_not_have_dependency_with_shorter_lifetime(self):
        my_session_object = object()
        my_module_object = object()
        my_test_object = object()

        @component(scope='module', component_manager=self.component_manager)
        def my_session_component():
            return my_session_object

        @component(scope='session', component_manager=self.component_manager)
        @requires(session_component=my_session_component)
        def my_module_component(session_component):
            self.assertIs(session_component, my_session_object)
            return my_module_object

        @requires(module_component=my_module_component)
        def my_function(module_component):
            self.assertIs(module_component, my_module_object)
            return my_test_object

        with self.assertRaises(ComponentDependencyError):
            self.f.call(my_function, self.scope)

    def test_generator_component(self):
        call_before_yield = MagicMock()
        object_to_yield = object()
        call_after_yield = MagicMock()

        @component(component_manager=self.component_manager)
        def my_generator_component():
            call_before_yield()
            yield object_to_yield
            call_after_yield()

        @requires(c=my_generator_component)
        def my_function(c):
            return c

        def my_other_function():
            pass

        self.assertIs(self.f.call(my_function, self.scope), object_to_yield)
        call_before_yield.assert_called_once_with()
        self.assertFalse(call_after_yield.called)
        self.f.exit_scope(self.scope)
        call_after_yield.assert_called_once_with()

    def test_context_manager_class_component(self):

        @component(component_manager=self.component_manager)
        class MyContextManager(object):
            __enter__ = MagicMock(return_value=3)
            __exit__ = MagicMock()

        @requires(c=MyContextManager)
        def my_function(c):
            return c

        self.assertEqual(self.f.call(my_function, self.scope), 3)
        MyContextManager.__enter__.assert_called_once_with()
        self.assertFalse(MyContextManager.__exit__.called)
        self.f.exit_scope(self.scope)
        self.assertTrue(MyContextManager.__exit__.called)

    def test_context_manager_function_component(self):
        called_on_enter = MagicMock()
        called_on_exit = MagicMock()

        @component(component_manager=self.component_manager)
        @contextmanager
        def my_context_manager():
            called_on_enter()
            yield 3
            called_on_exit()

        @requires(c=my_context_manager)
        def my_function(c):
            return c

        self.assertEqual(self.f.call(my_function, self.scope), 3)
        called_on_enter.assert_called_once_with()
        self.assertFalse(called_on_exit.called)
        self.f.exit_scope(self.scope)
        called_on_exit.assert_called_once_with()

    def test_context_manager_function_component_is_only_entered_once(self):
        called_on_enter = MagicMock()
        called_on_exit = MagicMock()

        @component(component_manager=self.component_manager)
        @contextmanager
        def my_context_manager():
            called_on_enter()
            yield 3
            called_on_exit()

        @component(component_manager=self.component_manager)
        @requires(c=my_context_manager)
        def my_function(c):
            return c

        @requires(a=my_function)
        @requires(b=my_context_manager)
        def my_other_function(a, b):
            return a == b

        self.assertTrue(self.f.call(my_other_function, self.scope))
        called_on_enter.assert_called_once_with()
        self.assertFalse(called_on_exit.called)
        self.f.exit_scope(self.scope)
        called_on_exit.assert_called_once_with()

    def test_context_manager_exit_is_called_with_exception_if_enter_fails(self):
        called_on_exit = MagicMock()

        @component(component_manager=self.component_manager)
        class FailOnEnter():

            def __enter__(self):
                raise (Exception('enter failed'))

            def __exit__(self, exc_type, exc_val, exc_tb):
                called_on_exit(str(exc_val))

        @requires(a=FailOnEnter)
        def my_test(a):
            assert False, 'should not be called'

        with self.assertRaises(Exception):
            self.f.call(my_test, self.scope)
        called_on_exit.assert_called_once_with('enter failed')

    def test_different_arguments_should_yield_different_instances(self):

        @component(scope='module', component_manager=self.component_manager)
        def my_component_that_takes_arguments(x, y):
            return x, y

        @requires(c=my_component_that_takes_arguments, args=[1, 2])
        def my_function(c):
            return c

        @requires(c=my_component_that_takes_arguments, args=[2, 3])
        def my_other_function(c):
            return c

        self.assertEqual((1, 2), self.f.call(my_function, self.scope))
        self.assertEqual((2, 3), self.f.call(my_other_function, self.scope))

    def test_raises_factory_error_if_no_suitable_component_can_be_found(self):

        @component(can=['A'], component_manager=self.component_manager)
        def my_component():
            pass

        @requires(c='my_component', can=['B'])
        def my_function(c):
            pass

        with self.assertRaises(ComponentDependencyError):
            self.f.call(my_function, self.scope)

    def test_component_can_match_single_can_requirement(self):

        @component(can=['B'], component_manager=self.component_manager)
        def my_component():
            return 123

        @requires(c='my_component', can=['B'])
        def my_function(c):
            return c

        self.assertEqual(self.f.call(my_function, self.scope), 123)

    def test_select_highest_priority_component_when_instance_true(self):

        @component(name='my_component', priority=0, component_manager=self.component_manager)
        def a():
            return 'A'

        @component(name='my_component', priority=-1, component_manager=self.component_manager)
        def b():
            return 'B'

        @component(name='my_component', priority=1, component_manager=self.component_manager)
        def c():
            return 'C'

        @requires(c='my_component', instance=True)
        def my_function(c):
            return c

        self.assertEqual(self.f.call(my_function, self.scope), 'C')

        def test_select_highest_priority_component_when_instance_false(self):

            @component(name='my_component', priority=0, component_manager=self.component_manager)
            def a():
                return 'A'

            @component(name='my_component', priority=-1, component_manager=self.component_manager)
            def b():
                return 'B'

            @component(name='my_component', priority=1, component_manager=self.component_manager)
            def c():
                return 'C'

            @requires(c='my_component', instance=False)
            def my_function(c):
                return c()

        self.assertEqual(self.f.call(my_function, self.scope), 'C')

    def test_components_are_created_in_the_order_they_are_required(self):
        instance_order = []

        @component(component_manager=self.component_manager)
        def A():
            instance_order.append('A')

        @component(component_manager=self.component_manager)
        def B():
            instance_order.append('B')

        @component(component_manager=self.component_manager)
        def C():
            instance_order.append('C')

        @component(component_manager=self.component_manager)
        def D():
            instance_order.append('D')

        @requires(a=A)
        @requires(c=C)
        @requires(b=B)
        @requires(d=D)
        def my_function(a, b, c, d):
            pass

        self.f.call(my_function, self.scope)
        self.assertEqual(instance_order, ['A', 'C', 'B', 'D'])

    def test_component_enter_scope_order(self):
        instance_order = []

        @component(scope='session', component_manager=self.component_manager)
        def session_scope():
            instance_order.append('session')

        @component(scope='module', component_manager=self.component_manager)
        def module_scope():
            instance_order.append('module')

        @component(scope='class', component_manager=self.component_manager)
        def class_scope():
            instance_order.append('class')

        @component(scope='test', component_manager=self.component_manager)
        def test_scope():
            instance_order.append('test')

        @requires(a=test_scope)
        @requires(c=module_scope)
        @requires(d=session_scope)
        @requires(b=class_scope)
        def my_function(a, b, c, d):
            pass

        self.f.call(my_function, self.scope)
        self.assertEqual(instance_order, ['session', 'module', 'class', 'test'])

    def test_get_implicit_requirements_with_class(self):
        m = MagicMock()

        @component(component_manager=self.component_manager)
        class MyClass(object):
            pass

        def my_function(MyClass):
            m(MyClass)

        self.f.call(my_function, Scope('name', None, None))
        m.assert_called_once_with(MyClass)

    def test_get_implicit_requirements_with_function(self):
        m = MagicMock()

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        def my_function(my_component):
            m(my_component)

        self.f.call(my_function, Scope('name', None, None))
        m.assert_called_once_with(my_component)

    def test_uses_selects_the_correct_transitive_dependency(self):

        @component(name='A', can=['1'], component_manager=self.component_manager)
        class A1(object):

            def __init__(self):
                self.name = 'a1'

        @component(name='A', can=['2'], component_manager=self.component_manager)
        class A2(object):

            def __init__(self):
                self.name = 'a2'

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A')
        class B(object):

            def __init__(self, a):
                self.name = a.name

        @component(name='C', component_manager=self.component_manager)
        @requires(a='A', can=['1'])
        @requires(b='B', uses=['a'])
        class C1(object):

            def __init__(self, a, b):
                self.name = b.name

        @component(name='C', component_manager=self.component_manager)
        @requires(a='A', can=['2'])
        @requires(b='B', uses=['a'])
        class C2(object):

            def __init__(self, a, b):
                self.name = b.name

        @requires(c1=C1)
        def test_1(c1):
            return c1.name

        @requires(c2=C2)
        def test_2(c2):
            return c2.name

        self.assertEqual(self.f.call(test_1, scope=self.scope), 'a1')
        self.assertEqual(self.f.call(test_2, scope=self.scope), 'a2')

    def test_uses_in_multiple_levels_combines_all_cans(self):

        @component(name='A', can=['1', 'x'], component_manager=self.component_manager)
        class A1X(object):

            def __init__(self):
                self.name = 'a1x'

        @component(name='A', can=['1', 'y'], component_manager=self.component_manager)
        class A1Y(object):

            def __init__(self):
                self.name = 'a1y'

        @component(name='A', can=['2', 'x'], component_manager=self.component_manager)
        class A2X(object):

            def __init__(self):
                self.name = 'a2x'

        @component(name='A', can=['2', 'y'], component_manager=self.component_manager)
        class A2Y(object):

            def __init__(self):
                self.name = 'a2y'

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A')
        class B(object):

            def __init__(self, a):
                self.name = a.name

        @component(name='C', component_manager=self.component_manager)
        @requires(a='A', can=['1'])
        @requires(b='B', uses=['a'])
        class C1(object):

            def __init__(self, a, b):
                self.name = b.name

        @component(name='C', component_manager=self.component_manager)
        @requires(a='A', can=['2'])
        @requires(b='B', uses=['a'])
        class C2(object):

            def __init__(self, a, b):
                self.name = b.name

        @requires(c1=C1, uses=['a'])
        @requires(a='A', can=['x'])
        def test_1(a, c1):
            return c1.name

        @requires(c2=C2, uses=['a'])
        @requires(a='A', can=['y'])
        def test_2(a, c2):
            return c2.name

        self.assertEqual(self.f.call(test_1, scope=self.scope), 'a1x')
        self.assertEqual(self.f.call(test_2, scope=self.scope), 'a2y')

    def test_two_required_components_uses_same_component_instance(self):

        @component(name='A', can=['1', '2'], component_manager=self.component_manager)
        class AComp(object):
            pass

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A')
        class BComp(object):

            def __init__(self, a):
                self.a = a

        @component(component_manager=self.component_manager)
        @requires(b1='B')
        class C1(object):

            def __init__(self, b1):
                self.name = 'C1'
                self.b = b1

        @component(component_manager=self.component_manager)
        @requires(a2='A')
        class C2(object):

            def __init__(self, a2):
                self.name = 'C2'
                self.a = a2

        @requires(a='A')
        @requires(c1=C1, uses=['a'])
        @requires(c2=C2, uses=['a'])
        def func(a, c1, c2):
            return (c1, c2)

        c1, c2 = self.f.call(func, scope=self.scope)
        self.assertEqual(c1.name, 'C1')
        self.assertIs(c1.b.a, c2.a)

    def test_factory_fails_when_uses_selects_component_that_is_not_compatible_with_other_requires(
            self):

        @component(name='A', can=['1'], component_manager=self.component_manager)
        class A1():

            def __init__(self):
                self.name = 'a1'

        @component(name='A', can=['2'], component_manager=self.component_manager)
        class A2():

            def __init__(self):
                self.name = 'a2'

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A', can=['2'])
        class B():

            def __init__(self, a):
                self.a = a.name

        @requires(a='A', can=['1'])
        @requires(b='B', uses=['a'])
        def test_1(a, b):
            pass

        with self.assertRaises(Exception):
            self.f.call(test_1, scope=self.scope)

    def test_uses_only_combines_nodes_below_the_requirement_node_in_the_graph(self):

        @component(name='C', can=['C1'], component_manager=self.component_manager)
        def c1():
            return 'c1'

        @component(name='C', can=['C2'], component_manager=self.component_manager)
        def c2():
            return 'c2'

        @component(name='Parent', component_manager=self.component_manager)
        @requires(c='C')
        def parent(c):
            return 'parent ' + c

        @requires(c='C', can=['C1'])
        @requires(parent='Parent', uses=['c'])
        @requires(c2='C', can=['C2'])
        def test(c, parent, c2):
            return c, parent, c2

        c_val, parent_val, c2_val = self.f.call(test, scope=self.scope)
        self.assertEqual(c_val, 'c1')
        self.assertEqual(parent_val, 'parent c1')
        self.assertEqual(c2_val, 'c2')

    def test_factory_fixates_entity_component(self):

        @component(name='A', component_manager=self.component_manager)
        class A1(object):
            entity = 'a1'

            def __init__(self):
                self.name = 'a1'

        @component(name='A', component_manager=self.component_manager)
        class A2(object):
            entity = 'a2'

            def __init__(self):
                self.name = 'a2'

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A')
        class B(object):

            def __init__(self, a):
                self.name = a.name

        @requires(b=B)
        def test(b):
            return b.name

        self.assertEqual(self.f.call(test, scope=self.scope, fixated_entities=['a1']), 'a1')
        self.assertEqual(self.f.call(test, scope=self.scope, fixated_entities=['a2']), 'a2')

    def test_factory_will_not_fixate_entity_when_fixate_entities_on_requires_is_false(self):

        @component(name='A', can=['1'], component_manager=self.component_manager)
        class A1(object):
            entity = 'a1'

            def __init__(self):
                self.name = 'a1'

        @component(name='A', can=['2'], component_manager=self.component_manager)
        class A2(object):
            entity = 'a2'

            def __init__(self):
                self.name = 'a2'

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A', can=['2'], fixate_entities=False)
        class B(object):

            def __init__(self, a):
                self.name = a.name

        @requires(b=B)
        def test(b):
            return b.name

        self.assertEqual(self.f.call(test, scope=self.scope, fixated_entities=['a1']), 'a2')
        self.assertEqual(self.f.call(test, scope=self.scope, fixated_entities=['a2']), 'a2')

    def test_require_context_contains_information_about_the_root_callable(self):
        self.component_manager.register_component(ComponentContext)

        @component(component_manager=self.component_manager)
        @requires(context='ComponentContext')
        class Component(object):

            def __init__(self, context):
                self._context = context

            def __call__(self):
                return {
                    'name': self._context.callable_name,
                    'qualname': self._context.callable_qualname,
                }

        @requires(comp=Component)
        def root_callable(comp):
            return comp()

        self.maxDiff = None
        self.assertEqual(self.f.call(root_callable, scope=self.scope)['name'], 'root_callable')
        self.assertEqual(
            self.f.call(root_callable, scope=self.scope)['qualname'], (
                'zaf.component.test.test_factory.TestFactory.'
                'test_require_context_contains_information_about_the_root_callable.<locals>.root_callable'
            ))

    def test_component_context_contains_args_and_kwargs_after_root_callable_is_called(self):
        self.component_manager.register_component(ComponentContext)

        @component(component_manager=self.component_manager)
        @requires(context='ComponentContext')
        class Component(object):

            def __init__(self, context):
                self.context = context

        @requires(comp=Component)
        def root_callable(arg, kwarg=None, comp=None):
            return comp

        self.maxDiff = None
        comp = self.f.call(root_callable, self.scope, 'arg', kwarg='kwarg')
        self.assertEqual(comp.context.args, ('arg', ))
        self.assertEqual(comp.context.kwargs, {'kwarg': 'kwarg', 'comp': comp})

    def test_component_context_does_not_contain_args_and_kwargs_before_root_callable_is_called(
            self):
        self.component_manager.register_component(ComponentContext)

        @component(component_manager=self.component_manager)
        @requires(context='ComponentContext')
        class Component(object):

            def __init__(self, context):
                self._args = context.args
                self._kwargs = context.kwargs

            def __call__(self):
                return self._args, self._kwargs

        @requires(comp=Component)
        def root_callable(arg, kwarg=None, comp=None):
            return comp()

        self.maxDiff = None
        args, kwargs = self.f.call(root_callable, self.scope, 'arg', kwarg='kwarg')
        self.assertEqual(args, None)
        self.assertEqual(kwargs, None)

    def test_required_components_may_be_omitted_from_the_arguments_list(self):

        @component
        class A(object):

            def __call__(self):
                return 'A'

        @component
        class B(object):

            def __call__(self):
                return 'B'

        @component
        @requires(a=A)
        @requires(b=B)
        def function_component(a):
            return lambda: a()  # noqa

        @component
        @requires(a=A)
        @requires(b=B)
        class ClassComponent(object):

            def __init__(self, b):
                self._b = b()

            def __call__(self):
                return self._b

        self.assertEqual(self.f.call(function_component, scope=self.scope)(), 'A')
        self.assertEqual(self.f.call(ClassComponent, scope=self.scope)(), 'B')

    def test_factory_takes_an_instance_id_specific_lock_in_the_scope_when_instantiating_components(
            self):

        @component
        def a():
            self.assertTrue(self.scope._instance_locks[0][1].locked())

        @requires(a=a)
        def f(a):
            pass

        self.f.call(f, scope=self.scope)
        self.assertFalse(self.scope._instance_locks[0][1].locked())

    def test_factory_can_instantiate_components_with_different_instance_ids_in_parallel(self):

        block_a_event = threading.Event()
        block_b_event = threading.Event()
        a_result = False

        @component
        def a():
            block_b_event.set()
            nonlocal a_result
            a_result = block_a_event.wait(timeout=1)

        @component
        def b():
            block_a_event.set()
            self.assertTrue(block_b_event.wait(timeout=1))

        @requires(a=a)
        def fa(a):
            pass

        @requires(b=b)
        def fb(b):
            pass

        thread = threading.Thread(target=self.f.call, args=[fa], kwargs={'scope': self.scope})
        try:
            thread.start()
            self.f.call(fb, scope=self.scope)
        finally:
            thread.join()
            self.assertTrue(a_result)

    def test_factory_instantiates_a_single_instance_for_same_instance_id_for_parallel_calls(self):
        init_called = threading.Event()
        init_block = threading.Event()

        @component
        class A:
            instance_count = 0

            def __init__(self):
                init_called.set()
                assert init_block.wait(timeout=1)
                A.instance_count += 1

        @requires(a=A)
        def f(a):
            pass

        thread1 = threading.Thread(target=self.f.call, args=[f], kwargs={'scope': self.scope})
        thread2 = threading.Thread(target=self.f.call, args=[f], kwargs={'scope': self.scope})
        try:
            thread1.start()
            thread2.start()
            init_called.wait(timeout=1)
            init_block.set()
        finally:
            thread1.join()
            thread2.join()
            self.assertEqual(A.instance_count, 1)

    def test_required_components_may_be_omitted_from_the_arguments_list_of_required_components(
            self):

        @component
        class A(object):

            def __call__(self):
                return 'A'

        @component
        class B(object):

            def __call__(self):
                return 'B'

        @component
        @requires(a=A)
        @requires(b=B)
        def required_component(a):
            return lambda: a()  # noqa

        @component
        @requires(a=required_component)
        def function_component(a):
            return lambda: a()  # noqa

        self.assertEqual(self.f.call(function_component, scope=self.scope)(), 'A')

    def test_factory_uses_pre_created_instances_when_they_exist_instead_of_instantiating_components(
            self):

        @component(name='PreInstantiated', component_manager=self.component_manager)
        def pre_instantiated():
            raise AssertionError('This should never be called to instantiate the component')

        @requires(p='PreInstantiated')
        def f(p):
            return p

        instance = 'my instance'

        self.assertEqual(
            self.f.call(f, self.scope, pre_instantiated={
                'PreInstantiated': instance
            }), instance)
