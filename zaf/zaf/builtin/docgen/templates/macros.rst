{########### formats list of options ##########}
{% macro format_options(options, headersize, include_extension_names=False, include_command_names=False) -%}
{% for option in options %}
{{ format_option(option, headersize, include_extension_names, include_command_names) }}
{% endfor %}
{%- endmacro %}

{########### formats an option ##########}
{% macro format_option(option, headersize, include_extension_names=False, include_command_names=False) -%}
{{ header(option.key, headersize) }}
{{ option.description }}

:Cli: {{ option.cli }}
:Type: {{ option.type_string }}
{%- if option.has_default  %}
:Default: {{ option.default }}{% endif %}
{%- if option.multiple %}
:Multiple: True{% endif %}
{%- if option.entity %}
:Entity: True{% endif %}
{% if include_extension_names and option.extension_names %}:Extensions: {{ option.extension_names|map('ref', 'extension')|join(', ')}}{% endif %}
{% if include_command_names and option.command_names %}:Commands: {{ option.command_names|map('ref', 'command')|join(', ')}}{% endif %}
{%- endmacro %}

{########### Header 1 ##########}
{% macro h1(name) -%}
{{ '*' * name|length }}
{{ name }}
{{ '*' * name|length }}
{%- endmacro %}

{########### Header 2 ##########}
{% macro h2(name) -%}
{{ name }}
{{ '=' * name|length }}
{%- endmacro %}

{########### Header 3 ##########}
{% macro h3(name) -%}
{{ name }}
{{ '-' * name|length }}
{%- endmacro %}

{########### Header 4 ##########}
{% macro h4(name) -%}
{{ name }}
{{ '^' * name|length }}
{%- endmacro %}

{########### Header 5 ##########}
{% macro h5(name) -%}
{{ name }}
{{ '"' * name|length }}
{%- endmacro %}

{########### Header with configurable size, size is an integer between 1 and 4 ##########}
{% macro header(name, size) -%}
{% if size == 1 %}{{ h1(name) }}
{% elif size == 2 %}{{ h2(name) }}
{% elif size == 3 %}{{ h3(name) }}
{% elif size == 4 %}{{ h4(name) }}
{% elif size == 5 %}{{ h5(name) }}
{%- endif %}
{%- endmacro %}

{########### formats an extension to a short description with link to full page ##########}
{% macro format_extension_short(extension) -%}
{{ extension.name|ref('extension') }}:
    {{ extension.short_description|indent(4)|replace("    \n", "\n") }}
{%- endmacro %}

{########### formats a command to a short description with link to full page ##########}
{% macro format_command_short(command) -%}
{{ command.name|ref('command') }}:
    {{ command.short_description|indent(4)|replace("    \n", "\n") }}
{%- endmacro %}

{########### formats a command with a configureable header size ##########}
{% macro format_command(command, headersize, included_extension_names) -%}
{{ header(command.name|capitalize, headersize) }}
{{ command.description }}

{% if command.extension_name in included_extension_names %}
Provided by:
    {{ command.extension_name|ref('extension') }}
{% endif %}

{% if command.config_option_ids -%}
{{ header('Options', headersize + 1) }}
{{- format_options(command.config_option_ids, headersize + 2) }}
{%- endif %}

{% if command.extension_config_option_ids -%}
{{ header('Extended Options', headersize + 1) }}
{{- format_options(command.extension_config_option_ids, headersize + 2, True) }}
{%- endif %}

{%- endmacro %}

{########### formats a command to a short description with link to full page ##########}
{% macro format_component_short(component) -%}
{{ component.name|ref('component') }}:
    {{ component.short_description|indent(4)|replace("    \n", "\n") }}
{%- endmacro %}

{########## formats a component with a configureable header size ##########}
{% macro format_component(component, headersize) -%}
{{ header(component.name, headersize) }}
{{ component.description }}

Default scope:
    {% if component.default_scope_name %}{{ component.default_scope_name|lower }}{% else %}None{% endif %}

{% if component.cans -%}
Can:
    {{ component.cans|join(', ') }}
{%- endif %}

{% if component.priority != 0 -%}
Priority:
    {{ component.priority }}
{%- endif %}

{% if component.extension_name -%}
Provided by:
    {{ component.extension_name|ref('extension') }}
{%- endif %}

{% if component.requires -%}
Requires
^^^^^^^^
{% for require in component.requires %}
{{ require.argument }}:
    component: {{require.component}}
    , instance: {{require.instance}}
    , scope: {% if require.scope_name %}{{require.scope_name|lower}}{% else %}None{% endif %}
    {% if require.can %}, can: {{require.can|join(', ')}}{% endif %}
{% endfor %}
{% endif %}

{% if component.methods -%}
Methods
^^^^^^^
{% for method in component.methods %}
.. _method-{{method.path}}:

.. automethod:: {{method.path}}
{% endfor %}
{% endif %}
{%- endmacro %}

{########### formats an endpoint ##########}
{% macro format_endpoint(endpoint, headersize) -%}
.. _endpoint-{{endpoint.name}}:

{{ header(endpoint.name|capitalize, headersize) }}
{{ endpoint.description }}

{% for message in endpoint.messages %}
{{ format_message_short(message) }}
{% endfor %}
{%- endmacro %}

{########### formats an endpoint to short description with link to complete description ##########}
{% macro format_endpoint_short(endpoint) -%}
{{ endpoint.name|ref('endpoint') }}:
    {{ endpoint.short_description|indent(4)|replace("    \n", "\n") }}
{% endmacro %}

{########### formats a message ##########}
{% macro format_message(message, headersize) -%}
.. _message-{{message.name}}:

{{ header(message.name, headersize) }}
{{ message.description }}

{% for endpoint in message.endpoints %}
{{ format_endpoint_short(endpoint) }}
{% endfor %}
{%- endmacro %}

{########### formats a message to short description with link to complete description ##########}
{% macro format_message_short(message) -%}
{{ message.name|ref('message') }}:
    {{ message.short_description|indent(4)|replace("    \n", "\n") }}
{%- endmacro %}
