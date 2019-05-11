import os


def get_template_path(name):
    return os.path.join(os.path.dirname(__file__), 'templates', name)
