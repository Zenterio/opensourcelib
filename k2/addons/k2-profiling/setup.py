import os

from setuptools import find_packages, setup

setup(
    name='k2-profiling',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Profiles a K2 command invocation',
    long_description=(
        (
            'Collects a couple of metrics about the performance and behavior of the K2 execution.'
            'It is not a replacement for proper profiling using python\'s built in'
            'profiling tools, but is intended to be used to give a quick overview of K2 behavior.')
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
            'profiling = profiling.profiling:Profiling',
        ],
    },
)
