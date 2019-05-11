"""
Znake provides facilities for generating documentation.

By default, Sphinx is used to generate both HTML and PDF versions of the documentation.
The generated documentation is available in the doc/build directory.
"""
from invoke import Collection, call, task

from znake.util import znake_tool_path

from .util import run, skip_if_up_to_date
from .venv import create


@task(default=True)
def doc(ctx):
    """Generate all documentation."""
    pass


@task
def clean(ctx):
    """Remove all generated documentation."""
    ctx.run('rm -rf {dir}'.format(dir=ctx.build_dir.doc_dir))


@task(pre=[create])
def doc_pre_commands(ctx):
    """Run commands prerequisite to generate the documentation."""
    for command in ctx.znake.doc.pre:
        run(ctx, 'local', command, use_venv=True)


def generate_doc_tasks(target):

    @task(pre=[create, doc_pre_commands])
    @skip_if_up_to_date(
        '{doc_dir}/{target}/html'.format(doc_dir='{doc_dir}', target=target['guide']))
    def html(ctx, target=target):
        """Generate HTML documentation."""
        run(
            ctx,
            'local',
            _render_generate_documentation_command(
                target['guide'], ctx, ctx.znake.doc.html_command_pattern),
            use_venv=True)

    @task
    def clean_html(ctx, target=target):
        """Remove generated HTML documentation."""
        ctx.run(_render_remove_html_documentation_command(target['guide'], ctx))

    @task(pre=[create, doc_pre_commands])
    @skip_if_up_to_date(
        '{doc_dir}/{target}/pdf'.format(doc_dir='{doc_dir}', target=target['guide']))
    def pdf(ctx, target=target):
        """Generate PDF documentation."""
        run(
            ctx,
            'local',
            _render_generate_documentation_command(
                target['guide'], ctx, ctx.znake.doc.pdf_command_pattern),
            use_venv=True)

    @task
    def clean_pdf(ctx, target=target):
        """Remove generated PDF documentation."""
        ctx.run(_render_remove_pdf_documentation_command(target['guide'], ctx))

    doc.pre.append(call(html, target=target))
    doc.pre.append(call(pdf, target=target))

    clean.pre.append(call(clean_html, target=target))
    clean.pre.append(call(clean_pdf, target=target))

    namespace = Collection(target['guide'])
    namespace.add_task(html)
    namespace.add_task(clean_html)
    namespace.add_task(pdf)
    namespace.add_task(clean_pdf)
    return namespace


def _render_generate_documentation_command(target, ctx, command_pattern):
    combined_kwargs = {}
    combined_kwargs.update(ctx.build_dir.templating_kwargs())

    return command_pattern.format(
        sphinx_build=znake_tool_path('sphinx-build'), target=target, **combined_kwargs)


def _render_remove_html_documentation_command(target, ctx):
    return 'rm -rf {doc_build_dir}/{target}/html'.format(
        doc_build_dir=ctx.build_dir.doc_dir, target=target)


def _render_remove_pdf_documentation_command(target, ctx):
    return 'rm -rf {doc_build_dir}/{target}/pdf'.format(
        doc_build_dir=ctx.build_dir.doc_dir, target=target)


def get_namespace(config):
    namespace = Collection('doc')
    for target in config.znake.doc.targets:
        namespace.add_collection(generate_doc_tasks(target))
    if config.znake.doc.targets:
        namespace.add_task(doc)
        namespace.add_task(clean)
    return namespace
