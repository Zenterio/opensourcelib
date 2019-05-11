{% import 'macros.rst' as macros %}
.. _extension-{{extension.name}}:

{{ macros.h1(extension.name|capitalize) }}

{{ extension.description }}

{% if extension.config_option_ids -%}
Config Options
==============
{{ macros.format_options(extension.config_option_ids, 3, include_command_names=True) }}
{%- endif -%}

{%- if extension.commands %}
Commands
========
{% for command in extension.commands %}
{{ macros.format_command_short(command) }}
{% endfor %}
{%- endif %}

{%- if extension.components and filter.include_components %}
Components
==========
{% for component in extension.components %}
{{ macros.format_component_short(component) }}
{% endfor %}
{%- endif %}

{% if filter.include_endpoints_and_messages %}
{%- if extension.endpoints %}
Endpoints
=========
{% for endpoint in extension.endpoints %}
{{ macros.format_endpoint_short(endpoint) }}
{% endfor %}
{%- endif %}

{%- if extension.messages -%}
Messages
=========
{% for message in extension.messages %}
{{ macros.format_message_short(message) }}
{% endfor %}
{%- endif %}
{% endif %}
{% if filter.include_classes %}
Classes
=======
{% for extension_class in extension.extension_classes %}
{{ macros.h3(extension_class.class_name) }}

{{ extension_class.description }}
{% endfor %}
{% endif %}

{%- if extension.groups %}
Related topics
==============
{% for group in extension.groups %}
{{ macros.h3(group) }}
{% for member in extension.group_members(group) %}
* {{ member|ref('extension') }}
{% endfor %}
{%- endfor %}
{% endif %}
