def render_sphinx_template(template_name, **kwargs):
    import jinja2
    env = jinja2.Environment(loader=jinja2.PackageLoader('zaf.builtin.docgen', 'templates'), )
    env.filters['ref'] = create_reference
    return env.get_template(template_name).render(**kwargs)


def create_reference(name, prefix):
    return ':ref:`{prefix}-{name}`'.format(prefix=prefix, name=name.replace(' ', '_'))
