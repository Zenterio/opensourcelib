import os

from setuptools import find_packages, setup

setup(
    name='k2-addon',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='The addon K2 addon.',
    long_description=('The K2 addon addon provides utilities for creating addons.'),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'pypsi<2.0,>=1',
        'jinja2<3.0,>=2',
        'python-editor<2.0,>=1',
    ],
    entry_points={
        'k2.addons': [
            'addon = addon.addon:AddonExtension',
        ],
    },
)
