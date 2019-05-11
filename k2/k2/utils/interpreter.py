"""Provides utilities for querying the Python runtime."""

import sys
from collections import namedtuple

python_location = namedtuple('python_location', ['module', 'name'])


def find_where_instance_is_defined(obj):
    """
    Attempt to figure out if an object is stored in a global variable.

    Returns a list of all places the object was found.
    """
    return [
        python_location(module_name, variable_name)
        for module_name, module_instance in list(sys.modules.items())
        if module_instance.__dict__ is not None
        for variable_name, variable_value in module_instance.__dict__.items()
        if variable_value is obj
    ]
