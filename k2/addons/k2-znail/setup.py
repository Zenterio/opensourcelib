import os

from setuptools import find_packages, setup

setup(
    name='k2-znail',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='K2 Znail',
    long_description=(
        'K2 addon to interact with a Znail - see https://github.com/znailnetem/znail'),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'httpretty<1.0,>=0',
        'requests<3.0,>=2',
    ],
    entry_points={
        'k2.addons': [
            'znail = znail.znail:Znail',
            'znailcc = znail.znailcc:ZnailConnectionCheck',
        ],
    },
)
