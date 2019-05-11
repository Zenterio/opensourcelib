from zaf.config.options import ConfigOptionId, Path
from zaf.application.context import ApplicationContext

ALL_EXTENSIONS = ConfigOptionId(
    'all',
    'Extensions',
    multiple=True,
    entity=True,
    namespace='ext',
    application_contexts=ApplicationContext.INTERNAL)

ENABLED_EXTENSIONS = ConfigOptionId(
    'enabled',
    'Enabled extensions (automatically provided option)',
    multiple=True,
    entity=True,
    namespace='ext',
    application_contexts=[ApplicationContext.INTERNAL])

DISABLEABLE_EXTENSIONS = ConfigOptionId(
    'disableable',
    'Extensions',
    multiple=True,
    entity=True,
    namespace='ext',
    application_contexts=[ApplicationContext.INTERNAL])

EXTENSION_ENABLED = ConfigOptionId(
    'enabled',
    'Enable extension',
    at=DISABLEABLE_EXTENSIONS,
    option_type=bool,
    default=True,
    hidden=True,
    application_contexts=[ApplicationContext.EXTENDABLE])

EXTENSIONS_DEFAULT_ENABLED = ConfigOptionId(
    'default.enabled',
    'Extensions should be enabled by default',
    option_type=bool,
    default=True,
    namespace='ext',
    hidden=True,
    application_contexts=[ApplicationContext.EXTENDABLE])

PLUGINS_PATHS = ConfigOptionId(
    'plugins.paths',
    'Path to load plugins from. Can be given multiple times to load from multiple paths',
    option_type=Path(exists=True),
    multiple=True,
    default=(),
    application_contexts=[ApplicationContext.EXTENDABLE])
