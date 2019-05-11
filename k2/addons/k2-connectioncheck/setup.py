import os

from setuptools import find_packages, setup

setup(
    name='k2-connectioncheck',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Triggers connection checks',
    long_description=(
        'Triggers and interprets the result of connection checks and can trigger recovery of the SUT'
    ),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    entry_points={
        'k2.addons': [
            'connectioncheck = connectioncheck.connectioncheck:ConnectionCheck',
        ],
    },
)
