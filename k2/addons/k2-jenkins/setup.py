import os

from setuptools import find_packages, setup

setup(
    name='k2-jenkins',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Components for interacting with Jenkins.',
    long_description=(('Components for interacting with Jenkins.')),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'python-jenkins<2.0,>=1',
        'requests<3.0,>=2',
    ],
    entry_points={'k2.addons': ['jenkins = k2_jenkins.jenkins:JenkinsAddon']},
)
