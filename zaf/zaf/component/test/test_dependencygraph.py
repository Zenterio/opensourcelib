import unittest
from textwrap import dedent

from zaf.component.decorator import Requirement, component, requires
from zaf.component.dependencygraph import ComponentDependencyError, DependencyGraphBuilder, \
    NonInstanceCallableNode
from zaf.component.manager import ComponentManager, create_entity_map, create_registry
from zaf.component.scope import Scope


class TestCreateDependencyGraphBuilder(unittest.TestCase):

    def setUp(self):
        self.component_manager = ComponentManager(create_registry(), create_entity_map())
        self.registry = self.component_manager.COMPONENT_REGISTRY
        self.builder = DependencyGraphBuilder(self.registry)
        self.scope = Scope('scope')

    def test_create_a_two_level_dependency_graph(self):

        @component(name='A', component_manager=self.component_manager)
        def a1():
            pass

        @component(name='A', component_manager=self.component_manager)
        def a2():
            pass

        @requires(a='A')
        def test(a):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['a'].argument, 'a')
        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[1].callable.__name__, 'a2')

    def test_create_a_three_level_dependency_graph(self):

        @component(name='A', component_manager=self.component_manager)
        def a1():
            pass

        @component(name='A', component_manager=self.component_manager)
        def a2():
            pass

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A')
        def b12(a):
            pass

        @component(name='B', component_manager=self.component_manager)
        @requires(a1=a1)
        def b1(a1):
            pass

        @component(name='B', component_manager=self.component_manager)
        @requires(a2=a2)
        def b2(a2):
            self.name = 'a2'

        @requires(b='B')
        def test(b):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['b'].argument, 'b')
        requirement = dependency_graph._root.requirements['b']
        self.assertEqual(requirement.callables[0].callable.__name__, 'b12')
        self.assertEqual(requirement.callables[1].callable.__name__, 'b1')
        self.assertEqual(requirement.callables[2].callable.__name__, 'b2')
        callable0 = requirement.callables[0]
        callable1 = requirement.callables[1]
        callable2 = requirement.callables[2]
        self.assertEqual(callable0.requirements['a'].argument, 'a')
        self.assertEqual(callable0.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertEqual(callable0.requirements['a'].callables[1].callable.__name__, 'a2')
        self.assertEqual(callable1.requirements['a1'].argument, 'a1')
        self.assertEqual(callable1.requirements['a1'].callables[0].callable.__name__, 'a1')
        self.assertEqual(callable2.requirements['a2'].argument, 'a2')
        self.assertEqual(callable2.requirements['a2'].callables[0].callable.__name__, 'a2')

    def test_create_dependency_graph_ends_when_reaching_instance_false(self):

        @component(name='A', component_manager=self.component_manager)
        def a():
            pass

        @component(name='B', component_manager=self.component_manager)
        @requires(a='A')
        def b(a):
            pass

        @requires(b='B', instance=False)
        def test(b):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['b'].argument, 'b')
        requirement = dependency_graph._root.requirements['b']
        self.assertEqual(type(requirement.callables[0]), NonInstanceCallableNode)

    def test_filter_out_not_fulfilled_when_can_is_not_fulfilled(self):

        @component(name='A', can=['1'], component_manager=self.component_manager)
        def a1():
            pass

        @component(name='A', can=['2'], component_manager=self.component_manager)
        def a2():
            pass

        @requires(a='A', can=['1'])
        def test(a):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        dependency_graph.remove_not_fulfilled()

        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['a'].argument, 'a')
        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertEqual(len(dependency_graph._root.requirements['a'].callables), 1)

    def test_filter_out_not_fulfilled_when_can_is_not_fullfilled_in_uses(self):

        @component(name='A', can=['2'], component_manager=self.component_manager)
        def a():
            pass

        @component(name='B', can=['1'], component_manager=self.component_manager)
        @requires(a='A', can=['1'])
        def b1(a):
            pass

        @component(name='B', can=['2'], component_manager=self.component_manager)
        @requires(a='A', can=['2'])
        def b2(a):
            pass

        @component(name='C', component_manager=self.component_manager)
        @requires(b='B')
        def c(b):
            pass

        @requires(a='A')
        @requires(c='C', uses=['a'])
        def test(a, c):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        dependency_graph.resolve(self.scope)

    def test_uses_works_with_callable_components(self):

        @component(name='C', can=['C1'], component_manager=self.component_manager)
        def c1():
            pass

        @component(name='C', can=['C2'], component_manager=self.component_manager)
        def c2():
            pass

        @component(name='SuperC', component_manager=self.component_manager)
        @requires(c='C')
        def superc(c):
            pass

        @component(name='MasterC', component_manager=self.component_manager)
        @requires(sc='SuperC')
        def masterc(sc):
            pass

        @requires(c=c2)
        @requires(mc='MasterC', uses=['c'])
        def test(c, mc):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        dependency_graph.resolve(self.scope)
        mc_callable_node = dependency_graph.root.requirements['mc'].callables[0]
        sc_callable_node = mc_callable_node.requirements['sc'].callables[0]
        c_callable_node = sc_callable_node.requirements['c'].callables[0]
        self.assertEqual(c_callable_node.callable, c2)

    def test_filter_out_not_fulfilled_when_no_component_exist_for_name(self):

        @component(name='A', component_manager=self.component_manager)
        def a1():
            pass

        @component(name='A', component_manager=self.component_manager)
        @requires(not_exists='DoesNotExist')
        def a2(not_exists):
            pass

        @requires(a='A')
        def test(a):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        dependency_graph.remove_not_fulfilled()

        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['a'].argument, 'a')
        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertEqual(len(dependency_graph._root.requirements['a'].callables), 1)

    def test_filter_out_component_with_shorter_scope_than_parent(self):

        @component(name='A', scope='long', component_manager=self.component_manager)
        def a1():
            pass

        @component(name='A', scope='short', component_manager=self.component_manager)
        def a2():
            pass

        @component(name='B', scope='long', component_manager=self.component_manager)
        @requires(a='A')
        def b():
            pass

        @requires(b='B')
        def test(b):
            pass

        long = Scope('long')
        short = Scope('short', parent=long)

        dependency_graph = self.builder.create_dependency_graph(test, short, None)
        dependency_graph.select_scopes(short)
        dependency_graph.remove_with_shorter_scope_than_parent(short)

        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['b'].argument, 'b')
        callable_b = dependency_graph._root.requirements['b'].callables[0]
        self.assertEqual(callable_b.callable.__name__, 'b')
        self.assertEqual(callable_b.requirements['a'].argument, 'a')
        self.assertEqual(callable_b.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertEqual(len(callable_b.requirements['a'].callables), 1)

    def test_filter_out_component_not_matching_fixated_entity(self):

        @component(name='A', component_manager=self.component_manager)
        class a1():
            entity = 'a1'

        @component(name='A', component_manager=self.component_manager)
        class a2():
            entity = 'a2'

        @requires(a='A')
        def test(a):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        dependency_graph.remove_not_matching_fixated_entities({'A': 'a1'})

        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['a'].argument, 'a')

        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertEqual(len(dependency_graph._root.requirements['a'].callables), 1)

    def test_requires_with_fixate_entities_false_will_not_filter_out_entities(self):

        @component(name='A', component_manager=self.component_manager)
        class a1():
            entity = 'a1'

        @component(name='A', component_manager=self.component_manager)
        class a2():
            entity = 'a2'

        @requires(a='A', fixate_entities=False)
        def test(a):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        dependency_graph.remove_not_matching_fixated_entities({'A': 'a1'})

        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['a'].argument, 'a')

        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[1].callable.__name__, 'a2')
        self.assertEqual(len(dependency_graph._root.requirements['a'].callables), 2)

    def test_error_message_when_remove_with_shorter_scope(self):

        @component(
            name='A',
            can=['stuff', 'other_stuff'],
            scope='short',
            component_manager=self.component_manager)
        def component_a_scope():
            pass

        @component(name='A', can=['no_stuff'], component_manager=self.component_manager)
        def component_a_cans():
            pass

        @component(name='A', can=['stuff', 'other_stuff'], component_manager=self.component_manager)
        @requires(require_not_exists='NotExists')
        def component_a_depends(require_not_exists):
            pass

        @component(name='B', scope='long', component_manager=self.component_manager)
        @requires(require_a='A', can=['stuff', 'other_stuff'])
        def component_b(require_a):
            pass

        @component(
            name='C', can=['stuff2', 'stuff3', 'stuff4'], component_manager=self.component_manager)
        def component_c():
            pass

        @component(name='D', component_manager=self.component_manager)
        @requires(require_c='C', can=['stuff2', 'stuff3'])
        def component_d(require_c):
            pass

        @requires(require_b='B')
        @requires(require_d=component_d)
        def test(require_b, require_d):
            pass

        long = Scope('long')
        short = Scope('short', parent=long)

        dependency_graph = self.builder.create_dependency_graph(test, short, None)
        expected_message = dedent(
            """\
            Error fulfilling requirements for test
            U: Requirement 'require_b' with name 'B': Unfulfilled
              U: Component 'component_b' with name 'B': Unfullfilled requirements
                U: Requirement 'require_a' with name 'A' and cans 'stuff, other_stuff': Unfulfilled
                  C: Component 'component_a_cans' with name 'A': Cans not fulfilled 'stuff, other_stuff'
                  U: Component 'component_a_depends' with name 'A': Unfullfilled requirements
                    M: Requirement 'require_not_exists' with name 'NotExists': Missing component 'NotExists'
                  S: Component 'component_a_scope' with name 'A': Scope 'short' is not one of the valid scopes 'long'
            F: Requirement 'require_d' with name 'component_d': Fulfilled
              E: Component 'component_d' with name 'component_d': Exists
                F: Requirement 'require_c' with name 'C': Fulfilled
                  E: Component 'component_c' with name 'C': Exists""")

        with self.assertRaises(ComponentDependencyError) as exc:
            dependency_graph.resolve(short)
            self.assertEqual(str(exc), expected_message)

    def test_make_selection_selects_the_component_with_the_highest_priority(self):

        @component(name='A', priority=1, component_manager=self.component_manager)
        class a1():
            entity = 'a1'

        @component(name='A', priority=2, component_manager=self.component_manager)
        class a2():
            entity = 'a2'

        @component(name='A', priority=0, component_manager=self.component_manager)
        class a3():
            entity = 'a3'

        @requires(a='A')
        def test(a):
            pass

        dependency_graph = self.builder.create_dependency_graph(test, self.scope, None)
        dependency_graph.make_selections()

        self.assertEqual(dependency_graph._root.callable, test)
        self.assertEqual(dependency_graph._root.requirements['a'].argument, 'a')

        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[0].callable.__name__, 'a1')
        self.assertFalse(dependency_graph._root.requirements['a'].callables[0].selected)

        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[1].callable.__name__, 'a2')
        self.assertTrue(dependency_graph._root.requirements['a'].callables[1].selected)

        self.assertEqual(
            dependency_graph._root.requirements['a'].callables[2].callable.__name__, 'a3')
        self.assertFalse(dependency_graph._root.requirements['a'].callables[2].selected)

    def test_extra_req(self):

        @component(name='Comp', component_manager=self.component_manager)
        def comp():
            pass

        def test(c):
            pass

        extra_req = [Requirement(c=comp)]
        dependency_graph = self.builder.create_dependency_graph(test, self.scope, extra_req)
        dependency_graph.resolve(self.scope)
        req = dependency_graph._root.requirements['c']
        self.assertEqual(req.component, comp)


class TestBuilderGetRequires(unittest.TestCase):

    def setUp(self):
        component_manager = ComponentManager()
        component_manager.clear_component_registry()
        self.registry = component_manager.COMPONENT_REGISTRY
        self.builder = DependencyGraphBuilder(self.registry)

    def test_get_explicit_requires_with_no_requirements_preset(self):
        item = lambda: None  # noqa
        self.assertEqual(self.builder._get_explicit_requires(item, None), [])

    def test_get_explicit_requires_with_requirements_present(self):
        item = lambda: None  # noqa
        my_requirements = [1, 2, 3]
        item._zaf_requirements = my_requirements
        self.assertEqual(self.builder._get_explicit_requires(item, None), my_requirements)

    def test_get_explicit_requires_with_only_extra_requirements(self):
        item = lambda: None  # noqa
        extra_req = [1]
        self.assertEqual(self.builder._get_explicit_requires(item, extra_req), extra_req)

    def test_get_explicit_requires_with_requirements_and_extra_requirements_present(self):
        item = lambda: None  # noqa
        my_requirements = [1, 2, 3]
        item._zaf_requirements = my_requirements
        extra_req = [4]
        self.assertEqual(
            self.builder._get_explicit_requires(item, extra_req), my_requirements + extra_req)
