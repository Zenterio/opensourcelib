import os

from setuptools import find_packages, setup

setup(
    name='k2-healthcheck',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='K2 SUT Health check',
    long_description=('Event definition and interface for SUT health checking.'),
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
            'healthcheck = healthcheck.healthcheck:HealthMonitor',
        ],
    },
)
