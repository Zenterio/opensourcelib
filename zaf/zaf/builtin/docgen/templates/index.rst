{{ application_name|capitalize }} User Guide
{{ '=' * application_name|length }}===========

.. toctree::
    :maxdepth: 2
    :caption: Contents:
    :glob:

    {% for index_entry in custom_index_entries %}
    {{ index_entry }}{% endfor %}
    command_list
    logging
    configuration
    {% if include_components %}components{% endif %}
    {% if include_endpoints_and_messages %}messages{% endif %}
    {% if include_components %}component_list{% endif %}
    config_option_id_list
    {% if include_endpoints_and_messages %}endpoint_list{% endif %}
    extension_list
    {% if include_endpoints_and_messages %}message_list{% endif %}
    {% if changelog %}changelog{% endif %}


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
