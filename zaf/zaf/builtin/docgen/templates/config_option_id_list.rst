{% import 'macros.rst' as macros %}
.. _list-config_option_ids:

{{ macros.header('List of Config Options', 1) }}

{% for option in config_option_ids %}
.. _option-{{ option.key }}:

{{ macros.format_option(option, 2, include_extension_names=True, include_command_names=True) }}
{% endfor %}
