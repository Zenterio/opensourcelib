"""
Znake provides facilities for running systests.

.. autofunction:: systest
.. autofunction:: systest_all
"""

from invoke import Collection, call, task

from .util import generate_test_command, run
from .venv import create_venv


@task(default=True)
def systest(ctx):
    """Run the system tests in the local environment."""
    pass


@task(name='all')
def systest_all(ctx):
    """Run the system tests in all applicable environments."""
    pass


def generate_systest_tasks(target):

    @task(name=target['name'], pre=[call(create_venv, target=target)])
    def run_systest(ctx, target=target):
        """Run system tests in the target environment."""
        command = generate_test_command(ctx, ctx.znake.systest, target['name'])
        run(ctx, target['image'], command, use_venv=True)

    if target['image'] == 'local':
        systest.pre.append(call(run_systest, target=target))
    systest_all.pre.append(call(run_systest, target=target))

    return run_systest


def generate_debug_tasks(target):

    @task(name=target['name'])
    def run_systest_debug(ctx, target=target):
        """Start an interactive shell in the systest environment."""
        run(ctx, target['image'], '/bin/bash', interactive=True, force_volume=True)

    return run_systest_debug


def get_namespace(config):
    namespace = Collection('systest')

    debug_namespace = Collection('debug')
    for target in config.znake.systest.targets:
        namespace.add_task(generate_systest_tasks(target))
        debug_namespace.add_task(generate_debug_tasks(target))

    namespace.add_collection(debug_namespace)

    if config.znake.systest.targets:
        namespace.add_task(systest)
        namespace.add_task(systest_all)
    return namespace
