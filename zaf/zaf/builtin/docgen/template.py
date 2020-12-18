def render_sphinx_template(
        template_name, package='zaf.builtin.docgen', template_dir='templates', **kwargs):
    import jinja2
    env = jinja2.Environment(loader=jinja2.PackageLoader(package, template_dir), )
    env.filters['ref'] = create_reference
    return env.get_template(template_name).render(**kwargs)


def create_reference(name, prefix):
    return ':ref:`{prefix}-{name}`'.format(prefix=prefix, name=name.replace(' ', '_'))
