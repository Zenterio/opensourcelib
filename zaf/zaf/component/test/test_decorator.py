import unittest

from ..decorator import Requirement, component, requires
from ..manager import ComponentManager, create_entity_map, create_registry


class TestComponentDecorator(unittest.TestCase):

    def setUp(self):
        self.component_manager = ComponentManager(create_registry(), create_entity_map())

    def test_can_be_used_without_arguments(self):

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        self.assertIn(my_component, self.component_manager.COMPONENT_REGISTRY['my_component'])

    def test_can_be_called_without_arguments(self):

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        self.assertIn(my_component, self.component_manager.COMPONENT_REGISTRY['my_component'])

    def test_components_can_be_given_a_name(self):

        @component(name='my_custom_name', component_manager=self.component_manager)
        def my_component():
            pass

            self.assertIn(my_component, self.component_manager.COMPONENT_REGISTRY['my_custom_name'])

    def test_multiple_components_can_share_a_name(self):
        my_components = []

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        my_components.append(my_component)

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        my_components.append(my_component)

        self.assertEqual(
            set(my_components), set(self.component_manager.COMPONENT_REGISTRY['my_component']))

    def test_multiple_named_components_can_share_a_name(self):

        @component(name='my_custom_name', component_manager=self.component_manager)
        def my_first_component():
            pass

        @component(name='my_custom_name', component_manager=self.component_manager)
        def my_second_component():
            pass

        my_components = [my_first_component, my_second_component]
        self.assertEqual(
            set(my_components), set(self.component_manager.COMPONENT_REGISTRY['my_custom_name']))

    def test_can_be_called_without_arguments_when_used_with_a_class(self):

        @component(component_manager=self.component_manager)
        class MyClass(object):
            pass

        self.assertIn(MyClass, self.component_manager.COMPONENT_REGISTRY['MyClass'])

    def test_can_be_called_with_arguments_when_used_with_a_class(self):

        @component(name='MyCustomName', component_manager=self.component_manager)
        class MyClass(object):
            pass

        self.assertIn(MyClass, self.component_manager.COMPONENT_REGISTRY['MyCustomName'])

    def test_if_no_scope_is_provided_the_default_scope_is_none(self):

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        self.assertIsNone(my_component._zaf_component_default_scope_name)

    def test_providing_a_scope(self):

        @component(scope='session', component_manager=self.component_manager)
        def my_component():
            pass

        self.assertEqual(my_component._zaf_component_default_scope_name, 'session')

    def test_can_is_default_none(self):

        @component(component_manager=self.component_manager)
        def my_component():
            pass

        self.assertEqual(my_component._zaf_component_can, set())

    def test_can_can_be_set(self):

        @component(can=['A', 'B', 'C'], component_manager=self.component_manager)
        def my_component():
            pass

        self.assertEqual(my_component._zaf_component_can, {'A', 'B', 'C'})


class TestRequirement(unittest.TestCase):

    def test_initialize(self):
        r = Requirement(argument='component', instance=False)
        self.assertEqual(r.argument, 'argument')
        self.assertEqual(r.component, 'component')
        self.assertFalse(r.instance)
        self.assertIsNone(r.scope_name)

    def test_initialize_as_instance(self):
        r = Requirement(argument='component', scope='class')
        self.assertEqual(r.argument, 'argument')
        self.assertEqual(r.component, 'component')
        self.assertTrue(r.instance)
        self.assertEqual(r.scope_name, 'class')

    def test_initialize_with_can(self):
        r = Requirement(argument='component', scope='session', can=['A', 'B', 'C'])
        self.assertEqual(r.argument, 'argument')
        self.assertEqual(r.component, 'component')
        self.assertTrue(r.instance)
        self.assertEqual(r.scope_name, 'session')
        self.assertEqual(r.can, {'A', 'B', 'C'})

    def test_make_requirement(self):
        r = Requirement.make_requirement('argument', 'component', True, 'module')
        self.assertIsInstance(r, Requirement)
        self.assertEqual(r.argument, 'argument')
        self.assertEqual(r.component, 'component')
        self.assertTrue(r.instance)
        self.assertEqual(r.scope_name, 'module')

    def test_repr_produced_a_string(self):
        r = Requirement.make_requirement('argument', 'component', True)
        self.assertIn('Requirement', r.__repr__())


class TestRequiresDecorator(unittest.TestCase):

    def setUp(self):
        self.component_manager = ComponentManager(create_registry(), create_entity_map())

    def test_component_can_have_a_single_requirement(self):

        @component(component_manager=self.component_manager)
        @requires(x='my_requirement', instance=False)
        def my_component(x):
            pass

        expected_requirements = [Requirement(x='my_requirement')]
        self.assertEqual(expected_requirements, my_component._zaf_requirements)

    def test_component_can_have_multiple_requirements(self):

        @component(component_manager=self.component_manager)
        @requires(y='my_other_requirement', instance=False)
        @requires(x='my_requirement', instance=False)
        def my_component(x):
            pass

        expected_requirements = [
            Requirement(y='my_other_requirement'),
            Requirement(x='my_requirement')
        ]
        self.assertEqual(
            expected_requirements, self.component_manager.COMPONENT_REGISTRY['my_component'][0]
            ._zaf_requirements)

    def test_requires_decorator_may_come_before_component_decorator(self):

        @requires(x='my_requirement', instance=False)
        @component(component_manager=self.component_manager)
        def my_component(x):
            pass

        expected_requirements = [Requirement(x='my_requirement')]
        self.assertEqual(
            expected_requirements, self.component_manager.COMPONENT_REGISTRY['my_component'][0]
            ._zaf_requirements)
