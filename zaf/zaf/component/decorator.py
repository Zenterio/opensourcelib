from .manager import ComponentManager
from .util import add_cans


def component(
        name=None, scope=None, can=None, provided_by_extension=None, priority=0,
        component_manager=None):
    """Decorate with @component to indicate that a function or a class is a component."""

    def register_component(fn, component_manager=component_manager):
        fn._zaf_component_name = name if name else fn.__name__
        fn._zaf_component_default_scope_name = scope
        fn._zaf_component_extension = provided_by_extension
        fn._zaf_component_priority = priority
        add_cans(fn, set(can) if can is not None else set())
        if component_manager is None:
            ComponentManager.register_component_global(fn)
        else:
            component_manager.register_component(fn)
        return fn

    if not callable(name) or name is None:
        # Used as @component(...), resulting in function calls like this:
        # >>> component()(callable)
        # >>> component(name='my_component_name')(callable)
        return register_component
    else:
        # Used as @component, resulting in function calls like this:
        # >>> component(callable)
        fn, name = name, None
        return register_component(fn)


fixture = component


class Requirement(object):

    def __init__(
            self,
            *,
            args=None,
            instance=True,
            scope=None,
            can=None,
            uses=None,
            fixate_entities=True,
            **kwargs):
        self._argument = None
        self._component = None
        self._args = [] if args is None else args
        self._instance = instance
        self._scope_name = scope
        self._can = set(can) if can is not None else set()
        self._uses = set(uses) if uses is not None else set()
        self._fixate_entities = fixate_entities

        for key, value in kwargs.items():
            self._argument = key
            self._component = value

        if len(kwargs.keys()) == 0:
            raise Exception('Error interpreting requires. No component specified.')

        if len(kwargs.keys()) > 1:
            raise Exception('Multiple components named in a single requirement.')

    @classmethod
    def make_requirement(cls, argument, component, instance, scope=None):
        return cls(**{argument: component, 'instance': instance, 'scope': scope})

    @property
    def args(self):
        return tuple(self._args)

    @property
    def instance(self):
        return self._instance

    @property
    def argument(self):
        return self._argument

    @property
    def name(self):
        if not hasattr(self.component, 'entity'):
            return self.component.__name__
        return self.component.entity

    @property
    def component(self):
        return self._component

    @property
    def scope_name(self):
        return self._scope_name

    @property
    def can(self):
        return self._can

    @property
    def uses(self):
        return self._uses

    @property
    def fixate_entities(self):
        return self._fixate_entities

    def __repr__(self):
        return (
            'Requirement(argument="{argument}", component="{component}", '
            'instance={instance} scope={scope})').format(
                argument=self.argument,
                component=self.component,
                instance=self.instance,
                scope=self.scope_name)

    def __eq__(self, other):
        return self.argument == other.argument

    def __hash__(self):
        return self.argument.__hash__()


def requires(**kwargs):
    """Decorate with @requires to indicate that a function or class requires a component."""

    def add_requirement(fn):
        try:
            fn._zaf_requirements.insert(0, Requirement(**kwargs))
        except AttributeError:
            fn._zaf_requirements = [Requirement(**kwargs)]
        return fn

    return add_requirement
