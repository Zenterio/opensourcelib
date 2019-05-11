import os

from setuptools import find_packages, setup

setup(
    name='k2-infra',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Addons for testing inftrastructure.',
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'docker-pycreds<1.0,>=0',
        'docker<4.0,>=3',
        'testinfra<2.0,>=1',
    ],
    entry_points={
        'k2.addons': [
            'hostshellexec = hostshellexec.hostshellexec:HostShellExec',
            'infra = infra.infra:InfraExtension',
            'docker = virt.docker:DockerExtension',
            'dockeraddsutscans = virt.docker:DockerAddSutCansExtension',
            'dockerclean = virt.docker_clean:CleanDocker',
        ],
    },
)
