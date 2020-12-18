import inspect
import logging
from collections import OrderedDict, namedtuple

from ordered_set import OrderedSet

from zaf.component.decorator import Requirement
from zaf.component.scope import ScopeError

logger = logging.getLogger('zaf.component')


class ComponentDependencyError(Exception):
    pass


Reason = namedtuple('Reason', ['short_message', 'message'])


class RequirementNode(object):
    """A node representing an @requires and metadata about the requires."""

    def __init__(self, requires, callables, required):
        self._requires = requires
        self._can = set(requires.can)
        self._callables = callables
        self._not_fulfilled_callables = []
        self._required = required
        self._selection_performed = False
        self._parent_callable = None

    @property
    def callables(self):
        return self._callables

    @callables.setter
    def callables(self, callables):
        self._callables = callables

    @property
    def not_fulfilled_callables(self):
        return self._not_fulfilled_callables

    @property
    def can(self):
        return self._can

    def add_cans(self, cans):
        return self._can.update(cans)

    @property
    def argument(self):
        return self._requires.argument

    @property
    def args(self):
        return self._requires.args

    @property
    def uses(self):
        return self._requires.uses

    @property
    def component(self):
        return self._requires.component

    @property
    def component_name(self):
        if isinstance(self._requires.component, str):
            return self._requires.component
        else:
            return self._requires.component.__name__

    @property
    def instance(self):
        return self._requires.instance

    @property
    def scope_name(self):
        return self._requires.scope_name

    @property
    def fixate_entities(self):
        return self._requires.fixate_entities

    @property
    def required(self):
        """Indicate if this requirement is allowed to be removed."""
        return self._required

    @property
    def selection_performed(self):
        return self._selection_performed

    @selection_performed.setter
    def selection_performed(self, selection_performed):
        self._selection_performed = selection_performed

    def selected(self):
        for callable in self._callables:
            if callable.selected:
                return callable


class InstanceCallableNode(object):
    """A node representing a callable that should be instantiated."""

    def __init__(self, callable, requirements, args, kwargs):
        self.callable = callable
        self.requirements = requirements
        self.args = args
        self.kwargs = kwargs
        self.selected = False
        self.selected_scope = None
        self._fulfilled = True
        self.not_fulfilled_reason = None

    @property
    def name(self):
        return repr(self.callable)

    @property
    def short_name(self):
        return self.callable.__name__

    @property
    def can(self):
        return self.callable._zaf_component_can

    @property
    def priority(self):
        return self.callable._zaf_component_priority

    @property
    def component_name(self):
        return self.callable._zaf_component_name

    @property
    def fulfilled(self):
        return self._fulfilled

    def set_not_fulfilled(self, reason):
        self._fulfilled = False
        self.not_fulfilled_reason = reason


class NonInstanceCallableNode(object):
    """A node representing a callable that should not be instantiated."""

    def __init__(self, callable, requirements):
        self.callable = callable
        self.requirements = requirements
        self.selected = False
        self.selected_scope = None
        self.fulfilled = True

    @property
    def name(self):
        return repr(self.callable)

    @property
    def priority(self):
        return self.callable._zaf_component_priority

    @property
    def short_name(self):
        return self.callable.__name__


class DependencyGraph(object):
    """
    A dependency graph that is used to decide which component to use for each requirement.

    This is built up of alternating RequirementNode and XXXCallableNode.
    The top node is a NonInstanceCallableNode that represents the callable that the user wants
    to call.
    This is linked to requirement nodes for each @requires on the callable.
    Each requirement node contains a list of callable nodes that can be used to fulfill the requirement.

    The different methods can be used to manipulate the graph so that it in the end represents
    selected callables that fulfills each requirements and which scope they should be instantiated in.
    """

    def __init__(self, root):
        self._root = root

    @property
    def root(self):
        return self._root

    def resolve(self, top_level_scope, fixated_entities=None):
        """
        Resolve the dependency graph by selecting callables for each requirement.

        :param top_level_scope: the top level, and thus shortest, scope that is used when
                                evaluating the dependencies
        :param fixated_entities:  Mapping from component name to the fixated entity component
                                  This is used to enforce a specific entity selection for components
                                  with the matching name.
        """
        fixated_entities = fixated_entities if fixated_entities else {}
        self.remove_not_fulfilled()
        self.combine_uses()
        self.select_scopes(top_level_scope=top_level_scope)

        self.remove_not_matching_fixated_entities(fixated_entities)
        self.remove_not_fulfilled()
        self.remove_with_shorter_scope_than_parent(top_level_scope=top_level_scope)

        self.assert_requirements_fulfilled(self._root)
        self.make_selections()

    def combine_uses(self):
        """Combine requirement nodes when using 'uses' to make sure that the same selection is made."""
        return self._recursively_combine_uses(self._root, parent_uses_mapping={})

    def _recursively_combine_uses(self, callable_node, parent_uses_mapping):

        for argument, requirement in callable_node.requirements.items():
            uses_mapping = dict(parent_uses_mapping)
            for use in requirement.uses:
                used_requirement = callable_node.requirements[use]
                if used_requirement.component not in uses_mapping:
                    uses_mapping[self._get_uses_mapping_key(used_requirement)] = used_requirement

            if requirement.component in uses_mapping and uses_mapping[requirement.
                                                                      component] != requirement:
                combined_requirement = uses_mapping[requirement.component]
                logger.debug(
                    (
                        "Combining requirement '{req}' on '{callable}' which can "
                        "'{req_can}' with uses '{uses}' which can '{uses_can}'").format(
                            req=requirement.argument,
                            callable=callable_node.name,
                            req_can=', '.join(requirement.can),
                            uses=combined_requirement.argument,
                            uses_can=', '.join(combined_requirement.can)))

                combined_requirement.add_cans(requirement.can)
                callable_node.requirements[argument] = combined_requirement
            else:
                for callable in requirement.callables:
                    self._recursively_combine_uses(callable, uses_mapping)

    def _get_uses_mapping_key(self, used_requirement):
        map_key = used_requirement.component
        if callable(map_key):
            map_key = map_key._zaf_component_name
        return map_key

    def remove_not_fulfilled(self):
        """
        Remove all nodes in the graph that can't be fulfilled.

        The cause can be that there are no components at all or that the
        available components have the wrong *cans*.
        """
        for requirement in self._root.requirements.values():
            self._recursively_remove(requirement, self._root, CheckRequirements())

    def remove_not_matching_fixated_entities(self, fixated_entities):
        """
        Remove all nodes in the graph that don't match fixated entities.

        :param top_level_scope: the top level, and thus shortest, scope that is used when
                                evaluating the dependencies
        :param fixated_entities:  Mapping from component name to the fixated entity component
        """
        for requirement in self._root.requirements.values():
            self._recursively_remove(requirement, self._root, CheckFixated(fixated_entities))

    def _recursively_remove(self, requirement_node, parent_callable, checker):
        filtered_callables = []
        not_fulfilled_callables = []
        for callable in requirement_node.callables:
            if type(callable) == InstanceCallableNode:
                all_fulfilled = True
                for requirement in callable.requirements.values():
                    self._recursively_remove(requirement, callable, checker)
                    if not requirement.callables:
                        all_fulfilled = False
                        break

                is_fulfilled, reason = checker.is_fulfilled(
                    parent_callable, requirement_node, callable)
                if not is_fulfilled:
                    callable.set_not_fulfilled(reason)
                    not_fulfilled_callables.append(callable)
                elif not all_fulfilled:
                    callable.set_not_fulfilled(Reason('U', 'Unfullfilled requirements'))
                    not_fulfilled_callables.append(callable)
                else:
                    filtered_callables.append(callable)
            else:
                filtered_callables.append(callable)

        requirement_node.callables = filtered_callables
        requirement_node.not_fulfilled_callables.extend(not_fulfilled_callables)

    def assert_requirements_fulfilled(self, top_level_callable):

        fulfilled = True
        for requirement in top_level_callable.requirements.values():
            if not requirement.callables:
                fulfilled = False

        if not fulfilled:
            msg_lines = [
                'Error fulfilling requirements for {name}'.format(
                    name=top_level_callable.short_name)
            ]

            for requirement in top_level_callable.requirements.values():
                msg_lines.extend(self.create_requirement_error_lines(requirement))
            msg = '\n'.join(msg_lines)
            logger.debug(msg)
            raise ComponentDependencyError(msg)

    def create_requirement_error_lines(self, requirement, indentation=''):
        msg_lines = []
        if requirement.callables:
            reason = Reason('F', 'Fulfilled')
        elif requirement.not_fulfilled_callables:
            reason = Reason('U', 'Unfulfilled')
        else:
            reason = Reason(
                'M', "Missing component '{comp}'".format(comp=requirement.component_name))

        cans = " and cans '{cans}'".format(
            cans=', '.join(requirement.can)) if requirement.can else ''
        msg_lines.append(
            "{indentation}{short}: Requirement '{req}' with name '{comp}'{cans}: {reason}".format(
                indentation=indentation,
                short=reason.short_message,
                req=requirement.argument,
                comp=str(requirement.component_name),
                cans=cans,
                reason=reason.message))

        indentation = '{indentation}  '.format(indentation=indentation)
        for callable in requirement.callables:
            msg_lines.append(
                "{indentation}E: Component '{comp}' with name '{name}': Exists".format(
                    indentation=indentation,
                    comp=callable.short_name,
                    name=requirement.component_name))

        for callable in requirement.not_fulfilled_callables:
            msg_lines.append(
                "{indentation}{short}: Component '{comp}' with name '{name}': {reason}".format(
                    indentation=indentation,
                    short=callable.not_fulfilled_reason.short_message,
                    comp=callable.short_name,
                    name=requirement.component_name,
                    reason=callable.not_fulfilled_reason.message))

        indentation += '  '
        for callable in requirement.callables + requirement.not_fulfilled_callables:
            for callable_requirement in callable.requirements.values():
                msg_lines.extend(
                    self.create_requirement_error_lines(callable_requirement, indentation))

        return msg_lines

    def remove_with_shorter_scope_than_parent(self, top_level_scope):
        """
        Remove all nodes in the graph that have a shorter scope than the parent.

        :param top_level_scope: the top level, and thus shortest, scope that is used when
                                evaluating the dependencies
        """
        for requirement in self._root.requirements.values():
            self._recursively_remove(requirement, self._root, CheckScopes(top_level_scope))

    def select_scopes(self, top_level_scope):
        """
        Populate each node in the graph with the selected scope.

        This must be executed before the remove_with_shorter_scope_than_parent
        :param top_level_scope: the top level, and thus shortest, scope that is used when
                                evaluating the dependencies
        """
        self._root.selected_scope = top_level_scope.name
        self._recursively_select_scopes(self._root, top_level_scope.name)

    def _recursively_select_scopes(self, callable_node, parent_scope_name):
        for requirement in callable_node.requirements.values():
            if not requirement.selection_performed:
                for callable in requirement.callables:
                    if callable.selected_scope is None:
                        callable.selected_scope = self._select_scope_for_requirement(
                            requirement.scope_name, callable.callable, parent_scope_name)

                        if requirement.instance:
                            self._recursively_select_scopes(callable, callable.selected_scope)

    def make_selections(self):
        """Select which callable that should be used to fulfill each requirement."""
        self._recursively_make_selections(self._root)

    def _recursively_make_selections(self, callable_node):
        for requirement in callable_node.requirements.values():
            if not requirement.selection_performed:
                selected = sorted(requirement.callables, key=lambda c: c.priority, reverse=True)[0]
                selected.selected = True
                if requirement.instance:
                    self._recursively_make_selections(selected)
                requirement.selection_performed = True

    def _select_scope_for_requirement(self, requires_scope_name, callable, parent_scope_name):
        if requires_scope_name is not None:
            return requires_scope_name
        elif callable._zaf_component_default_scope_name is not None:
            return callable._zaf_component_default_scope_name
        else:
            return parent_scope_name


class CheckRequirements(object):

    def is_fulfilled(self, parent_callable, requirement, callable):
        """Check that a requirement is fulfilled."""
        return requirement.can.issubset(callable.can), Reason(
            'C',
            "Cans not fulfilled '{cans}'".format(
                cans=', '.join(requirement.can.difference(callable.can))))


class CheckScopes(object):
    """
    Check that the scope for a callable is valid.

    A scope is valid if it is part of the scope hierarchy and it the same or longer
    than the selected scope of the parent_callable.
    """

    def __init__(self, top_level_scope):
        self._top_level_scope = top_level_scope

    def is_fulfilled(self, parent_callable, requirement, callable):
        parent_scope = self._top_level_scope.find_ancestor(parent_callable.selected_scope)

        try:
            parent_scope.find_ancestor(callable.selected_scope)
            return True, None
        except ScopeError:
            return False, Reason(
                'S', "Scope '{scope}' is not one of the valid scopes '{valid_scopes}'".format(
                    scope=callable.selected_scope,
                    valid_scopes=', '.join(parent_scope.hierarchy())))


class CheckFixated(object):
    """
    Check that the scope for a callable is valid.

    A scope is valid if it is part of the scope hierarchy and it the same or longer
    than the selected scope of the parent_callable.
    """

    def __init__(self, fixated_entities):
        self._fixated_entities = fixated_entities

    def is_fulfilled(self, parent_callable, requirement, callable):
        name = requirement.component_name
        if (requirement.fixate_entities and name in self._fixated_entities
                and getattr(callable.callable, 'entity', '') != self._fixated_entities[name]):

            return False, Reason(
                'E',
                "Fixated on another component entity '{entity}'".format(
                    entity=self._fixated_entities[name]))
        else:
            return True, None


class DependencyGraphBuilder(object):
    """Builds the dependency graph from all registered components."""

    def __init__(self, component_registry):
        self._component_registry = component_registry

    def create_dependency_graph(self, callable, top_level_scope, extra_req, *args, **kwargs):
        return DependencyGraph(
            self._recursively_create_nodes(
                callable, top_level_scope, args, kwargs, extra_req=extra_req))

    def _recursively_create_nodes(
            self,
            callable,
            top_level_scope,
            args,
            kwargs,
            is_top_level=True,
            instantiate=False,
            extra_req=None):
        requirement_nodes = OrderedDict()
        for requires in self._get_requires(callable, extra_req):
            callables = self._translate_requirement_to_callables(requires)
            callable_nodes = [
                self._recursively_create_nodes(
                    child_callable,
                    top_level_scope,
                    requires.args, {},
                    is_top_level=False,
                    instantiate=requires.instance,
                    extra_req=None) for child_callable in callables
            ]
            requirement_nodes[requires.argument] = RequirementNode(
                requires=requires, callables=callable_nodes, required=is_top_level)

        if instantiate:
            return InstanceCallableNode(
                callable=callable, requirements=requirement_nodes, args=args, kwargs=kwargs)
        else:
            return NonInstanceCallableNode(callable=callable, requirements=requirement_nodes)

    def _get_requires(self, callable, extra_req):
        requires = OrderedSet(self._get_explicit_requires(callable, extra_req))
        requires.update(OrderedSet(self._get_implicit_requires(callable)))
        return requires

    def _get_implicit_requires(self, fn):
        """
        Return a list of implicit requirements associated with a function or class.

        Implicit requirements are requirements that have been named as part of the
        parameters list of a function. Instances of required components can not be
        requested using this mechanism.

        .. code-block:: python

            @component
            class MyComponent(object):
                pass

            def my_function(MyComponent):
                pass  # ... do something with the MyComponent class

        .. code-block:: python

            @component
            def my_component():
                pass

            def my_function(my_component):
                pass  # ... do something with the my_component function

        Returns the empty list if there are no such requirements.
        """

        def find_implicit_requires():
            for argument in inspect.signature(fn).parameters:
                for component in self._component_registry.keys():
                    if argument.lower() == component.lower():
                        yield argument, component

        return [
            Requirement.make_requirement(argument, component, False)
            for argument, component in find_implicit_requires()
        ]

    def _get_explicit_requires(self, item, extra_req):
        """
        Return a list of explicit requirement associated with a function or class.

        Explicit requirements are requirements that have been provided in advance
        using the @requires decorator, or passed on as extra requirements from
        other sources.

        Returns the empty list if there are no such requirements.
        """
        requirements = list(item._zaf_requirements if hasattr(item, '_zaf_requirements') else [])
        if extra_req:
            requirements.extend(extra_req)
        if not len(set(requirements)) == len(requirements):
            raise ComponentDependencyError('Explicit requirements may not share the same name.')
        return requirements

    def _translate_requirement_to_callables(self, require):
        if isinstance(require.component, str):
            return self._component_registry[require.component]
        elif callable(require.component):
            return [require.component]
        raise ComponentDependencyError(
            "Component '{comp}' is of invalid type. Components must be named or callable.".format(
                comp=repr(require.component)))
