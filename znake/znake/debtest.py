"""
Znake provides facilities for running debtests.

.. autofunction:: debtest
.. autofunction:: debtest_all
"""
from invoke import Collection, call, task

from .deb import create_deb
from .util import generate_test_command, run


@task(default=True)
def debtest(ctx):
    """Run debtests for all non local targets."""
    pass


@task(name='all')
def debtest_all(ctx):
    """Run debtests for all environments including local."""
    pass


def generate_debtest_tasks(target):

    @task(name=target['name'], pre=[call(create_deb, target=target)])
    def run_debtest(ctx, target=target):
        """Run debtests in a specific target environment."""

        command = generate_test_command(ctx, ctx.znake.debtest, target['name'])
        install_dependencies_command = generate_install_dependencies_command(
            ctx.znake.debtest.get('install_packages', []))
        run(
            ctx, target['test_image'], (
                'sudo apt-get update && '
                '{install_dependencies_command}'
                'sudo DEBIAN_FRONTEND=noninteractive gdebi --quiet --non-interactive '
                '$(ls -t {dist_dir}/{codename}/*.deb | head -1) && '
                '{command}').format(
                    install_dependencies_command=install_dependencies_command,
                    dist_dir=ctx.build_dir.dist_dir,
                    codename=target['codename'],
                    command=command))

    if target['test_image'] != 'local':
        debtest.pre.append(call(run_debtest, target=target))
    debtest_all.pre.append(call(run_debtest, target=target))

    return run_debtest


def generate_debtest_debug_tasks(target):

    @task(name=target['name'])
    def run_debtest_debug(ctx, target=target):
        """Start an interactive shell in the debtest environment."""
        run(ctx, target['test_image'], '/bin/bash', interactive=True)

    return run_debtest_debug


def generate_install_dependencies_command(packages):
    if len(packages) == 0:
        return ''
    return (
        'sudo apt-get --yes '
        '-o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" '
        'install {packages} && ').format(packages=' '.join(packages))


def get_namespace(config):
    namespace = Collection('debtest')

    debug_namespace = Collection('debug')
    for target in config.znake.deb.targets:
        if 'test_image' in target:
            namespace.add_task(generate_debtest_tasks(target))
            debug_namespace.add_task(generate_debtest_debug_tasks(target))

    namespace.add_collection(debug_namespace)

    if config.znake.deb.targets:
        namespace.add_task(debtest)
        namespace.add_task(debtest_all)
    return namespace
