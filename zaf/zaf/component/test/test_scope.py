import unittest

from ..factory import _InstanceId
from ..scope import Scope, ScopeError


class TestScope(unittest.TestCase):

    def setUp(self):
        self.scope = Scope('scope')

    def test_find_ancestor_traverses_scope_hierarchy_to_find_scope_with_matching_name(self):
        grand_parent = Scope('grand_parent')
        parent = Scope('parent', grand_parent)
        child = Scope('child', parent)

        self.assertIs(child.find_ancestor('grand_parent'), grand_parent)
        self.assertIs(child.find_ancestor('parent'), parent)
        self.assertIs(child.find_ancestor('child'), child)

    def test_find_ancestor_raises_scope_error_if_no_matching_ancestor_found(self):
        with self.assertRaises(ScopeError):
            self.scope.find_ancestor('not an ancestor')

    def test_hierarchy_gives_a_list_of_the_scope_names_in_hierarchy_order_with_grandest_parent_first(
            self):
        grand_parent = Scope('grand_parent')
        parent = Scope('parent', grand_parent)
        child = Scope('child', parent)

        self.assertEqual(child.hierarchy(), ['grand_parent', 'parent', 'child'])

    def test_scope_may_not_have_same_name_as_ancestor(self):
        with self.assertRaises(ScopeError):
            Scope('scope', parent=self.scope)

    def test_register_the_same_instance_twice_in_the_same_scope_raises_scope_error(self):
        instance_id = _InstanceId(lambda: None, ())
        my_instance = object()
        self.scope.register_instance(instance_id, my_instance)
        with self.assertRaises(ScopeError):
            self.scope.register_instance(instance_id, my_instance)

    def test_get_instance_returns_no_instance_if_no_suitable_instance_exists(self):
        instance_id = _InstanceId(lambda: None, ())
        self.assertIs(self.scope.get_instance(instance_id), Scope.NO_INSTANCE)

    def test_can_get_a_previous_registered_instance(self):
        instance_id = _InstanceId(lambda: None, ())
        my_instance = object()
        self.scope.register_instance(instance_id, my_instance)
        self.assertIs(my_instance, self.scope.get_instance(instance_id))

    def test_can_register_multiple_instances(self):
        instance_id = _InstanceId(lambda: None, ())
        my_instance = object()

        my_other_instance_id = _InstanceId(lambda: None, ())
        my_other_instance = object()

        self.scope.register_instance(instance_id, my_instance)
        self.scope.register_instance(my_other_instance_id, my_other_instance)

        self.assertIs(my_instance, self.scope.get_instance(instance_id))
        self.assertIs(my_other_instance, self.scope.get_instance(my_other_instance_id))
