"""Provides utilities for generating the files that are part of an addon."""

# flake8: noqa

from textwrap import dedent

from k2.utils.interpreter import find_where_instance_is_defined


def generate_setup_py_file(addon_info):
    template_string = dedent(
        r"""
        from setuptools import find_packages, setup
        import os

        setup(
            name='{{addon_info.package_name}}',
            version='{{addon_info.version}}' + os.getenv('BUILD_NUMBER', '0'),

            description='{{addon_info.description}}',
            long_description=(
                {% for line in addon_info.long_description.split('\n') -%}
                    '{{line}}'
                {% endfor -%}
            ),

            maintainer='{{addon_info.maintainer}}',
            maintainer_email='{{addon_info.maintainer_email}}',
            license='© 2018 Zenterio AB All rights reserved',

            packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*', 'systest']),
            install_requires=['{{addon_info.install_requires}}'],

            entry_points={
                'k2.addons': [
                    '{{addon_info.package_name}} = {{addon_info.package_name}}.{{addon_info.package_name}}:{{addon_info.entrypoint}}',
                ],
            },
        )

        """)
    return render_jinja_template(template_string, addon_info=addon_info)


def generate_framework_extension_entrypoint(addon_info):
    template_string = dedent(
        r'''
        """
        TODO: Write a module docstring for the '{{addon_info.package_name}}' addon.

        {{addon_info.description}}

        {% for line in addon_info.long_description.split('\n') -%}
        {{line}}
        {% endfor %}

        This text will be added to the extensions chapter of the K2 user guide.
        """

        import logging

        from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name


        logger = logging.getLogger(get_logger_name('k2', '{{addon_info.package_name}}'))
        logger.addHandler(logging.NullHandler())


        @FrameworkExtension(
            name='{{addon_info.package_name}}',
            config_options=[],
            endpoints_and_messages={}
        )
        class {{addon_info.entrypoint}}(AbstractExtension):
            """
            TODO: Write docstring for the '{{addon_info.package_name}}' addon entrypoint.

            This text will be displayed when asking K2 for help about this addon.
            """

            def __init__(self, config, instances):
                pass

        ''')
    return render_jinja_template(template_string, addon_info=addon_info)


def generate_command_extension_entrypoint(addon_info):
    template_string = dedent(
        r'''
        """
        TODO: Write a module docstring for the '{{addon_info.package_name}}' addon.

        {{addon_info.description}}

        {% for line in addon_info.long_description.split('\n') -%}
        {{line}}
        {% endfor %}

        This text will be added to the extensions chapter of the K2 user guide.
        """

        import logging

        from {{command_info.module}} import {{command_info.name}}
        from zaf.extensions.extension import CommandExtension, AbstractExtension, get_logger_name


        logger = logging.getLogger(get_logger_name('k2', '{{addon_info.package_name}}'))
        logger.addHandler(logging.NullHandler())


        @CommandExtension(
            name='{{addon_info.package_name}}',
            extends=[{{command_info.name}}],
            config_options=[],
            endpoints_and_messages={}
        )
        class {{addon_info.entrypoint}}(AbstractExtension):
            """
            TODO: Write docstring for the '{{addon_info.package_name}}' addon entrypoint.

            This text will be displayed when asking K2 for help about this addon.
            """

            def __init__(self, config, instances):
                pass

        ''')
    command_info = find_where_instance_is_defined(addon_info.command)[0]
    return render_jinja_template(template_string, addon_info=addon_info, command_info=command_info)


def generate_initial_unittest(addon_info):
    template_string = dedent(
        r'''
        from unittest import TestCase

        from ..{{addon_info.package_name}} import {{addon_info.entrypoint}}


        class Test{{addon_info.entrypoint}}(TestCase):

            def test_{{addon_info.package_name}}(self):
                """TODO: Description of the purpose of this test case."""
                raise NotImplementedError('Do not forget to write some tests!')

        ''')
    return render_jinja_template(template_string, addon_info=addon_info)


def render_jinja_template(template_string, **kwargs):
    from zaf.utils.jinja import render_template

    return render_template(template_string, **kwargs)
