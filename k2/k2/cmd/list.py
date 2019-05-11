"""Provides the *list* command that can list testcases using one or more test sources."""

from textwrap import dedent

from zaf.commands.command import CommandId
from zaf.extensions.extension import FrameworkExtension
from zaf.utils.jinja import render_template

from k2.finder import FIND_TEST_CASES, FINDER_ENDPOINT


def test_list(core):
    """
    List test cases for the specified test sources, files, modules classes etc.

    Example to run with multiple files::

        zk2 list path/to/test_1.py path/to/test_2.py
    """
    tests = []
    for find_result in core.messagebus.send_request(FIND_TEST_CASES, FINDER_ENDPOINT).wait():
        tests.extend(find_result.result())
    print(format_result(tests))


def format_result(tests):
    template_string = dedent(
        """\
        {%- for test in tests %}
        {{test.name}}
          {%- for line in test.description.splitlines() %}
          {{line}}
          {%- endfor %}
        {% endfor %}
        """)
    return render_template(template_string, tests=tests)


LIST_COMMAND = CommandId('list', test_list.__doc__, test_list, config_options=[])


@FrameworkExtension(name='listcommand', commands=[LIST_COMMAND])
class ListCommand():
    """Provides the list command."""

    def __init__(self, config, instances):
        pass
