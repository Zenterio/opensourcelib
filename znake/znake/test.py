"""
Znake provides facilities for running tests.

.. autofunction:: test
.. autofunction:: test_all
"""
from invoke import Collection, call, task

from .util import generate_test_command, run
from .venv import create_venv


@task(default=True)
def test(ctx):
    """Run the unit tests in the local environment."""
    pass


@task(name='all')
def test_all(ctx):
    """Run the unit tests in all applicable environments."""
    pass


def generate_test_tasks(target):

    @task(name=target['name'].replace('.', '-'), pre=[call(create_venv, target=target)])
    def run_test(ctx, target=target):
        """Run unit tests in the target environment."""
        command = generate_test_command(ctx, ctx.znake.test, target['name'])
        run(ctx, target['image'], command, use_venv=True)

    if target['image'] == 'local':
        test.pre.append(call(run_test, target=target))
    test_all.pre.append(call(run_test, target=target))

    return run_test


# Nosetest discovers that this is a test because it contains the word "test".
generate_test_tasks.__test__ = False  # It is not a test.


def generate_debug_tasks(target):

    @task(name=target['name'])
    def run_test_debug(ctx, target=target):
        """Start an interactive shell in the test environment."""
        run(ctx, target['image'], '/bin/bash', interactive=True, force_volume=True)

    return run_test_debug


def get_namespace(config):
    namespace = Collection('test')

    debug_namespace = Collection('debug')
    for target in config.znake.test.targets:
        namespace.add_task(generate_test_tasks(target))
        debug_namespace.add_task(generate_debug_tasks(target))

    namespace.add_collection(debug_namespace)

    if config.znake.test.targets:
        namespace.add_task(test)
        namespace.add_task(test_all)

    return namespace
