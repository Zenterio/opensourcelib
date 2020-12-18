import importlib
import inspect
import os


def get_file_path_to_module(module_name):
    return os.path.dirname(inspect.getfile(importlib.import_module(module_name)))
