from collections import namedtuple
from itertools import starmap

from voluptuous import REMOVE_EXTRA, All, Required, Schema

from debpacker.common.configparser import YAMLListConfigParser
from debpacker.common.utils import validate_deb_package_name

from .utils import DEFAULT_TOOLCHAIN_ROOT, ToolchainLink

ToolchainDefinition = namedtuple(
    'ToolchainDefinition',
    ['name', 'url', 'version', 'paths', 'toolchain_root', 'links', 'depends'])


def _validate_toolchain_definition(toolchain_data: dict):

    # noinspection PyPep8Naming
    def NotEmpty(iterable):
        if len(iterable) == 0:
            raise ValueError('The list may not be empty!')
        return iterable

    # noinspection PyPep8Naming
    def ConvertStringToList(data):
        if isinstance(data, list):
            return data
        elif isinstance(data, str):
            return [data]
        else:
            raise ValueError('Can only convert a single string to a list!')

    # noinspection PyPep8Naming
    def ConvertDictToToolchainLink(data: dict) -> [ToolchainLink]:
        return list(starmap(ToolchainLink, data.items()))

    # noinspection PyPep8Naming
    def ValidPackageName(value):
        validate_deb_package_name(value)
        return value

    schema = Schema(
        {
            Required('name'): str,
            Required('version'): str,
            Required('url'): str,
            Required('paths'): All(ConvertStringToList, [str], NotEmpty),
            Required('toolchain_root', default=DEFAULT_TOOLCHAIN_ROOT): str,
            Required('links', default=[]): All({
                str: str
            }, ConvertDictToToolchainLink),
            Required('depends', default=[]): All(ConvertStringToList, [str]),
        },
        extra=REMOVE_EXTRA)
    return schema(toolchain_data)


class ToolchainDefinitionsParser(YAMLListConfigParser):

    def __init__(self):
        super().__init__(ToolchainDefinition, _validate_toolchain_definition)
