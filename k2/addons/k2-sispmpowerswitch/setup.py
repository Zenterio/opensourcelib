import os

from setuptools import find_packages, setup

setup(
    name='k2-sispmpowerswitch',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Addon for interacting with Silver Shield PM devices.',
    maintainer='Patrik Dahlström',
    maintainer_email='risca@dalakolonin.se',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[],
    entry_points={
        'k2.addons': [
            'sispmpowerswitch = sispmpowerswitch.sispmpowerswitch:SispmPowerSwitch',
            'sispmpowerswitchframeworkextension = sispmpowerswitch.sispmpowerswitch:SispmPowerSwitchFrameworkExtension',
        ],
    },
)
