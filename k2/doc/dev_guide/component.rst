
********************
The component module
********************

For an overview of the intended usage of the components concept, please see the
K2 user guide.

Decorators
==========

The @component decorator
------------------------

Each function or class decorated with the :py:func:`zaf.component.decorator.component`
decorator is registered with the :py:class:`zaf.component.manager.ComponentManager`
at evaluation time. When a component is registered with the `ComponentManager`,
a reference to the component is stored. This ensures that the component can be
found at a later time and that the lifetime of each component definition is at
least as long as that of the `ComponentManager`.

.. automodule:: zaf.component.manager
.. autoclass:: ComponentManager
.. automodule:: zaf.component.decorator
.. autofunction:: component

The @requires decorator
-----------------------

Requirements are expressed as instances of the :py:class:`zaf.component.decorator.Requirement`
class. Explicit requirements are stored as an attribute on the decorated function
or class, named `_k2_requirements`. If there are no explicit requirements,
this attribute is not set.

.. autoclass:: Requirement
   :members:
.. autofunction:: requires

Factory
=======

The :py:mod:`zaf.component.factory` module is responsible for lifetime management
and creation of component instances requested by users of the framework. Most of
this functionality is provided via the :py:func:`zaf.component.factory.call`
method, which wraps a function call to a potential component recipient. The
recipient is inspected and if any requirements are found, the keyword arguments
dictionary of the call is updated to include the requested dependencies.

Implicit requirements are discovered by inspecting the signature of the
recipient function and explicit requirements are found by inspecting the
`_k2_requirements` attribute.

.. automodule:: zaf.component.factory
.. autoclass:: Factory
   :members:
.. automodule:: zaf.component.scope
.. autoclass:: Scope
   :members:

Lifetime management
===================

When using the :py:func:`zaf.component.factory.call` method, all component instances
required to perform the call are created. To facilitate re-using component instances,
all such instances are then stored in the scope that was included in the call, or in
the applicable parent scope.

It's up to the creator of scopes to deal with exiting the scopes at the correct time.
When exiting a scope, all references to instances associated with that scope are removed.

Extending components
====================

It may be desirable to extend an existing component with additional properties or
capabilities instead of creating a new one.

Registering an extensible component
-----------------------------------

To allow others to extend a component, a reference to that component must be available
for others to use. The :py:class:`zaf.component.manager.ComponentManager` provides
facilities for this purpose, where a class reference may be requested based on an entity
identifier.

.. autoclass:: zaf.component.manager.ComponentManager
   :members: get_unique_class_for_entity

Example usage
-------------

.. code-block:: python

    # Registering a "Sut" component ...
    sut = ComponentManager.get_unique_class_for_entity('Sut')
    Component(name='Sut')(sut)

    # ... and then later on adding a property to it.
    sut = ComponentManager.get_unique_class_for_entity('Sut')
    add_properties(sut, 'telnet', { 'port': 123 })

    @requires(sut=Sut)
    def check_telnet_port(sut):
        assert sut.telnet.port == 123

Extending capabilities of a component
-------------------------------------

.. autofunction:: zaf.component.util.add_cans

Extending properties of a component
-----------------------------------

.. autofunction:: zaf.component.util.add_properties
