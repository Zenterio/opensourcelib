"""A configuration reader that merges the results of multiple configuration readers."""

from .config import merge_configs


class MultiConfigReader():

    def __init__(self, *args):
        self.readers = args

    def get_config(self):
        return merge_configs(*[r.get_config() for r in self.readers])
