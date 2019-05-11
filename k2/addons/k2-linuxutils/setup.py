import os

from setuptools import find_packages, setup

setup(
    name='k2-linuxutils',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Utilities specialized for the Linux operating system.',
    long_description=(
        (
            'Provides utilities, such as monitors and health checks, '
            'specialized for the Linux operating system.')),
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
            'linuxsystemcpumonitor = linuxutils.system.cpu:SystemCpuUsageMonitor',
            'linuxsystemmemorymonitor = linuxutils.system.mem:SystemMemoryUsageMonitor',
            'linuxsystemnetmonitor = linuxutils.system.net:SystemNetworkUsageMonitor',
            'linuxsystemfilesmonitor = linuxutils.system.files:SystemFileUsageMonitor',
            'linuxproccpumonitor = linuxutils.process.cpu:ProcCpuUsageMonitor',
            'linuxprocmemmonitor = linuxutils.process.mem:ProcMemoryUsageMonitor',
            'linuxprochealthcheck = linuxutils.process.pid:ProcMonitoringHealthCheck',
        ],
    },
)
