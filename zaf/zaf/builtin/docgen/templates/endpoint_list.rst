{% import 'macros.rst' as macros %}
.. _list-endpoints:

{{ macros.header('List of Endpoints', 1) }}

{%- for endpoint in endpoints %}
{{ macros.format_endpoint(endpoint, 2) }}
{% endfor %}
