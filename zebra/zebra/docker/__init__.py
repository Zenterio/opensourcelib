from zaf.config.options import ConfigOptionId
from zaf.config.types import Choice, Flag

from zebra.docker import docker

IMAGE_OPTION = ConfigOptionId(
    'image',
    'The name of the image to use.',
    option_type=Choice(sorted(docker.IMAGES.keys())),
    default=list(docker.IMAGES.keys())[0],
    short_name='i',
)
IMAGE_OVERRIDE_OPTION = ConfigOptionId(
    'image.override',
    'Override the image option to allow the loading of any image in the repository.',
)
TAG_OPTION = ConfigOptionId(
    'tag',
    'The tag of the image to use.',
    default='latest',
    short_name='t',
)
REGISTRY_OPTION = ConfigOptionId(
    'registry',
    'The registry to fetch the image from.',
    default='docker.zenterio.lan',
    short_name='r',
)
USE_REGISTRY_OPTION = ConfigOptionId(
    'use.registry',
    'Specify if registry should be used when determining URL to pull from.',
    default=True,
    option_type=Flag(),
)
REGISTRY_CACHE_OPTION = ConfigOptionId(
    'registry.cache',
    'The registry cache to use when fetching images.',
)
PULL_OPTION = ConfigOptionId(
    'pull',
    'Specify if the docker image should be pulled before running command.',
    option_type=Flag(),
    default=True,
)
HOSTNAME_OPTION = ConfigOptionId(
    'hostname',
    'Set the host name to use in the container. This is normally not needed.',
)
ENV_VARIABLES_OPTION = ConfigOptionId(
    'env.variable',
    'Forward an environment variable into the container, can be provided multiple times.',
    multiple=True,
    short_name='e',
)
MOUNTS_OPTION = ConfigOptionId(
    'mount',
    'Forward additional mount configurations to the container, can be provided multiple times. '
    'This follows the format of the Docker --mount option, for more information see '
    'https://docs.docker.com/storage/volumes.',
    multiple=True,
)
ROOT_OPTION = ConfigOptionId(
    'root',
    'Run as root inside container. '
    'DANGER! This will normally give the container root access to the host computer.',
    option_type=Flag(),
    default=False,
)
ROOT_DIR_OPTION = ConfigOptionId(
    'root.dir',
    'The root directory to mount in to the --container-root-dir directory. '
    'If not specified the root will be determined by first looking for a project root '
    'and using the parent directory of the project root '
    'and if that is not found then the parent directory of the current working directory is used.',
    short_name='d')
CONTAINER_ROOT_DIR_OPTION = ConfigOptionId(
    'container.root.dir',
    'The root directory inside the container.',
    default='/zebra/workspace',
)
PROJECT_DIR_OPTION = ConfigOptionId(
    'project.dir',
    'Override the project directory determination algorithm. '
    'For more information about directory structure see user guide.',
)
PROJECT_DIR_NAME_OPTION = ConfigOptionId(
    'project.dir.name',
    'Override the project directory name inside the container. '
    'For more information about directory structure see user guide.',
)
NETWORK_OPTION = ConfigOptionId(
    'network',
    'The docker network to use. '
    "By default 'host', 'bridge' and 'none' are available but this can also be used "
    'to select a manually created network.',
    default='host',
)
