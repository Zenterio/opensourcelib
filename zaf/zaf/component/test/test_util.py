import unittest
from contextlib import contextmanager

from ..util import ComponentPropertyError, add_cans, add_properties, is_context_manager, \
    is_generator


def construct_function_component(self):
    return lambda: None  # noqa


def construct_class_component(self):

    class MyComponent(object):
        pass

    return MyComponent


class _AddCans(unittest.TestCase):

    def setUp(self):
        self.c = self.construct_component()

    def test_add_cans_to_a_component_without_previous_cans(self):
        cans = ('capability_a', )
        add_cans(self.c, cans)
        self.assertEqual(self.c._zaf_component_can, set(cans))

    def test_add_cans_as_single_string(self):
        # common programming mistake - missing a comma will make this a string
        # instead of a single item tuple.
        cans = ('capability_a')
        add_cans(self.c, cans)
        self.assertEqual(self.c._zaf_component_can, {cans})

    def test_add_multiple_cans_to_a_component_without_previous_cans(self):
        cans = (
            'capability_a',
            'capability_b',
        )
        add_cans(self.c, cans)
        self.assertEqual(self.c._zaf_component_can, set(cans))

    def test_add_cans_to_a_component_with_previous_cans(self):
        add_cans(self.c, ('capability_a', ))
        add_cans(self.c, ('capability_b', ))
        self.assertEqual(self.c._zaf_component_can, {'capability_a', 'capability_b'})


class TestAddCansToFunctionComponent(_AddCans):
    construct_component = construct_function_component


class TestAddCansToClassComponent(_AddCans):
    construct_component = construct_class_component


class _AddProperties(unittest.TestCase):

    def setUp(self):
        self.c = self.construct_component()

    def test_add_properties_to_component(self):
        add_properties(self.c, 'my_namespace', {'key': 'value'})
        self.assertEqual(self.c.my_namespace.key, 'value')

    def test_add_additional_properties_component(self):
        add_properties(self.c, 'my_namespace', {'key': 'value'})
        add_properties(self.c, 'my_other_namespace', {'other_key': 'other_value'})
        self.assertEqual(self.c.my_namespace.key, 'value')
        self.assertEqual(self.c.my_other_namespace.other_key, 'other_value')

    def test_add_additional_properties_to_existing_namespace(self):
        add_properties(self.c, 'my_namespace', {'key': 'value'})
        print(self.c.my_namespace.__dict__)
        add_properties(self.c, 'my_namespace', {'other_key': 'other_value'})
        print(self.c.my_namespace.__dict__)
        self.assertEqual(self.c.my_namespace.key, 'value')
        self.assertEqual(self.c.my_namespace.other_key, 'other_value')

    def test_can_not_override_existing_properties(self):
        add_properties(self.c, 'my_namespace', {'key': 'value'})
        with self.assertRaises(ComponentPropertyError):
            add_properties(self.c, 'my_namespace', {'key': 'other_value'})

    def test_can_not_add_properties_to_a_non_namespace(self):
        self.c.my_namespace = object()
        with self.assertRaises(ComponentPropertyError):
            add_properties(self.c, 'my_namespace', {'key': 'other_value'})


class TestAddPropertiesToFunctionComponent(_AddProperties):
    construct_component = construct_function_component


class TestAddPropertiesToClassComponent(_AddProperties):
    construct_component = construct_class_component


class TestIsGenerator(unittest.TestCase):

    def test_thing_is_not_a_generator(self):
        self.assertFalse(is_generator(None))

    def test_thing_is_a_generator(self):
        self.assertTrue(is_generator((None for _ in [])))


class TestIsContextManager(unittest.TestCase):

    class MyContextManager(object):

        def __enter__(self):
            pass

        def __exit__(self, *args, **kwargs):
            pass

    def test_thing_is_a_context_manager_object(self):
        self.assertTrue(is_context_manager(TestIsContextManager.MyContextManager()))

    def test_that_a_class_is_not_a_context_manager(self):
        self.assertFalse(is_context_manager(TestIsContextManager.MyContextManager))

    def test_thing_is_a_contextlib_contextmanager(self):

        @contextmanager
        def my_context_manager():
            yield

        self.assertTrue(is_context_manager(my_context_manager()))

    def test_thing_is_not_a_contextmanager(self):
        self.assertFalse(is_context_manager(lambda: None))
