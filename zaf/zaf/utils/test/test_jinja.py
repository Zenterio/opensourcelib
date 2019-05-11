import unittest

from ..jinja import render_template


class TestRenderTemplate(unittest.TestCase):

    def test_render_template_without_kwargs(self):
        template_string = 'this is my template'
        rendered_template = render_template(template_string)
        self.assertEqual(template_string, rendered_template)

    def test_render_template_with_kwargs(self):
        template_string = '{{data}}'
        rendered_template = render_template(template_string, data='this is my data')
        self.assertEqual('this is my data', rendered_template)
