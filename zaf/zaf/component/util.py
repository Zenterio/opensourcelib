import inspect
from types import SimpleNamespace


def add_cans(component, cans):
    """
    Add capabilities to a component.

    :param component: Reference to the component to add capabilities to
    :param cans: List of capabilities to add to the component

    Example usage:

    .. code-block:: python

        # If the capabilities of a component is known when declaring a
        # component, we can add them as part of the declaration.
        @component(cans=['telnet'])
        def Stb():
            pass

    .. code-block:: python

        # If the capabilities are unknown when declaring a component ...
        @component
        def Stb():
            pass

        # ... we can add them at a later time.
        add_cans(Stb, ['telnet'])
    """
    if not isinstance(getattr(component, '_zaf_component_can', None), set):
        component._zaf_component_can = set()
    if isinstance(cans, str):
        cans = [cans]
    component._zaf_component_can.update(cans)


class ComponentPropertyError(Exception):
    pass


def add_properties(component, namespace, properties):
    """
    Add properties to a component.

    :param component: Reference to the component to add properties to
    :param namespace: Name of the namespace to add properties to
    :param properties: Dictionary containing the properties to add

    A namespace may be extended with new properties.
    Existing properties may not be overriden.

    Example usage:

    .. code-block:: python

        @component
        def my_telnet_component():
            pass

        add_properties(my_telnet_component, 'telnet', {'port': 23})

        # The port property can then later be accessed, like so:
        @requires(exec=my_telnet_component, instance=False)
        def my_test_case(exec):
            print(exec.telnet.port)  # This will print 23
    """
    if hasattr(component, namespace):
        namespace_instance = getattr(component, namespace)
        if not isinstance(namespace_instance, SimpleNamespace):
            raise ComponentPropertyError(
                "'{namespace}' is not a namespace on component '{component}'".format(
                    namespace=namespace, component=component))
        non_unique_keys = namespace_instance.__dict__.keys() & properties.keys()
        if non_unique_keys:
            raise ComponentPropertyError(
                "Properties '{keys}' already exists on '{component}.{namespace}'".format(
                    keys=non_unique_keys, namespace=namespace, component=component))
        namespace_instance.__dict__.update(properties)
    else:
        setattr(component, namespace, SimpleNamespace(**properties))


def is_generator(thing):
    """Determine if something is a generator instance."""
    return inspect.isgenerator(thing)


def is_context_manager(thing):
    """Determine if something is a context manager."""
    return not inspect.isclass(thing) and hasattr(thing, '__enter__') and hasattr(thing, '__exit__')
