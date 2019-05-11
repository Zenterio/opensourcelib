import logging
import os

from debpacker.common.preparedassets import PreparedWorkspace, prepare_output_dir
from debpacker.common.templatehandling import import_template_file
from debpacker.common.utils import create_deb_equivs_package
from debpacker.metapackage.configreader import PackageConfig
from debpacker.metapackage.utils import get_template_path
from debpacker.toolchain.toolchain import move

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

UBUNTU_14_CODENAME = 'trusty'
UBUNTU_16_CODENAME = 'xenial'
UBUNTU_18_CODENAME = 'bionic'
OUTPUT_BASE_DIR = 'dist'


class UnknownDistributionException(Exception):
    pass


def create_metapackage(output_dir, workspace, force, config: PackageConfig):
    with PreparedWorkspace(workspace, force) as (workspace, package_root):
        for distribution in _get_distribution_list(config.distributions):
            distribution_output_dir = _prepare_distribution_output_dirs(output_dir, distribution)
            template_path = _import_debian_template(package_root, config, distribution)
            deb_file = create_deb_equivs_package(template_path)
            move(deb_file, distribution_output_dir, override=force)


def _get_distribution_list(distributions):
    return distributions if distributions else [None]


def _prepare_distribution_output_dirs(output_dir, distribution):
    logger.debug('Preparing output dir for {dist}'.format(dist=distribution))
    if not distribution:
        path = os.path.join(output_dir, OUTPUT_BASE_DIR)

    elif UBUNTU_14_CODENAME == distribution:
        path = os.path.join(output_dir, OUTPUT_BASE_DIR, UBUNTU_14_CODENAME)

    elif UBUNTU_16_CODENAME == distribution:
        path = os.path.join(output_dir, OUTPUT_BASE_DIR, UBUNTU_16_CODENAME)

    elif UBUNTU_18_CODENAME == distribution:
        path = os.path.join(output_dir, OUTPUT_BASE_DIR, UBUNTU_18_CODENAME)

    else:
        raise UnknownDistributionException(
            'Did not recognize the distributions: {dist}'.format(dist=distribution))

    prepare_output_dir(path)
    return path


def _import_debian_template(package_root, config: PackageConfig, distribution):
    version = config.version if not distribution else config.version + '+' + distribution
    template_kwargs = {
        'PACKAGE_NAME': config.name,
        'VERSION': version,
        'SHORT_DESCRIPTION': config.short_description,
        'LONG_DESCRIPTION': _get_long_description_format(config.long_description),
        'ARCHITECTURE': config.architecture,
        'DEPENDENCIES': ', '.join(config.dependencies),
    }
    return import_template_file(
        get_template_path('debian_template.equivs'), package_root, **template_kwargs)


def _get_long_description_format(description: str) -> str:
    return description.replace('\n', '\n ')
