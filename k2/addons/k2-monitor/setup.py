import os

from setuptools import find_packages, setup

setup(
    name='k2-monitor',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Monitors resources and generates metrics.',
    long_description=(
        (
            'Monitors and generates metrics related to one or more SUTs. '
            'Each SUT is monitored by periodically performing some measurement.')),
    maintainer='Zenterio AB',
    maintainer_email='engineering.services@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[''],
    entry_points={
        'k2.addons': [
            'monitor = monitor.monitor:Monitor',
        ],
    },
)
