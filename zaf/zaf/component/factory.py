import inspect
import logging
from collections import OrderedDict, namedtuple

from zaf.component.decorator import component
from zaf.component.dependencygraph import DependencyGraphBuilder

from .scope import Scope
from .util import is_context_manager, is_generator

logger = logging.getLogger('zaf.component.factory')

_InternalInstanceId = namedtuple('_InternalInstanceId', ['callable', 'args', 'kwargs'])


class _InstanceId(_InternalInstanceId):

    __slots__ = ()

    def __new__(cls, callable, args=(), kwargs=None):
        if not kwargs:
            kwargs = {}
        return super().__new__(cls, callable, args, kwargs)


class ExitScopeResult(object):

    def __init__(self, scope, success, exceptions):
        self.scope = scope
        self.success = success
        self.exceptions = exceptions

    def combine(self, other_result):
        self.success = self.success and other_result.success
        self.exceptions.extend(other_result.exceptions)


class ComponentInstanceException(Exception):
    pass


class CallableInformation(object):

    def __init__(self, callable):
        self._callable = callable
        self.args = None
        self.kwargs = None

    @property
    def callable(self):
        """Get the callable that the component was instantiated for."""
        return self._callable

    @property
    def name(self):
        """Get the name of the callable."""
        return self._callable.__name__

    @property
    def qualname(self):
        """Get the qualified name of the callable."""
        return '{module}.{qualname}'.format(
            module=self._callable.__module__, qualname=self._callable.__qualname__)


@component(name='ComponentContext')
class ComponentContext(object):
    """
    The context in which the component is instantiated.

    This can be used to get information about when the component was instantiated.
    For example the name of the callable that is going to be run.
    """

    def __init__(self, callable_information):
        self._callable_information = callable_information

    @property
    def callable(self):
        """Get the callable that the component was instantiated for."""
        return self._callable_information.callable

    @property
    def args(self):
        """
        Get the positional arguments that the callable are called with.

        NOTE: This is only available after the callable has been called.
              This means that this is not available in __init__ or context
              manager __enter__ for dependent components.
        """
        return self._callable_information.args

    @property
    def kwargs(self):
        """
        Get the keyword arguments that the callable are called with.

        NOTE: This is only available after the callable has been called.
              This means that this is not available in __init__ or context
              manager __enter__ for dependent components.
        """
        return self._callable_information.kwargs

    @property
    def callable_name(self):
        """Get the name of the callable that the component was instantiated for."""
        return self._callable_information.name

    @property
    def callable_qualname(self):
        """Get the qualified name of the callable that the component was instantiated for."""
        return self._callable_information.qualname

    def __eq__(self, other):
        return isinstance(other, ComponentContext)


class Factory(object):

    def __init__(self, component_manager):
        self._component_manager = component_manager
        self._builder = DependencyGraphBuilder(component_manager.COMPONENT_REGISTRY)

    def call(
            self,
            callable,
            scope,
            *args,
            fixated_entities=None,
            extra_req=None,
            pre_instantiated=None,
            **kwargs):
        """
        Call a callable with a scope.

        This will find and instantiate components related to the callable.

        :param callable: the callable to call
        :param scope: the scope to use to instantiate components
        :param args: the args to call the callable with
        :param kwargs: the kwargs to call the callable with
        :param fixated_entities: List of entities that must be selected
                                 for matching entity components or None
        :param extra_req: List (or None) of extra requirements in addition to
                          those declared on the callable.
        :param pre_instantiated: dict (or None) from name to pre-created
                                 instance that should be used instead of trying to
                                 instantiate the component inside the factory
        :return: the return value of the call to the callable
        """
        fixated_entities = [] if fixated_entities is None else fixated_entities
        pre_instantiated = {} if pre_instantiated is None else pre_instantiated
        dependency_graph = self._builder.create_dependency_graph(
            callable, scope, extra_req, *args, **kwargs)
        fixated_entity_mapping = self._component_manager.component_name_to_entity_mapping(
            fixated_entities)

        dependency_graph.resolve(top_level_scope=scope, fixated_entities=fixated_entity_mapping)

        callable_information = CallableInformation(callable)
        kwargs = dict(kwargs)
        instances = self.instantiate(
            dependency_graph, scope, callable_information, pre_instantiated)
        kwargs.update(instances)

        kwargs = self._strip_unused_kwargs(callable, kwargs)

        callable_information.args = args
        callable_information.kwargs = kwargs
        return callable(*args, **kwargs)

    def enter_scope(self, scope, parent=None, data=None):
        """
        Enter scope just creates a new sub scope.

        This doesn't trigger any component instantiations so it's safe to use at any time.

        :param scope: the name of the scope
        :param parent: the parent scope. Can be None for the top scope
        :param data: scope data that can be anything
        :return: the new scope object
        """
        return Scope(scope, parent, data)

    def exit_scope(self, scope):
        """
        Exit a scope, and active sub scopes, and exits all components on the scope.

        :param scope: the scope to exit
        :return: an ExitScopeResult object with information about the result
        """
        result = ExitScopeResult(scope.parent, True, [])

        for instance_id, context in scope.contexts():
            logger.debug(
                'Exiting scope {scope} for component {component}'.format(
                    scope=scope.name, component=instance_id.callable.__name__))
            try:
                if is_generator(context):
                    try:
                        next(context)
                    except StopIteration:
                        pass
                if is_context_manager(context):
                    context.__exit__(None, None, None)
            except Exception as e:
                logger.error(
                    'Error occurred when exiting scope {scope} for component {component}: {msg}'.
                    format(scope=scope.name, component=instance_id.callable.__name__, msg=str(e)))
                logger.debug(
                    'Error occurred when exiting scope {scope} for component {component}: {msg}'.
                    format(scope=scope.name, component=instance_id.callable.__name__, msg=str(e)),
                    exc_info=True)
                result.success = False
                result.exceptions.append(e)

        return result

    def instantiate(self, dependency_graph, scope, callable_information, pre_instantiated):
        """
        Instantiate all the selected components in the graph.

        :param dependency_graph: The complete dependency graph
        :param scope: the scope to use when instantiating components
        :param callable_information: Information about the top level callable
        :param pre_instantiated: dict mapping from component name to pre-created
                                 component instances
        """
        return self._instantiate_requirements_for_callable(
            dependency_graph.root, scope, callable_information, pre_instantiated)

    def _strip_unused_kwargs(self, callable, kwargs):
        signature = inspect.signature(callable)
        splat_arguments = (
            inspect._VAR_KEYWORD,
            inspect._VAR_POSITIONAL,
        )
        if not any(filter(lambda p: p.kind in splat_arguments, signature.parameters.values())):
            for k in list(kwargs.keys()):
                if k not in signature.parameters:
                    kwargs.pop(k)
        return kwargs

    def _instantiate_requirements_for_callable(
            self, callable_node, scope, callable_information, pre_instantiated):
        """
        Instantiate the selected callable for each of the requirements for the callable using the scope.

        :param callable_node: the callable to instantiate the requirements for
        :param scope: the scope to use when instantiating components
        :param callable_information: Information about the top level callable
        :param pre_instantiated: dict mapping from component name to pre-created
                                 component instances
        :return: a dict from the argument name to the instantiated component
        """
        kwargs = OrderedDict()
        for argument, requirement in self._sort_requirements_in_scope_order(
                callable_node.requirements, scope).items():
            kwargs[argument] = self._recursively_instantiate(
                requirement, scope, callable_node, callable_information, pre_instantiated)
        return self._strip_unused_kwargs(callable_node.callable, kwargs)

    def _recursively_instantiate(
            self, requirement, parent_scope, parent_callable, callable_information,
            pre_instantiated):
        callable = requirement.selected()
        selected_instantiation_scope = parent_scope.find_ancestor(callable.selected_scope)

        if not requirement.instance:
            return callable.callable
        else:
            kwargs = self._instantiate_requirements_for_callable(
                callable, selected_instantiation_scope, callable_information, pre_instantiated)

            try:
                return self._get_instance(
                    callable.callable, selected_instantiation_scope, requirement.args, kwargs,
                    requirement.argument, parent_callable, callable_information, pre_instantiated,
                    callable.component_name)
            except Exception as e:
                raise ComponentInstanceException(
                    "Error occurred when instantiating '{comp}' for requirement '{req}' on '{name}': {msg}".
                    format(
                        comp=callable.name,
                        req=requirement.argument,
                        name=parent_callable.name,
                        msg=str(e))) from e

    def _get_instance(
            self, callable_to_instantiate, scope, args, kwargs, argument_name, parent_callable,
            callable_information, pre_instantiated, component_name):

        def prepare_instance(context):
            if is_generator(context):
                return next(context)
            if is_context_manager(context):
                try:
                    return context.__enter__()
                except Exception as e:
                    context.__exit__(type(e), e, e.__traceback__)
                    raise e
            return context

        def find_or_create_instance():
            instance_id = _InstanceId(callable_to_instantiate, args, kwargs)

            with scope.instantiation_lock(instance_id):
                instance = scope.get_instance(instance_id)
                if instance == Scope.NO_INSTANCE:
                    logger.debug(
                        "Instantiating '{comp}' for requirement '{req}' on '{name}' in scope '{scope}'".
                        format(
                            comp=callable_to_instantiate.__name__,
                            req=argument_name,
                            name=parent_callable.name,
                            scope=scope.name))
                    context = callable_to_instantiate(*args, **kwargs)
                    instance = prepare_instance(context)
                    scope.register_instance(instance_id, instance)
                    scope.register_context(instance_id, context)
                else:
                    logger.debug(
                        "Existing component instance of '{instance}' found for "
                        "requirement '{req}' on '{name}' in scope '{scope}'".format(
                            instance=callable_to_instantiate.__name__,
                            req=argument_name,
                            name=parent_callable.name,
                            scope=scope.name))
            return instance

        # Special handling of Context components because
        # it needs state from the factory
        if callable_to_instantiate == ComponentContext:
            return ComponentContext(callable_information)
        elif component_name in pre_instantiated:
            return pre_instantiated[component_name]
        else:
            return find_or_create_instance()

    def _sort_requirements_in_scope_order(self, requirements, scope):

        def ordering(req_arg_val_tuple):
            _, requirement = req_arg_val_tuple
            return scope.hierarchy().index(requirement.selected().selected_scope)

        return OrderedDict(sorted(requirements.items(), key=ordering))
