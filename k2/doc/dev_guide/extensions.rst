
.. _extensions:

**********
Extensions
**********

K2 is built around extending the basic functionality with extensions.
There are currently two kinds of extensions that are handled differently.
These are *framework extensions* and *command extensions*.
Framework extensions can provide new commands or provide new general functionality to the K2 core framework while
command extensions can extend the functionality of one or multiple commands.


Common functionality
====================

All extensions provide a name, the config options that the extension needs and the messagebus endpoints and messages
that the extension defines.

If an extension does work that can take time or isn't entirely driven by acting on messages, it should listen for the
ABORT and CRITICAL_ABORT events and take appropriate shutdown actions when they happen. This to ensure that a K2 run
can be interrupted if needed.

On top of this all extensions can implement the following methods.

initialize:
    Called with the config that the extension has requested to initialize the extension

destroy:
    Called when the extension should deregister from the messagebus and clean up resources

States
------
An extension can be disabled/enabled. If an extension is disabled, it will not
be initialized at all. See also load order in what stages extensions can be
disabled/enabled.

An extension can be active/inactive. If an extension is inactive, it will be
initialized but its dispatchers will not be registered and it will hence
not react to messages.

The extensions active state can be conditioned on configuration by
passing arguments for `activate_on` and `deactivate_on` in the extension decorators.

`deactivate_on` has precedence over `activate_on`.


Framework Extensions
====================

Framework extensions have the ability to extend the functionality of the K2 framework.
They have the ability to add commands or to provide new general functionality to the K2 core framework.
Because framework extensions both can request config and provide config it's important to be able to control
both the load order and priority of them.

A framework extension has the following additional methods that it can implement

get_config:
    Possibility for the extension to provide additional config

Load Order
----------

The load order specifies the order that the framework extension will be loaded.
The load order is a number between 1 and 1000 that are divided into 4 ranges.

1-10:
    After load order 10 all plugins will be loaded.
    This means that affecting the plugins.path config after load order 10 doesn't have any effect

11-20:
    After load order 20 extensions will be enabled/disabled depending on the config.
    This means that extensions disabling other extensions need to have load order <= 20.

21-90:
    At load order 90 the first parsing of the command parameters is performed.
    This means that most of the extensions adding config have load order < 90

91-100:
    At load order 100 the default mechanic is to fail if all required config doesn't exist.
    91-99 gives the possibilty to act on the command parameters.
    This means that all extensions that provide config should have load order <= 100.

100+:
    All config should be completely loaded so it should be ok to do anything that depends on config.
    If depending on config before this point the load order should be carefully considered.

Config Priority
---------------

The return value of the get_config method contains a priority.
This is used to decide which config value to use if multiple extensions provide different values for the same key.
Default values get priority 0 and when adding values to the config the existing value will be overwritten if the new
value has the same or higher priority.


Command Extensions
==================

Command extensions can extend a command's execution. This is accomplished by
registering dispatchers to the messages that a command provides.

There are two ways for command extensions to extend commands. The most direct
way is for the command extension to simply extend the command directly by
referencing the command's CommandId. The other way is through the *command
capability* mechanism.

Command Capabilities
--------------------

Command capabilities is a mechanism that provides loose coupling between
command extensions and commands.

Instead of command extensions only being directly coupled to specific commands
by extending the command itself (by referencing its CommandId), a command
extension may instead extend abstract command capabilities. A command can in
turn specify that it *uses* a set of command capabilities.

The application then makes the connection between commands and command
extensions by evaluating command capabilities to determine which command
extensions match which commands.

This evaluation will match a command extension to a command if the set of
command capabilities specified in the extension's ``extends`` *is a subset of*
the command capabilities specified in the command's ``uses``.

Command capabilities are specified as Python strings.

.. Note::
    There is no limitation on whether a command extension only extends commands
    directly, only extends command capabilities or extends a mix both. All
    combinations are allowed.


Extension Classification
========================
Extensions, both framework and command extensions, can be classified as:

* Core
* General
* Product-line specific

See the respective sub-sections below for a deeper description.

K2 does not distinguish between these classes, but the developer should have
in mind what the intended use is and design configuration options, logging
and documentation accordingly.

Core Extensions
---------------
Core extensions are central to the K2 framework to perform its core functionality.
It includes extensions such as the test runner (invoked by the run command) and
the config, extensions, end-points commands.

General Extensions
------------------
General extensions are multi-/general-purpose extensions that can be used in a
variety of settings. They are not product specific and are often highly configurable.
Examples of possible general extensions are ssh-client extension allowing for
execution of commands on a remote system, HTTP-server that can be configured
to give specific responses to certain requests.

Product-line specific
---------------------
This class of extensions are highly specialized and very narrow in their use. It
could be clients that implement a proprietary protocol only available in a specific
product; a firmware upgrade procedure unique to a line of products.


Implementation
==============

Extensions are implemented by using one of the decorators
:py:meth:`zaf.extensions.extension.CommandExtension` or :py:meth:`zaf.extensions.extension.FrameworkExtension`.


Documentation
=============

Extensions provide documentation to the user guide.
The main documentation is taken from the module docstring of the module where the extension is declared.
If the same extension name is used in multiple modules the docstrings are concatenated.
The recommendation in this case is to write the complete documentation in one module to get more control.

The documentation will also include the docstrings from the extension classes as well as generated documentation
about all config options, commands, endpoints and messages that the extensions uses.
The config options, commands, endpoints and messages are also included in the complete lists for all of K2.


Examples
========

Creating a new Extension
------------------------

Extensions can easily be created by using the addon extension. To create a new extension, simply
start the extension creation wizard and follow the on-screen instructions:

.. code-block:: shell

    $ zk2 addon create

Defining new CommandExtension
-----------------------------

This example uses the direct command extension mechanism to associate the
extension with a specific command by extending its CommandId in ``RUN_COMMAND``.

.. code-block:: python

    from zaf.extensions.extension import CommandExtension

    @CommandExtension(
        name='myextension',
        config_options=[MY_CONFIG_OPTION],
        extends=[RUN_COMMAND],
        endpoints_and_messages={MY_EXTENSION_ENDPOINT: [MY_MESSAGE1, MY_MESSAGE2]})
    class MyExtension(object):

        def initialize(self, config, instances):
            self.my_config_value = config.get(MY_CONFIG_OPTION)

        @sequential_dispatcher([SOME_MESSAGE], [SOME_ENDPOINT])
        def handle_some_message(self, message):
            ...

        def destroy():
            ...

A CommandExtension Extending Command Capabilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First we define a command **mycommand** that *uses* two command capabilities:
**capability_a** and **capability_b**.

.. code-block:: python

    from zaf.commands.command import CommandId

    def mycommand(core):
        pass

    MY_COMMAND = CommandId(
        'mycommand', 'Runs my command', mycommand, [],
        uses=['capability_a', 'capability_b'])

Then we create a command extension which extends the same command
capabilities.

.. code-block:: python

    from zaf.extensions.extension import CommandExtension

    @CommandExtension(
        name='myextension',
        config_options=[MY_CONFIG_OPTION],
        extends=['capability_a', 'capability_b'],
        endpoints_and_messages={MY_EXTENSION_ENDPOINT: [MY_MESSAGE1, MY_MESSAGE2]})
    class MyExtension(object):

        def initialize(self, config, instances):
            self.my_config_value = config.get(MY_CONFIG_OPTION)

        @sequential_dispatcher([SOME_MESSAGE], [SOME_ENDPOINT])
        def handle_some_message(self, message):
            ...

        def destroy(self):
            ...

Remember that the matching rules governing command capabilities dictate that if
the command capabilities a command extension ``extends`` is a subset of a
command's ``uses``, the command extension will be associated with the
command. This is the case here, so ``myextension`` will match for
``mycommand``.


Defining new FrameworkExtension
-------------------------------

.. code-block:: python

    from zaf.extensions.extension import FrameworkExtension

    @FrameworkExtension(
        name='myextension',
        config_options=[MY_CONFIG_OPTION],
        commands=[MY_NEW_COMMAND],
        endpoints_and_messages={MY_NEW_COMMAND_ENDPOINT: [MY_NEW_COMMAND_MESSAGE1, MY_NEW_COMMAND_MESSAGE2]})
    class MyExtension(object):

        def initialize(self, config, instances):
            self.my_config_value = config.get(MY_CONFIG_OPTION)

        def get_config(self, config, requested_config_options, commands_with_config_options):
            return ExtensionConfig(read_config_from_somewhere(), priority=14)

        @sequential_dispatcher([SOME_MESSAGE], [SOME_ENDPOINT])
        def handle_some_message(self, message):
            ...

        def destroy(self):
            ...


Extensions Documentation
========================

.. automodule:: zaf.extensions.extension

.. autofunction:: FrameworkExtension

.. autofunction:: CommandExtension

.. autoclass:: ExtensionConfig

   .. automethod:: __new__


Extension Test Harness
======================

Extensions rely on the availablility a lot of underlying infrastructure to function. They can be difficult to
write unit tests for. The message bus needs to be made available, an appropriate configuration context needs
to be prepared and everything needs to be connected together.

The extension test harness can be used to simplify this process.

For example, lets take a look at this ficticious extension:

.. code-block:: Python

    from zaf.component.decorator import requires
    from zaf.config.options import ConfigOption, ConfigOptionId
    from zaf.extensions.extension import AbstractExtension, CommandExtension
    from zaf.messages.decorator import sequential_dispatcher
    from zaf.messages.message import EndpointId, MessageId

    from k2.cmd.run import RUN_COMMAND
    from k2.runner import TEST_CASE_FINISHED


    MY_ENDPOINT = EndpointId('MY_ENDPOINT', 'This is my endpoint')
    MY_MESSAGE = MessageId('MY_MESSAGE', 'This is my message')

    MY_CONFIG_OPTION = ConfigOptionId(
        'my.config.option',
        'When a TEST_CASE_FINISHED is received, trigger a MY_MESSAGE with this value as data',
        option_type=int,
        default=1)


    @CommandExtension(
        name='myextension',
        extends=[RUN_COMMAND],
        config_options=[
            ConfigOption(MY_CONFIG_OPTION, required=True),
        ],
        endpoints_and_messages={
            MY_ENDPOINT: [MY_MESSAGE],
        })
    class MyExtension(AbstractExtension):

        def __init__(self, config, instances):
            self._value = config.get(MY_CONFIG_OPTION)

        @sequential_dispatcher([TEST_CASE_FINISHED])
        @requires(messagebus='MessageBus')
        def handle_test_case_finished(self, message, messagebus):
            messagebus.trigger_event(MY_MESSAGE, MY_ENDPOINT, data=self._value)

It takes configurable value and each time it sees that a test case has completed, it triggers an
event with some configurable data. Now we want to write some unit tests! To acomplish this we will
make use of the extension test harness:

.. code-block:: Python

    import unittest
    from ..myextension import MY_CONFIG_OPTION, MY_MESSAGE, MyExtension
    from zaf.builtin.unittest.harness import ExtensionTestHarness
    from zaf.messages.dispatchers import LocalMessageQueue
    from zaf.messages.message import EndpointId

    from k2.runner import TEST_CASE_FINISHED


    MOCK_ENDPOINT = EndpointId('mock endpoint', 'mock description')


    class TestMyExtension(unittest.TestCase):

        @staticmethod
        def _create_harness(my_config_option):
            return ExtensionTestHarness(
                MyExtension,
                config={
                    MY_CONFIG_OPTION: my_config_option,
                },
                endpoints_and_messages={
                    MOCK_ENDPOINT: [TEST_CASE_FINISHED],
                })

The test harness can now be used to create instances of our extension. Lets start writing some tests:

.. code-block:: Python

    class TestMyExtension(unittest.TestCase):

        # ...

        def test_my_extension_triggers_an_event_when_test_case_finished_is_received(self):
            with self._create_harness(my_config_option=5) as harness:
                with harness.message_queue([MY_MESSAGE]) as queue:
                    harness.messagebus.trigger_event(TEST_CASE_FINISHED, MOCK_ENDPOINT, data=None)
                    message = queue.get(timeout=10)
                    assert message.data == 5

The extension test harness is widely used throughout K2. If you need further inspiration as to its operation
and how it can be used, there are plenty of examples in the K2 source tree.

Extension Test Harness Documentation
====================================

.. automodule:: zaf.builtin.unittest.harness

.. autoclass:: ExtensionTestHarness
    :members:

.. autoclass:: SyncMock
    :members:

Decisions
=========

Load order
----------

The idea behind the load order and config priority handling is that we will have extensions depending on config
provided by other extensions and if we don't build a complete dependency system around this we will need to solve it
in some other way.

Let's take an example with two extensions.
One that reads config from a file and one that reads extended config from a database.
To be able to use the database the database extension requests the *db.url*, *db.name*, *db.user* and *db.pwd* config
options.
And let's say that those config values are read from the config file.

To be able to make sure that the values exist before we initialize the database extension we need to be able to specify
this dependency or specify in some other way that we run the database intialization after the config file parsing.

The load order lets us deal with this manually.

Priority
--------

We will probably have the case that multiple extensions provide the same config values.
This needs to be handled by prioritizing the config that extensions provide.
The easiest way to do this is to use the load order and say that the last read value will be used.

This leads to problems though because we need to be able to specify the load order to solve dependencies.
It's not certain that just because something is loaded after something else that it should override all the config.
In the example above we might want the database to be lower priority than the config file but we still need the config
file to provide the config required to connect to the database.

Logging
-------

Extensions should use a logger named with the help of the get_logger_name method from k2.extension.extension.
This will ensure that the name of their logger is predictable based on their name, and correctly placed in the k2 logger hierarchy.

.. code-block:: python

    logger = logging.getLogger(get_logger_name('k2', EXTENSION_NAME))
    logger.addHandler(logging.NullHandler())


EXTENSION_NAME should be the same as in the name= parameter to the Extension decorator

See also :ref:`logging`.
