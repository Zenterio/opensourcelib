{% import 'macros.rst' as macros %}

.. _changelog:

{{ macros.h1('Changelog'|capitalize) }}

{% for item in changelog %}

{{ macros.h2(item.version) }}
{{ item.short_date }}

{% for change in item.changes %}
* {{ change }}

{% endfor %}

{% endfor %}