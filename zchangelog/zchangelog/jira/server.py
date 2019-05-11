import getpass

from jira import JIRA, JIRAError
from requests.exceptions import ConnectionError


def connect_to_jira(user, password, server):
    """
    Connect to specified jira server. Prompts for password if not given.

    :param user: The jira user
    :param password: The password for the jira user
    :param server: The jira server
    :return: A Jira connection instance
    """
    options = {'server': server, 'verify': _get_cert()}
    if not password:
        jira_password = getpass.getpass()
    else:
        jira_password = password
    try:
        jira = JIRA(options, basic_auth=(user, jira_password))
    except (JIRAError, ConnectionError) as e:
        print('Connecting to jira failed, message: {text}'.format(text=e))
        exit(1)
    return jira


def _get_cert():
    return '/usr/local/share/ca-certificates/Zenterio_AD_Root_CA.crt'
