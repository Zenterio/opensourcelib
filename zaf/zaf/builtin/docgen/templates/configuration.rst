.. _configuration:

Configuration
=============

Configuration can be read from different sources. The following sources are
available:

* Command line
* File

{% if include_config_command %}

The config command
------------------

The  `config` command can be used to print the current configuration.

The simplest version prints all configuration options available:

 $ {{entrypoint_name}} config

Each line contains information about a specific option, including its name,
value and where it was provided. Optionally, a list of names may be provided as
arguments to the `config` command. If such a list is provided, only information
about the named option will be printed.

{% endif %}

.. _configuration_files-label:

Configuration files
-------------------

Configuration on file is stored in the YAML format.

The order in which configuration files are loaded is determined by their load
order. Configuration files that are loaded before others may change the paths
for configuration files loaded at a later time.

Different configuration files have different priority, where configuration files
of a higher priority may override other configuration regardless of load order.

.. list-table::
   :header-rows: 1

   * - Type
     - Default location
     - Load order (lower is loaded first)
     - Priority
   * - System configuration
     - /etc/{{application_name}}/config
     - 4
     - 10
   * - User configuration
     - ~/.{{application_name}}config
     - 6
     - 20
   * - Local configuration
     - ./{{application_name}}config
     - 8
     - 30
   * - Additional configuration
     -
     - 2
     - 40
   * - Explicit configuration
     -
     - 2
     - 50

Additional and explicit configuration files
-------------------------------------------

In addition to the system, user and local configuration files, configuration
files may be provided on the command line. It is possible to provide multiple
configuration files on the command line, where they will be evaluated in the
order that they are provided.

Additional configuration files are provided using the `--additional-config-file-pattern`
option and are applied in addition to other configuration files.

example:

.. code-block:: shell

    {{entrypoint_name}} --additional-config-file-pattern 'path/*.yaml' <command>

Explicit configuration files are provided using the `--config-file-pattern` option and
are applied instead of other configuration files.

Note that while explicit configuration files will also override additional
configuration files, it is possible to specify multiple explicit configuration
files.


Config file format
------------------

The YAML config files have a very simple format with keys and values.
The keys are the dot-separated format of the :ref:`config options <list-config_option_ids>` and the values
are specified using normal YAML types.
Multiple values are specified as YAML arrays.

example:

.. code-block:: yaml

    suts.ids: [mystb1, mystb2]
    suts.mystb1.ip: 1.2.3.4
    suts.mystb2.ip: 1.2.3.5


Includes
--------

It's possible to include files into other files using the 'include.files' key.
This takes a list of files to be included.
Config values from included files will have lower priority than the parent file
to make it possible to override values.

example:

.. code-block:: yaml

    include.files:
      - file1.yaml
      - file2.yaml


Entity includes
---------------

It's also possible to include files into an entity namespace.

example:

.. code-block:: yaml

    entity.id.include.files:
      - file1.yaml

This will load *file1.yaml* and prepend all keys in the file with *entity.id*.

All entity config options also has automatically generated *include-files* options
to make it possible to do this on the command line.
In this case it would be used with *--entity-id@include-files file1.yaml*

.. _config-types:

Config Types
------------

Config options can be defined with different types that will be automatically
enforced. Currently supported types are:

* :py:class:`str`
* :py:class:`int`
* :py:class:`float`
* :py:class:`bool`
* :py:class:`zaf.config.types.Path`
* :py:class:`zaf.config.types.Choice`
* :py:class:`zaf.config.types.ConfigChoice`
* :py:class:`zaf.config.types.GlobPattern`
* :py:class:`zaf.config.types.Flag`
* :py:class:`zaf.config.types.Count`

Each type may provide a self-check mechanism that performs sanity checks on provided configuraiton. Such sanity-checks are performed by the :py:class:`zaf.builtin.config.validator.ConfigurationValidator` framework extension.

Config Option Expansion
-----------------------

It's possible to use values of config options in other options using using ${key} syntax.

A common use case of this is to configure files to be inside the output directory.

.. code-block:: yaml

    output.dir: /path/to/output
    log.dir: ${output.dir}/logs
    log.file.mylogfile.path: ${log.dir}/my_log_file.log

This will end up as *log.file.mylogfile.path: /path/to/output/logs/my_log_file.log*.

This of course also works on command line *--log-file-mylogfile@path '${log.dir}/my_log_file.log'*.
Just make sure that the variable is not expanded in the shell.
