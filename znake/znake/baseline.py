"""
Znake provides facilities for updating baselines.

A baseline is configured with a source glob pattern and a target directory

.. autofunction:: update
.. autofunction:: clean
"""
from invoke import Collection, task


@task(default=True)
def update(ctx):
    for baseline in ctx.znake.baseline:
        ctx.run('mkdir -p {target}'.format(target=baseline['target']))
        ctx.run(
            'cp -r {source} -t {target}'.format(
                source=baseline['source'], target=baseline['target']))


@task
def clean(ctx):
    for _, target in ctx.znake.baseline:
        ctx.run('rm -rf {target}'.format(target=target))


def get_namespace(config):
    namespace = Collection('baseline')

    if config.znake.baseline:
        namespace.add_task(update)
        namespace.add_task(clean)
    return namespace
