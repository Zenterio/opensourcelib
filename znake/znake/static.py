"""
Znake provides facilities for static code analysis.

.. autofunction:: static
.. autofunction:: flake8
.. autofunction:: pydocstyle
.. autofunction:: yapf
.. autofunction:: isort
"""

from invoke import Collection, task

from znake import tools


@task()
def flake8(ctx):
    """
    Check PEP8 compliance using the `flake8` utility.

    For more information about PEP8 and the `flake8` utility, please see:

    * https://pypi.python.org/pypi/flake8
    * https://www.python.org/dev/peps/pep-0008/

    Uses the following flake8 plugins:

    * https://pypi.org/project/flake8-string-format/0.2.3/
    * https://pypi.org/project/flake8_tuple/0.2.13/
    * https://pypi.org/project/flake8-deprecated/1.3/
    * https://pypi.org/project/flake8-pep3101/1.2.1/
    * https://pypi.org/project/flake8-class-newline/1.6.0/
    * https://pypi.org/project/flake8-comprehensions/1.4.1/

    Not yet in use:

    * https://www.python.org/dev/peps/pep-0008/0.6.1/
     * Our k2 component injection naming convention goes against this, resulting in big changes
    * https://pypi.org/project/flake8-blind-except/0.1.1/
     * We do a lot of blind excepts and changing them is not trivial.

    Not used due to problems:

    * https://pypi.org/project/flake8-builtins/1.4.0
     * Having this installed breaks 'used but not declared' checks on u16.
    """
    ctx.run(tools.render_flake8_check(ctx))


@task
def pydocstyle(ctx):
    """
    Check docstring formatting using the `pydocstyle` utility.

    For more information about the `pydocstyle` utility, please see:

    * https://pypi.python.org/pypi/pydocstyle
    """
    ctx.run(tools.render_pydocstyle_check(ctx))


@task
def yapf(ctx):
    """
    Check source code formatting using the `yapf` utility.

    For more information about the `yapf` utility, please see:

    * https://pypi.python.org/pypi/yapf
    """
    ctx.run(tools.render_yapf_check(ctx))


@task
def isort(ctx):
    """
    Check import statement formatting using the `isort` utility.

    For more information about the `isort` utility, please see:

    * https://pypi.python.org/pypi/isort
    """
    ctx.run(tools.render_isort_check(ctx))


@task(default=True, pre=[flake8, pydocstyle, yapf, isort])
def static(ctx):
    """Run all static code analysis."""
    pass


def get_namespace(config):
    namespace = Collection('static')
    namespace.add_task(flake8)
    namespace.add_task(pydocstyle)
    namespace.add_task(yapf)
    namespace.add_task(isort)
    namespace.add_task(static)
    return namespace
