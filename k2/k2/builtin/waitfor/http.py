import logging
import re

import requests
from zaf.component.decorator import component
from zaf.extensions.extension import get_logger_name

from .common import wait_for

logger = logging.getLogger(get_logger_name('k2', 'waitfor', 'http'))
logger.addHandler(logging.NullHandler())


@component()
class WaitForHttp:

    def wait_for_match_in_response(
            self, url, regex, timeout=60, poll_interval=1.0, **request_kwargs):
        """
        Wait for a match in the the GET content for the URL and return Match object.

        :param url: The url to get the content for
        :param regex: The regex pattern to use
        :param timeout: the timeout in seconds
        :param poll_interval: the interval in seconds to use when polling the file
        :param request_kwargs: Extra kwargs for the requests.get call
        :return: Match object
        :raises: TimeoutError if match is not found before timeout
        """
        compiled_regex = re.compile(regex)

        def check_response():
            try:
                r = requests.get(url, **request_kwargs)
                if r.ok:
                    return compiled_regex.search(r.text)
                else:
                    return False
            except Exception:
                logger.debug(
                    'Error occurred when requesting url {url}'.format(url=url), exc_info=True)
                return False

        return wait_for(check_response, timeout=timeout, poll_interval=poll_interval)

    def wait_for_status_code(
            self, url, status_code, timeout=60, poll_interval=1.0, **request_kwargs):
        """
        Wait for a status code for the HTTP GET request and return the response object.

        :param url: The url to get the content for
        :param status_code: Expected status code
        :param timeout: the timeout in seconds
        :param poll_interval: the interval in seconds to use when polling the file
        :param request_kwargs: Extra kwargs for the requests.get call
        :return: Response object
        :raises: TimeoutError if match is not found before timeout
        """

        def check_response():
            try:
                r = requests.get(url, **request_kwargs)
                if r.status_code == status_code:
                    return (True, r)
                else:
                    logger.debug(
                        'None-matching status code (expected={e}, actual={a}) when requesting url {url}'.
                        format(e=status_code, a=r.status_code, url=url),
                        exc_info=True)
                    return False
            except Exception:
                logger.debug(
                    'Error occurred when requesting url {url}'.format(url=url), exc_info=True)
                return False

        return wait_for(check_response, timeout=timeout, poll_interval=poll_interval)[1]

    def wait_for_ok(self, url, timeout=60, poll_interval=1.0, **request_kwargs):
        """
        Wait for a status code for the HTTP GET request to be OK and return the response object.

        :param url: The url to get the content for
        :param timeout: the timeout in seconds
        :param poll_interval: the interval in seconds to use when polling the file
        :param request_kwargs: Extra kwargs for the requests.get call
        :return: Response object
        :raises: TimeoutError if match is not found before timeout
        """

        def check_response():
            try:
                r = requests.get(url, **request_kwargs)
                if r.ok:
                    return r
                else:
                    return False
            except Exception:
                logger.debug(
                    'Error occurred when requesting url {url}'.format(url=url), exc_info=True)
                return False

        return wait_for(check_response, timeout=timeout, poll_interval=poll_interval)
