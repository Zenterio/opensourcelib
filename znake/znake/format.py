"""
Znake provides facilities for automatic source code formatting.

.. autofunction:: format
.. autofunction:: isort
.. autofunction:: yapf
"""

from invoke import Collection, task

from znake import tools


@task
def yapf(ctx):
    """
    Automatically format source code using the `yapf` utility.

    For more information about the `yapf` utility, please see:

    * https://pypi.python.org/pypi/yapf
    """
    ctx.run(tools.render_yapf_apply(ctx))


@task
def isort(ctx):
    """
    Automatically format import statements using the `isort` utility.

    For more information about the `isort` utility, please see:

    * https://pypi.python.org/pypi/isort
    """
    ctx.run(tools.render_isort_apply(ctx))


@task(default=True, pre=[yapf, isort])
def format(ctx):
    """Apply all automatic source code formatting."""
    pass


def get_namespace(config):
    namespace = Collection('format')
    namespace.add_task(yapf)
    namespace.add_task(isort)
    namespace.add_task(format)
    return namespace
