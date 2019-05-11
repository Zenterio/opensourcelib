import inspect
import importlib
import os


def data_file(rel_path):
    return os.path.join(zpider_package_dir(), 'data', rel_path)


def zpider_package_dir():
    return os.path.dirname(inspect.getfile(importlib.import_module('zpider')))
