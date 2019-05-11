"""Provides facilities for interacting with the jinja2 package."""


def render_template(template_string, **kwargs):
    import jinja2
    template = jinja2.Template(template_string)
    return template.render(**kwargs)
