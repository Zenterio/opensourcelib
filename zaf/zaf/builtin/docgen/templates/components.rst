.. _components:

**********
Components
**********

Components are functions or classes that encapsulates some information or
functionallity intended for re-use by others. Each component is registered with
the framework and can be requested by a test function, a message handler or
other components.

By default, the framework will create instances of components and is responsible
for the lifetime management and configuration of each component. A user may opt
to configure and manage the lifetime of a component themselves by requesting
a reference instead.

The @component decorator
========================

The :py:func:`zaf.component.decorator.component` decorator provides a mechanism
for declaring components. Components declared at the top-level will be
registered by the framework immediately. Components declared in other scopes,
for example as part of a function body, will be registered each time that
function is called.

The default name of a component is the name of the decorated function or class.
Optionally, a name may be passed as an argument to the
:py:func:`zaf.component.decorator.component` decorator. Multiple components may
share the same name.

The same component may be registered multiple times. This is useful in cases
where different components provide the same type of functionality but use
different methods or require different configuration.

Example usage
-------------

.. code-block:: python

    @component  # This component will be registered as "MediaPlayer"
    class MediaPlayer(object):

        def play_stream(self, url):
            pass

.. code-block:: python

    @component(name='MediaPlayer')
    class SpecializedMediaPlayer(object):

        def play_stream(self, url):
            pass

The @requires decorator
=======================

The :py:func:`zaf.component.decorator.requires` decorator provides a mechanism
where test functions, message handlers and components may declare their dependencies. When called
by the framework, the appropriate components are located, prepared and passed
to the recipient as part of the keyword arguments.

By default, the name of the keyword argument is the name of the component.
Optionally, a different name may be specified as part of the call to
:py:func:`zaf.component.decorator.requires`.

When requesting a component, the recipient can ask to either get a reference to
the component or for the framework to provide a pre-configured instance. This
is controlled using the `instance` keyword argument.

Example usage
-------------

The recipient requires a pre-configured instance of a component named `MediaPlayer`:

.. code-block:: python

    @requires(media_player='MediaPlayer')
    def test_playing_a_stream(media_player):
        media_player.play_stream(url='...')

The recipient requires a reference to a component named `MediaPlayer`:

.. code-block:: python

    @requires(media_player=MediaPlayer, instance=False)
    def test_playing_a_stream(MediaPlayer):
        media_player = MediaPlayer(...)
        media_player.play_stream(url='...')

The recipient specifically requests an instance of the `SpecializedMediaPlayer`.

.. code-block:: python

   @requires(media_player=SpecializedMediaPlayer)
   def test_playing_a_stream(media_player):
       media_player.play_stream(url='...')

Component arguments
-------------------

When requesting an instance of a component, positional arguments to be provided
as part of the call to :py:func:`zaf.component.decorator.requires` using the
`args` argument. Such arguments are passed to the component.

Example usage
-------------

.. code-block:: python

   @component(name='MediaPlayer')
   def media_player(stream_type):
       pass

   @requires(media_player='MediaPlayer', args=['HLS'])
   def test_playing_a_stream(media_player):
       media_player.play_stream(url='...')

Naming conventions
------------------

Components should follow the python convention. Hence classes should be
registered with `CamelCase` and functions as `snake_case`. When requesting
instances, you essentially request a reference stored in a variable and
should hence use `snake_case` for argument names.

Implicit requirements
=====================

The framework support implicit requirements, where test function and component
may declare a dependency by simply adding the name of the component to their
argument list. Note that instances of a component may not be requested using
this method.

Note that explicit requirements take precedence over implicit requirements.

Example usage
-------------

The recipient requires a reference to a component named `MediaPlayer`:

.. code-block:: python

    def test_playing_a_stream(MediaPlayer):
        media_player = MediaPlayer(...)
        media_player.play_stream(url='...')

.. _components_types-label:

Component types
===============

The component factory has support for multiple types of components. Different
types of components are handled differently when instances are created.

Function components
-------------------

When creating an instance of a component that is a function, the return value of
the function is provided to the requester.

.. code-block:: python

    @component
    def one():
        return 1

    @requires(component=one)
    def test_that_uses_my_component(component):
        assert component == 1

Class components
----------------

When creating an instance of a component that is a class, an instance of that
class is provided to the requester.

.. code-block:: python

    @component
    class MyComponent(object):
        pass

    @requires(component=MyComponent)
    def test_that_uses_my_component(component):
        assert type(component) == MyComponent

Generator components
--------------------

When creating an instance of a component that is a generator, the first yielded
value of the generator is provided to the requester.

.. code-block:: python

    @component()
    def my_component():
        instance = create_component_instance()
        yield instance
        destroy_component_instance(instance)

    @requires(component=my_component)
    def test_that_uses_my_component(component):
        pass

Context manager components
--------------------------

When creating an instance of a component that is a context manager, the `__enter__()`
function of the context manager will be called when the instance is created and the
`__exit__()` function of the context manager will be called when the instance is
destroyed.

The return value of calling the `__enter__()` function is provided to the requester.

.. code-block:: python

    @component()
    class MyComponent(object):

        def __enter__(self):
            self.instance = create_component_instance()
            return instance

        def __exit__(self, *exc_details):
            destroy_component_instance(self.instance)

    @requires(component=MyComponent)
    def test_that_uses_my_component(component):
        pass

Lifetime management
===================

Component instances created by the framework can have different lifetimes. For
example, some instances may be created once per session while others should be
recreated before each test.

The lifetime of a component instance is decided by providing a scope in which it is intended to live.
There are different scopes available when using components depending on the place.

Component instances are created as they are requested. As such, an instance with
session scope may not necessarily be created at the start of a test session.
Instead, it will be created the first time a test function requests it. That
instance will then be re-used each time a session scoped instance of that
component is requested.

.. note::

    Note that component instances can only depend on other instances that have
    longer or equal lifetime.

Components may provide a default `scope` by providing a `scope` argument to the
:py:func:`zaf.component.decorator.component` decorator.

The actual scope is decided by the `scope` argument provided to the
:py:func:`zaf.component.decorator.requires` decorator. If no such argument is
provided, the default scope is used.


Scopes, Components and Threads
------------------------------
Some scopes are shared between multiple threads.
This means that components created on those scopes need to be thread safe.

When instantiating components on a scope a lock is taken to avoid collisions where multiple threads
try to create the same component at the same time.
If it takes a long time to instantiate a component this will block all other component instantiations on that
scope which could lead to unexpected slowdowns.


Test Case scopes
----------------
The most common place to use components are inside test cases.
For test cases the available scopes are.

session (multi threaded)
    The session includes all the initialization and cleanup stages
runner (multi threaded)
    From the first test case starts until the last test case is complete
module (single threaded)
    When running consecutive test cases from the same module the module scope is from
    the start of the first test case in the module until just before the first test case outside of the module.
class (single threaded)
    When running consecutive test cases from the same class the class scope is from
    the start of the first test case in the class until just before the first test case outside of the class.
test (single threaded)
    From just before a test case to just after a test case

Message scopes
--------------
It's also possible to use components when handling messages.
This should be seen more as an internal detail and should not be needed when developing test cases.
For messages the available scopes are.

session (multi threaded)
    The session includes all the initialization and cleanup stages

message (single threaded)
    From just before a message is handled to just after it's handled

Example usage
-------------

.. code-block:: python

    # Component with default scope 'session'
    @component(scope='session')
    class MockServer(object):
        pass

    # The 'session' scoped MockServer will be created for this test
    @requires(mock_server=MockServer)
    def test_use_a_mock_server(mock_server):
        pass

    # The 'session' scoped MockServer will be re-used for this test
    @requires(mock_server=MockServer)
    def test_use_a_mock_server_again(mock_server):
        pass

    # A 'test' scoped MockServer will be created for this test
    @requires(mock_server=MockServer, scope='test')
    def test_use_a_unique_mock_server(mock_server):
        pass

Instantiation order
===================

If multiple component instances of the same lifetime are requested, they will
be created in the order they are listed.

.. code-block:: python

   @component
   def one():
       return 1

   @component
   def two():
       return 2

   # The "one" instance will be created before the "two" instance
   @require(one=one, scope='test')
   @require(two=two, scope='test')
   def test_case(one, two):
       assert one == 1
       assert two == 2

If multiple instances of different lifetime are requested, the instances with
a longer lifetime will be created first, in the order they are listed.

.. code-block:: python

   @component
   def one():
       return 1

   @component
   def two():
       return 2

   @component
   def three():
       return 3

   # The "three" instance will be created first since it belongs to
   # the larger scope.
   @require(one=one, scope='test')
   @require(two=two, scope='test')
   @require(three=three, scope='session')
   def test_case(one, two, three):
       assert one == 1
       assert two == 2
       assert three == 3

Instances are destroyed in the reverse order that they are listed. Instances
with a shorter lifetime will be destroyed first.

Component requirements
======================

A component may provide a list of capabilities that it has. Items from this
capability list can then be used to request a component instance that has
specific capabilities.

Example usage
-------------

.. code-block:: python

    @component(can=['HLS'])
    class Sut(object):
        pass

    @component(can=['IGMP'])
    class Sut(object):
        pass

    @component
    class Player(object):
        pass

    @requires(stb='Sut', can=['HLS'])
    def test_play_a_hls_stream(stb, Player):
        Player(stb).play('http://... stream URL .../')

    @requires(stb='Sut', can=['IGMP'])
    def test_play_a_igmp_stream(stb, Player):
        Player(stb).play('igmp://... stream URL .../')

Adding capabilities to Sut
--------------------------

It's possible to add capabilities to the sut using configuration with the
:ref:`option-suts.<ids>.add.can` config.


Priority
========

When there are multiple components fulfilling a requirement the selection will
first be based on the priority of the components and then on the order they are loaded.
The priority is a an integer with the default value *0*.
A component with higher priority value will be selected before a component with lower value.

.. code-block:: python

    @component(exec='Exec', can=['telnet'], priority=1)
    class TelnetExec(object):
        pass

    @component(exec='Exec', can=['serial'], priority=-1)
    class SerialExec(object):
        pass

    @component(exec='Exec', can=['serial'], priority=0)
    class OtherSerialExec(object):
        pass

    @requires(exec='Exec')
    def test_receives_correct_exec(exec):
        assert type(exec) == TelnetExec

    @requires(exec='Exec', can=['serial'])
    def test_receives_correct_serial_exec(exec):
        assert type(exec) == OtherSerialExec

In the dependency graph the selections will be performed separately for each requirement
and the priority will only be considered for the components that fulfill the same requirement.
This means that a high priority component far down the dependency graph will not affect
the selection on higher levels.

Uses
====

Sometimes it's necessary to enforce the usage of the exact same component
in other components or tests.
This can be done with the `uses` keyword in the *requires* decorator.

Uses is a list of local names of other required components.
The following code example makes sure that the same sut is used in the sut argument
and when instantiating the Player.

.. code-block:: python

    @requires(sut='Sut')
    @requires(player='Player', uses=['sut'])
    def test_with_sut_and_player(sut, player):
        ...

Without *uses* different instances of *Sut* could be selected if there are multiple know *Suts*
in the test run.
