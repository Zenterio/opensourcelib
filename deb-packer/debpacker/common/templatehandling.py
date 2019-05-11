import logging
import os
from enum import Enum, unique
from string import Template

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@unique
class ConflictStrategy(Enum):
    fail = 1
    skip = 2
    replace_files = 3


def import_template_dir(
        template_dir,
        dst_dir,
        output_dir=None,
        conflict_strategy: ConflictStrategy = ConflictStrategy.replace_files,
        **kwargs):
    logger.debug('Importing template from {path}'.format(path=template_dir))
    output_dir = os.path.join(dst_dir, output_dir if output_dir else os.path.basename(template_dir))
    _prepare_output_dir(output_dir, conflict_strategy)
    for file in os.listdir(template_dir):
        path = os.path.join(template_dir, file)
        if os.path.isfile(path):
            import_template_file(path, output_dir, conflict_strategy=conflict_strategy, **kwargs)
    return output_dir


def _prepare_output_dir(output_dir, conflict_strategy):
    if os.path.isdir(output_dir) and conflict_strategy == ConflictStrategy.fail:
        raise FileExistsError(output_dir)

    os.makedirs(output_dir, exist_ok=True)


def import_template_file(
        template_path,
        output_dir,
        conflict_strategy: ConflictStrategy = ConflictStrategy.replace_files,
        **kwargs):
    with open(template_path, 'r') as template_file:
        template = Template(template_file.read())
        out_path = os.path.join(output_dir, os.path.basename(template_path))
        if _skip_importing_to(out_path, conflict_strategy):
            logger.warning('Skip to import {path} since it already exists'.format(path=out_path))
        else:
            with open(out_path, 'w') as out_file:
                logger.debug('Filling in template for {path}'.format(path=template_path))
                out_file.write(template.substitute(kwargs))
        return out_path


def _skip_importing_to(path: str, conflict_strategy: ConflictStrategy):
    if not os.path.isfile(path):
        return False

    if conflict_strategy == ConflictStrategy.skip:
        return True

    elif conflict_strategy == ConflictStrategy.replace_files:
        logger.debug('Removing existing template file: {path}'.format(path=path))
        os.remove(path)

    else:
        raise FileExistsError(path)

    return False
