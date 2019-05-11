import sys
from contextlib import contextmanager

from coverage import Coverage

from zaf.builtin.unittest.packages import in_any_package


@contextmanager
def coverage(
        packages, output_stream=sys.stdout, coverage_file=None, xml_enabled=None, xml_file=None):
    """
    Context manager that activates coverage on the specified packages.

    Modules in the packages that are already loaded are removed and nosetest will load
    them again with coverage instrumentation when they are needed.

    :param packages: list of packages
    :param output_stream: the stream to write the results to
    :param coverage_file: the coverage file. If not specified coverage will use the default .coverage file
    :param xml_enabled: enable XML coverage report
    :param xml_file: the XML coverage report file. If not specified coverage will use the defualt coverage.xml file
    :return: instance of coverage.Coverage
    """
    source = {}
    for module_name, module in [(module_name, module)
                                for module_name, module in list(sys.modules.items())
                                if in_any_package(module_name, packages)]:
        source[module_name] = module
        del sys.modules[module_name]

    cover = Coverage(data_file=coverage_file, auto_data=False, branch=False)
    cover.combine()
    cover.erase()
    cover.start()
    yield cover

    for module_name, module in [(module_name, module)
                                for module_name, module in list(sys.modules.items())
                                if in_any_package(module_name, packages)]:
        source[module_name] = module

    cover.stop()
    cover.combine()
    cover.save()
    cover.report(list(source.values()), file=output_stream, show_missing=True)

    if xml_enabled:
        cover.xml_report(list(source.values()), xml_file)
