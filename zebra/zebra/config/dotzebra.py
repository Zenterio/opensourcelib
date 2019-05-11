"""
Extension providing the support for .zebra files.

see :ref:`dot_zebra` for more information.
"""
import os

from zaf.builtin.config.loader import _recursively_load_configuration
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension


@FrameworkExtension(
    'dotzebra',
    load_order=21,
)
class DotZebraExtension(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        dot_zebra_file = self.find_zebra_file(os.getcwd())
        if dot_zebra_file:
            return _recursively_load_configuration(dot_zebra_file, 9)
        else:
            return ExtensionConfig({}, 9)

    def find_zebra_file(self, start_dir):
        dir = start_dir

        while dir != '/' and not os.path.exists(os.path.join(dir, '.zebra')):
            dir = os.path.dirname(dir)

        zebra_file = os.path.join(dir, '.zebra')
        if os.path.exists(zebra_file):
            return zebra_file
        else:
            return None
