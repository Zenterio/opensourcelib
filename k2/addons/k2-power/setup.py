import os

from setuptools import find_packages, setup

setup(
    name='k2-power',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Addons for interacting with powerswitches and meters.',
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=['requests'],
    entry_points={
        'k2.addons': [
            'dummypowermeter = dummypowermeter.dummypowermeter:DummyPowerMeter',
            'dummypowermeterframeworkextension = dummypowermeter.dummypowermeter:DummyPowerMeterFrameworkExtension',
            'powermetercommand = powermeter.powermetercommand:PowerMeterExtension',
            'powermetercc = powermeter.powermetercc:PowerMeterConnectionCheck',
            'powercommand = powerswitch.powercommand:PowerSwitchExtension',
            'powerswitchcc = powerswitch.powerswitchcc:PowerSwitchConnectionCheck',
            'powermonitor = powermonitor.powermonitor:PowerConsumptionMonitor',
        ],
    },
)
