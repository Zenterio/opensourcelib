"""
Znake provides facilities for creating Debian packages.

Each Debian package targets a specific architecture and environment.
Each environment is defined as a Docker container and is assumed to have all
neccessary tools pre-installed.

.. autofunction:: deb
.. autofunction:: clean
"""

import os
from textwrap import dedent

from invoke import Collection, call, task

from .doc import doc
from .util import render_template, run, skip_if_up_to_date
from .venv import write_setup_py_file, write_version_file

# This directory is required by dpkg-buildpackage and is used during the
# packaging process.
DEBIAN_DPKG_DIR = 'debian'


@task(default=True)
def deb(ctx):
    """Build all Debian packages."""
    pass


@task
def clean(ctx):
    """Remove all Debian packaging build artifacts."""
    ctx.run('rm -rf {dir}'.format(dir=ctx.build_dir.debian_dir))
    ctx.run('rm -rf {dir}'.format(dir=ctx.build_dir.dist_dir))
    ctx.run('rm -rf {dir}'.format(dir=DEBIAN_DPKG_DIR))


@task(pre=[doc])
def create_debian_directory(ctx):
    ctx.run('rm -rf {dir}'.format(dir=ctx.build_dir.debian_dir))
    ctx.run('mkdir -p {dir}'.format(dir=ctx.build_dir.debian_dir))
    ctx.run('mkdir -p {dir}'.format(dir=DEBIAN_DPKG_DIR))
    _copy_include(ctx)
    _copy_documentation(ctx)
    _write_control_file(ctx)
    _write_compat_file(ctx)
    _write_changelog_file(ctx)
    _write_rules_file(ctx)
    _write_source_options_file(ctx)
    _write_triggers_file(ctx)
    _write_links_file(ctx)
    _write_install_file(ctx)
    _copy_scripts(ctx)


@task(pre=[create_debian_directory, write_version_file, write_setup_py_file])
def create_deb(ctx, target):
    """Build a Debian package."""
    skip_if_up_to_date(
        '{dist_dir}/{codename}'.format(
            dist_dir=ctx.build_dir.dist_dir, codename=target['codename']))(_build_debian_package)(
                ctx, target)


def generate_debian_packaging_tasks(target):

    @task(name=target['name'], pre=[call(create_deb, target=target)])
    def create_deb_for_target(ctx, target=target):
        """Build a Debian package for a specific target."""
        pass

    deb.pre.append(call(create_deb_for_target, target=target))

    return create_deb_for_target


def generate_debug_tasks(target):

    @task(name=target['name'])
    def run_deb_debug(ctx, target=target):
        """Start an interactive shell in the deb build environment."""
        run(ctx, target['image'], '/bin/bash', interactive=True)

    return run_deb_debug


def _render_copy_documentation_command(target, ctx):
    return dedent(
        """\
        mkdir -p {debian_dir}/doc/{target}/pdf &&
        cp {doc_dir}/{target}/pdf/{target}.pdf {debian_dir}/doc/{target}/pdf &&
        cp -r {doc_dir}/{target}/html {debian_dir}/doc/{target}/""").format(
            debian_dir=ctx.build_dir.debian_dir, doc_dir=ctx.build_dir.doc_dir, target=target)


def _render_copy_include_command(include_source, ctx):
    return dedent(
        """\
        mkdir -p {debian_dir}/{include_dir} &&
        cp -r {include} {debian_dir}/{include}""").format(
            debian_dir=ctx.build_dir.debian_dir,
            include_dir=os.path.dirname(include_source),
            include=include_source)


def _copy_include(ctx):
    """Include files into the debian package."""
    for include in ctx.znake.deb.include:
        ctx.run(_render_copy_include_command(include['source'], ctx))


def _copy_documentation(ctx):
    for target in ctx.znake.deb.doc:
        ctx.run(_render_copy_documentation_command(target, ctx))


def _render_copy_scripts_command(package, ctx):
    return 'cp ./znaketools/debian_config/* {debian_dir} || true'.format(
        debian_dir=ctx.build_dir.debian_dir)


def _copy_scripts(ctx):
    if os.path.exists('znaketools/debian_config'):
        ctx.run(_render_copy_scripts_command(ctx.znake.deb.package, ctx))


def _render_compat_file(ctx):
    return '9'


def _write_compat_file(ctx):
    with open('{debian_dir}/compat'.format(debian_dir=ctx.build_dir.debian_dir), 'w') as f:
        f.write(_render_compat_file(ctx))


def _render_control_file(ctx):
    template_string = dedent(
        """\
        Source: {{package}}
        Section: python
        Priority: extra
        Maintainer: {{maintainer}} <{{maintainer_email}}>
        Standards-Version: 3.9.5

        Package: {{package}}
        Architecture: any
        Pre-Depends: python3.6-minimal | python3.6
        Depends: {{dependencies}}{% raw %}${python:Depends}, ${misc:Depends}{% endraw %}
        Description: {{short_description}}
          {{long_description|indent(2)}}
        """)

    if ctx.znake.deb.dependencies:
        dependencies = ', '.join(ctx.znake.deb.dependencies) + ', '
    else:
        dependencies = ''

    return render_template(
        template_string,
        package=ctx.znake.deb.package,
        maintainer=ctx.znake.info.maintainer,
        maintainer_email=ctx.znake.info.maintainer_email,
        dependencies=dependencies,
        short_description=ctx.znake.info.short_description,
        long_description=ctx.znake.info.long_description)


def _write_control_file(ctx):
    with open('{debian_dir}/control'.format(debian_dir=ctx.build_dir.debian_dir), 'w') as f:
        f.write(_render_control_file(ctx))


def _render_changelog_file(ctx):
    if not ctx.znake.info.changelog:
        raise Exception('Changelog must not be empty')

    template_string = dedent(
        """\
        {% for entry in changelog -%}
        {{package}} ({{entry.version}}) unstable; urgency=low
        {% for change in entry.changes %}
          * {{change}}
        {%- endfor %}

         -- {{maintainer}} <{{maintainer_email}}>  {{entry.date}}

        {% endfor %}
        """)
    return render_template(
        template_string,
        package=ctx.znake.deb.package,
        changelog=ctx.znake.info.changelog,
        maintainer=ctx.znake.info.maintainer,
        maintainer_email=ctx.znake.info.maintainer_email).strip()


def _write_changelog_file(ctx):
    with open('{debian_dir}/changelog'.format(debian_dir=ctx.build_dir.debian_dir), 'w') as f:
        f.write(_render_changelog_file(ctx))


def _render_rules_file(package, ctx):
    template_string = dedent(
        """\
        #!/usr/bin/make -f

        %:
        \tdh $@ --with python-virtualenv --python /usr/bin/python3.6 --sourcedirectory={{package}}

        override_dh_shlibdeps:
        \tdh_shlibdeps --exclude=numpy --exclude=matplotlib --exclude=pandas --exclude=selenium

        override_dh_strip:
        \tdh_strip --no-automatic-dbgsym || dh_strip

        override_dh_virtualenv:
        \t{{dh_virtualenv_command}}""")

    # This is not part of the template as flake8 thinks the line gets long.
    # If a noqa comment is added the long line is allowed, but yapf starts
    # compaining about formatting instead, wanting to put the noqa comment on
    # its own line.
    dh_virtualenv_command = (
        'dh_virtualenv --python /usr/bin/python3.6 '
        '--upgrade-pip '
        '--preinstall fastentrypoints==0.10 '
        '--builtin-venv '
        '--index-url http://pip.zenterio.lan/simple '
        '--extra-index-url https://pypi.org/simple '
        '--extra-pip-arg --trusted-host '
        '--extra-pip-arg pip.zenterio.lan '
        '--requirements {requirements_dir}/requirements.txt'.format(
            requirements_dir=ctx.build_dir.requirements_dir))

    return render_template(
        template_string, package=package, dh_virtualenv_command=dh_virtualenv_command)


def _write_rules_file(ctx):
    with open('{debian_dir}/rules'.format(debian_dir=ctx.build_dir.debian_dir), 'w') as f:
        f.write(_render_rules_file(ctx.znake.info.package, ctx))


def _render_write_source_options_file_command(ctx):
    return (
        'mkdir {debian_dir}/source && '
        'echo \'tar-ignore = "*"\' > {debian_dir}/source/options'
    ).format(debian_dir=ctx.build_dir.debian_dir)


def _write_source_options_file(ctx):
    ctx.run(_render_write_source_options_file_command(ctx))


def _render_triggers_file(ctx):
    triggers_file_contents = dedent(
        """\
        # Register interest in Python interpreter changes (Python 2 for now); and
        # don't make the Python package dependent on the virtualenv package
        # processing (noawait)
        interest-noawait /usr/bin/python3.4
        interest-noawait /usr/bin/python3.5
        interest-noawait /usr/bin/python3.6

        # Also provide a symbolic trigger for all dh-virtualenv packages
        interest dh-virtualenv-interpreter-update
        """)
    return triggers_file_contents


def _write_triggers_file(ctx):
    package = ctx.znake.deb.package
    path = '{debian_dir}/{package}.triggers'.format(
        debian_dir=ctx.build_dir.debian_dir, package=package)
    with open(path, 'w') as f:
        f.write(_render_triggers_file(ctx))


def _render_links_file(ctx):
    template_string = dedent(
        """\
        {%- for item in links -%}
        {{item.target}} {{item.link}}
        {% endfor -%}
        """)
    links = ctx.znake.deb.links
    return render_template(template_string, links=links)


def _write_links_file(ctx):
    package = ctx.znake.deb.package
    path = '{debian_dir}/{package}.links'.format(
        debian_dir=ctx.build_dir.debian_dir, package=package)
    with open(path, 'w') as f:
        f.write(_render_links_file(ctx))


def _render_install_file(ctx):
    """
    Create the content of the install file.

    This contains items from deb.install, deb.doc and deb.include.
    """
    package = ctx.znake.deb.package

    template_string = dedent(
        """\
        {%- for item in install -%}
        debian/{{item.source}} {{item.target}}
        {% endfor -%}
        """)
    install = []
    install.extend(ctx.znake.deb.install)
    if ctx.znake.deb.doc:
        install.append({'source': 'doc', 'target': '/opt/venvs/{package}/'.format(package=package)})
    install.extend(ctx.znake.deb.include)
    return render_template(template_string, install=install)


def _write_install_file(ctx):
    package = ctx.znake.deb.package
    path = '{debian_dir}/{package}.install'.format(
        debian_dir=ctx.build_dir.debian_dir, package=package)
    with open(path, 'w') as f:
        f.write(_render_install_file(ctx))


def _render_build_debian_package_command(ctx, target):
    template_string = dedent(
        """\
        cp -R {{debian_dir}}/* ./debian/ &&
        sed -i s/\\({{version}}\\)/\\({{version}}+{{build_number}}+{{codename}}\\)/g ./debian/changelog &&
        dpkg-buildpackage -us -uc -a{{architecture}} &&
        mkdir -p {{dist_dir}}/{{codename}} &&
        mv -f ../*.deb {{deb_path}} &&
        touch {{dist_dir}}/{{codename}} """)
    name = ctx.znake.deb.package
    version = ctx.znake.info.changelog[0]['version']
    build_number = os.getenv('BUILD_NUMBER', 0)
    architecture = target['architecture']
    codename = target['codename']

    deb_path = '{dist_dir}/{codename}/{name}_{version}+{build_number}+{codename}_{architecture}.deb'.format(
        dist_dir=ctx.build_dir.dist_dir,
        codename=codename,
        name=name,
        version=version,
        build_number=build_number,
        architecture=architecture)

    return render_template(
        template_string,
        name=name,
        version=version,
        build_number=build_number,
        architecture=architecture,
        codename=codename,
        deb_path=deb_path,
        debian_dir=ctx.build_dir.debian_dir,
        dist_dir=ctx.build_dir.dist_dir)


def _build_debian_package(ctx, target):
    run(ctx, target['image'], _render_build_debian_package_command(ctx, target))


def get_namespace(config):
    namespace = Collection('deb')

    debug_namespace = Collection('debug')
    for target in config.znake.deb.targets:
        namespace.add_task(generate_debian_packaging_tasks(target))
        debug_namespace.add_task(generate_debug_tasks(target))

    namespace.add_collection(debug_namespace)

    if config.znake.deb.targets:
        namespace.add_task(deb)
        namespace.add_task(clean)
    return namespace
