import os

from setuptools import find_packages, setup

setup(
    name='k2-multirunner',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='K2 Multirunner',
    long_description=(
        'Alternative runner to the built-in runner. Allows multiple sub-runners to collectively generate a vertict.'
    ),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[''],
    entry_points={
        'k2.addons': [
            'multirunner = multirunner.multirunner:MultiRunner',
        ],
    },
)
