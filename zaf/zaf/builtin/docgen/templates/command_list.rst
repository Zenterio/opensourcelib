{% import 'macros.rst' as macros %}
.. _list-commands:

{{ macros.header('List of Commands', 1) }}

.. toctree::
    :hidden:
    :glob:

    commands/*

{% for command in commands %}
{{ macros.format_command_short(command) }}

{% endfor %}
