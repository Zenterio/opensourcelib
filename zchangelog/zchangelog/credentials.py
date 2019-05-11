import base64
import functools
import json
import logging
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

_default_username_marker = 'default-username'


def read_default_username():
    """
    Read the credentials file and returns the default username.

    :return: the default username or None
    """
    return read_credentials(_default_username_marker)


def write_default_username(username):
    """
    Write a default username to the credentials file.

    :param username: new default username
    """
    write_credentials(_default_username_marker, username)


def read_credentials(username):
    """
    Read the credentials for the username.

    Returns None if there are no matching credentials.
    :param username: the user
    :return: the password for the user
    """
    credentials_path = _credentials_file_path()
    try:
        password = _read_credentials_file(credentials_path).get(username, None)
        if password is not None:
            password = base64.b64decode(password.encode('utf-8')).decode('utf-8')
        return password
    except Exception as e:
        logger.warning('Problem reading credentials file %s.', credentials_path)
        raise e


def write_credentials(username, password):
    """
    Write the credentials for the username in a file is the users home directory.

    :param username: the user
    :param password: the password
    """
    credentials_path = _credentials_file_path()
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

    existing_credentials = {}
    try:
        existing_credentials = _read_credentials_file(credentials_path)
    except Exception:
        logger.warning(
            'Problem reading credentials file %s. Overwriting with correct information.',
            credentials_path)

    # Stores the password base64 encoded to make it a little bit harder to get it.
    # The main security is that the file is only readable by the user (or root)
    existing_credentials[username] = base64.b64encode(password.encode('utf-8')).decode('utf-8')

    _write_credentials_file(credentials_path, existing_credentials)


def remove_credentials(username, all=False):
    """
    Remove the credentials for username.

    If all is True then all credentials are removed.
    :param username: the user to remove the credentials for
    :param all: if all credentials should be removed
    """
    credentials_path = _credentials_file_path()

    existing_credentials = {}
    if not all:
        try:
            existing_credentials = _read_credentials_file(credentials_path)
            try:
                del existing_credentials[username]
            except KeyError:
                logger.warning('No credentials to remove for user %s', username)
        except Exception:
            logger.warning(
                'Problem reading credentials file %s. Clearing file to mitigate future problems.',
                credentials_path)

    _write_credentials_file(credentials_path, existing_credentials)


@functools.lru_cache(maxsize=1)
def _read_credentials_file(credentials_path):
    if os.path.exists(credentials_path):
        with open(credentials_path, 'r') as f:
            return json.loads(f.read())
    else:
        return {}


def _write_credentials_file(credentials_path, credentials):
    try:
        if os.path.exists(credentials_path):
            os.chmod(credentials_path, 0o600)
        with open(credentials_path, 'w') as f:
            f.write(json.dumps(credentials))
    finally:
        _read_credentials_file.cache_clear()
        if os.path.exists(credentials_path):
            os.chmod(credentials_path, 0o400)


def _credentials_file_path():
    # Versioning the file to allow for future changes to the format and contents
    return os.path.expanduser(os.path.join('~', '.config', 'zchangelog', '.credentials-v1'))
