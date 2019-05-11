
******
Config
******

Config options are defined by extensions or by the K2 Core by using the
:py:class:`zaf.config.options.ConfigOptionId` class.
The name of the config option should be a dot separated string where each part of the string corresponds to a
level in the config structure.

An example is the config that is used to active the XML report generation that has the name "reports.xml".
This should be read as if it belongs to the reports section of the config and the unique identifier in the reports
section is the "xml" part.
Expanding this we could have other connected config options like "reports.html" or "reports.xml.encoding".

Types
=====

Config options can be defined with different types that will be enforced by K2.
Currently supported types are:

* :py:class:`str`
* :py:class:`int`
* :py:class:`float`
* :py:class:`bool`
* :py:class:`zaf.config.types.Path`
* :py:class:`zaf.config.types.Choice`
* :py:class:`zaf.config.types.ConfigChoice`
* :py:class:`zaf.config.types.GlobPattern`
* :py:class:`zaf.config.types.Flag`

Each type may provide a self-check mechanism that performs sanity checks on provided configuraiton.
Such sanity-checks are performed by the :py:class:`zaf.builtin.config.validator.ConfigurationValidator` framework extension.

Registering config options
==========================

Config options can be registered by extensions with decorators
:py:meth:`zaf.extensions.extension.CommandExtension` or :py:meth:`zaf.extensions.extension.FrameworkExtension`.
This makes it possible to also specify if the config option is required or not.

CLI Options and Environment Variables
=====================================

The config options are converted to CLI options by replacing dots with dashes.
For example the "reports.xml" config option will be translated to the "--reports-xml" CLI option.

The config options are also converted to environment variables by prefixing with K2, replacing dots with underscore
and converting to uppercase.
The "reports.xml" config option can be specified with the "K2_REPORTS_XML" environment variable.

Hidden Options
==============

Less common options can be marked as hidden and will then not be included in the normal *--help* output.
This is especially useful on options that are defined at an entity option because they can generate a lot
of lines in the help, hiding more important information.
The hidden options will be shown if *--full-help* is given.

Setting hidden on an option will in the future also change how it is presented in the generated user guide information.

Application Context
===================

An application has an application context that is used to select which commands and options that should be included in the application.
The currently available contexts are *INTERNAL*, *EXTENDABLE* and *STANDALONE*.

It's possible to specify on a command or an option for which contexts it is applicable for.
If an option is not applicable for an application it will be removed completely from the command line parsing
and providing it anyway will give an error.

INTERNAL
    An internal option should never be visible and is only meant to distribute internal informaton
    to extensions.
    It's not intended to set INTERNAL on an application.

EXTEDANBLE
    An extendable application means that options and commands related to extensions should be added.

STANDALONE
    A standalone application will not include options related to extendability and is therefore meant
    for more focused applications.

Conventions
===========

* Always name the python constant for a ConfigOptionId to name in uppercase with underscore instead of dots

Examples
========

Defining new ConfigOptionId
---------------------------

.. code-block:: python

   from zaf.config.options import ConfigOptionId
   MY_CONFIG_OPTION = ConfigOptionId('my.config.option', 'Description of my.config.option', type=int)


Defining Config Options in extensions
-------------------------------------

.. code-block:: python

   from zaf.config.options import ConfigOptionId, ConfigOption
   MY_CONFIG_OPTION = ConfigOptionId('my.config.option', 'Description of my.config.option', type=int)

   @CommandExtension(name='myextension', config_options=[ConfigOption(MY_CONFIG_OPTION, required=True)])
   class MyExtension(AbstractExtension):
      pass


Endpoint Documentation
======================

.. automodule:: zaf.config.options

.. autoclass:: ConfigOptionId
   :members:

   .. automethod:: __new__

.. autoclass:: ConfigOption
   :members:

.. automodule:: zaf.builtin.config.validator

.. autoclass:: ConfigurationValidator
   :members:

.. automodule:: zaf.config.types

.. autoclass:: Path
   :members:

.. autoclass:: Choice
   :members:

.. autoclass:: ConfigChoice
   :members:

.. autoclass:: GlobPattern
   :members:

.. autoclass:: Flag
   :members:
