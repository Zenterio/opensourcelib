{% import 'macros.rst' as macros %}
.. _list-messages:

{{ macros.header('List of Messages', 1) -}}
{% for message in messages %}
{{ macros.format_message(message, 2) }}
{%- endfor %}
