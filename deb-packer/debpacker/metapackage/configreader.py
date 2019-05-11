import logging
from collections import namedtuple

from voluptuous import Any, Required, Schema

from debpacker.common.configparser import YAMLConfigParser

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

PackageConfig = namedtuple(
    'PackageConfig', [
        'name', 'version', 'long_description', 'short_description', 'dependencies', 'architecture',
        'distributions'
    ])


def _validate_package_config(data: dict):
    schema = Schema(
        {
            Required('name'): str,
            Required('version'): str,
            Required('long_description'): str,
            Required('short_description'): str,
            Required('dependencies'): list,
            Required('architecture', default='all'): Any('amd64', 'i686', 'any', 'all'),
            Required('distributions', default=[None]): [Any('trusty', 'xenial', 'bionic')]
        })
    return schema(data)


class PackageConfigParser(YAMLConfigParser):

    def __init__(self):
        super().__init__(PackageConfig, _validate_package_config)

    def parse(self, document) -> PackageConfig:
        return super().parse(document)
