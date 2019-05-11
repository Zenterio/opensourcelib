{% import 'macros.rst' as macros %}
.. _list-components:

{{ macros.header('List of Components', 1) }}

.. toctree::
    :hidden:
    :glob:

    components/*

{% for component in components %}
{{ macros.format_component_short(component) }}
{% endfor %}
