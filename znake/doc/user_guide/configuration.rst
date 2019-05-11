
*************
Configuration
*************

Znake uses YAML and environment variables to source its configuration.

Configuration is read in the following order from the following locations:

1. A default znake.yaml that is built into Znake.
2. A project-specific znake.yaml that is read from the current working directory.
3. Environment variables prefixed with ZNAKE.
4. A .yaml file provided on the command line using the -f flag.

The above configuration sources are merged into the final configuration.
If different sources provide conflicting settings, the configuration that is loaded last is used.

Znake provides a sane default configuration that is applicable for most Python projects.
Some project specific configuration that Znake can not guess must be provided, such as a project name and version.
