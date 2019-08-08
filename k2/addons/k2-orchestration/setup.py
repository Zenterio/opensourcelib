import os

from setuptools import find_packages, setup

setup(
    name='k2-orchestration',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Interact with orchestration tools',
    long_description=(
        'Interact with orchestation, provisioning and configuration management tools.'),
    maintainer='engineering-services',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[],
    entry_points={
        'k2.addons': [
            'ansiblemanager = orchestration.ansible.manager:AnsibleManager',
            'ansibleaddsutcans = orchestration.ansible.manager:AnsibleAddSutCansExtension',
            'ansiblesuts = orchestration.ansible.manager:AnsibleSuts',
            'ansibleinitializesuts = orchestration.ansible.initialize:InitializeAnsibleSuts',
            'ansiblesutsconfig = orchestration.ansible.manager:AnsibleSutsConfig',
            'ansibledocker = orchestration.ansible.backends.docker:DockerAnsibleExtension',
        ],
    },
)
