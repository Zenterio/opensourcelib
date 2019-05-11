import collections
import inspect
import logging
from textwrap import dedent

logger = logging.getLogger('zaf.component.manager')


def create_registry():
    return collections.defaultdict(list)


def create_entity_map():
    return collections.defaultdict(set)


def _create_class():

    class Class(object):
        pass

    return Class


ComponentInfo = collections.namedtuple(
    'ComponentInfo', [
        'name', 'callable_name', 'doc', 'module', 'default_scope_name', 'cans', 'requires',
        'extension', 'methods', 'callable', 'priority'
    ])

COMPONENT_REGISTRY = create_registry()
ENTITY_COMPONENT_NAMES = create_entity_map()


class ComponentManager(object):

    def __init__(
            self, component_registry=COMPONENT_REGISTRY,
            entity_component_names=ENTITY_COMPONENT_NAMES):
        self.COMPONENT_REGISTRY = component_registry
        self.ENTITY_COMPONENT_NAMES = entity_component_names
        self.ENTITY_REGISTRY = collections.defaultdict(_create_class)

    @classmethod
    def register_component_global(cls, fn):
        if hasattr(fn, 'entity'):
            ENTITY_COMPONENT_NAMES[fn.entity].add(fn._zaf_component_name)

        COMPONENT_REGISTRY[fn._zaf_component_name].append(fn)

    def register_component(self, fn):
        if hasattr(fn, 'entity'):
            self.ENTITY_COMPONENT_NAMES[fn.entity].add(fn._zaf_component_name)

        self.COMPONENT_REGISTRY[fn._zaf_component_name].append(fn)

    def clear_component_registry(self):
        self.COMPONENT_REGISTRY.clear()
        self.ENTITY_REGISTRY.clear()
        self.ENTITY_COMPONENT_NAMES.clear()

    def get_unique_class_for_entity(self, entity):
        """
        Return a unique anonymous class reference for a named entity.

        The first time this method is called for one specific entity, an anonymous
        class is created and a reference to it is returned.

        Subsequent calls to this method for the same entity returns a reference
        to the same anonymous class.

        :param entity: Any hashable type identifying the entity
        :return: A reference to an anonymous class.
        """
        entity_class = self.ENTITY_REGISTRY[entity]
        entity_class.entity = entity
        return entity_class

    def get_cans(self, component):
        if hasattr(component, '_zaf_component_can'):
            return component._zaf_component_can
        else:
            return set()

    def component_name_to_entity_mapping(self, entities):
        mapping = {}
        for entity in entities:
            for component_name in self.ENTITY_COMPONENT_NAMES.get(entity, []):
                if component_name in mapping:
                    raise KeyError("Can't create mapping for entities with same component name")
                mapping[component_name] = entity
        return mapping

    def get_components_info(self):
        components_info = []

        def is_public_function(function):
            return inspect.isfunction(function) and not function.__name__.startswith('_')

        for name, components in self.COMPONENT_REGISTRY.items():

            for component in components:
                methods = []
                if inspect.isclass(component):
                    methods = inspect.getmembers(component, predicate=is_public_function)

                components_info.append(
                    ComponentInfo(
                        name=name,
                        callable_name=component.__name__,
                        doc='No description'
                        if component.__doc__ is None else dedent(component.__doc__).strip(),
                        module=inspect.getmodule(component),
                        default_scope_name=component._zaf_component_default_scope_name,
                        cans=self.get_cans(component),
                        requires=[] if not hasattr(component, '_zaf_requirements') else
                        component._zaf_requirements,
                        extension=component._zaf_component_extension,
                        methods=[method for name, method in methods],
                        callable=component,
                        priority=component._zaf_component_priority,
                    ))
        return components_info

    def log_components_info(self):
        """Log information about all components to assist in trouble-shooting."""
        components_info = self.get_components_info()
        components_info.sort(key=lambda c: c.name)
        for comp in components_info:
            logger.debug(comp)
