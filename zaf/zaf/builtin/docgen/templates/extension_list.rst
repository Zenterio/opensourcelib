{% import 'macros.rst' as macros %}
.. _list-extensions:

{{ macros.header('List of Extensions', 1) }}

.. toctree::
    :hidden:
    :glob:

    extensions/*

{% for extension in extensions %}
{{ macros.format_extension_short(extension) }}
{% endfor %}
