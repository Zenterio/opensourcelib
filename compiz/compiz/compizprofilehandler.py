import configparser
import os

COMPIZ_PROFILE = '.zcompiz_profile'


def get_root_and_db(target):
    target = os.path.abspath(target)
    if not os.path.isdir(target):
        target = os.path.split(target)[0]
    profile_path = _find_profile(target)
    if profile_path == '' or profile_path == '/':
        raise ProfileNotFoundError()
    db_path = _get_db_path_from_profile_file(profile_path)
    return profile_path, db_path


def _find_profile(path):
    while path != '' and path != '/' and COMPIZ_PROFILE not in os.listdir(path):
        path = os.path.split(path)[0]
    return path


def _get_db_path_from_profile_file(path):
    parser = configparser.ConfigParser()
    parser.read(path + '/' + COMPIZ_PROFILE)
    try:
        return path + '/' + parser['db']['path']
    except KeyError as e:
        raise InvalidProfileFormatError('Key {e} not found in file "{file}"'.format(e=e, file=path))


class ProfileNotFoundError(Exception):
    pass


class InvalidProfileFormatError(Exception):
    pass
