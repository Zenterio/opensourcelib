"""
Provides *output.dir* config option that can be used when configuring output paths.

All users of the output.dir must ensure that the directory exists by using os.makedirs(OUTPUT_DIR, exists_ok=True)
to not create the output dir when it's not used.

Example::

    my.path: ${output.dir}/my_dir/my_file.ext
"""

from zaf.config.options import ConfigOption
from zaf.extensions.extension import FrameworkExtension

from . import OUTPUT_DIR


@FrameworkExtension(
    name='output', load_order=30, config_options=[ConfigOption(OUTPUT_DIR, required=True)])
class Output(object):
    """Handles output directory."""

    def __init__(self, config, instances):
        pass
