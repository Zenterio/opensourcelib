import os

from setuptools import find_packages, setup

setup(
    name='k2-networking',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='K2 network utils',
    long_description=('Components to handle network related.'),
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
            'networking = networking.networking:Networking',
        ],
    },
)
