import os

from setuptools import find_packages, setup

setup(
    name='k2-gude',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='K2 Gude Power Control',
    long_description=(
        'Interact with Gude Power Control unit.'),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'requests<3.0,>=2',
    ],
    entry_points={
        'k2.addons': [
            'gudepowerswitch = gudepowercontrol.gudepowerswitch:GudePowerSwitchExtension',
            'gudepowermeter = gudepowercontrol.gudepowermeter:GudePowerMeterExtension',
            'gudeframework = gudepowercontrol.gudecommand:GudeFrameworkExtension',
        ],
    },
)
