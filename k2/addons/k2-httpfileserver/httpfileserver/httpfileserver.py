r"""
Simple HTTP server for serving file requests.

The server will listen for GET requests and answer with file content
(Content-type: application/octet-stream). Content can be provided in memory or
through file I/O. Different content is provided based on path and queries in the
request URL.
It is also possible to setup redirects (302) and to respond with a status code
(default is 404 Not found).

The following examples show how to use the ``zk2 httpfileserver`` command.

Example to serve "Hello world!" on http://localhost:8888/hi::

    zk2 httpfileserver --httpfileserver-port 8888 --httpfileserver-serve-data '/hi:Hello world!'

Example to serve:
    - "Hello world!" on http://localhost:8888/hi
    - "Goodbye world!" on http://localhost:8888/bye
    - "Hello afterlife!" on http://localhost:8888/bye?DEATH=true

.. code-block:: python

    zk2 httpfileserver --httpfileserver-port 8888 \
                       --httpfileserver-serve-data '/hi:Hello world!' \
                       --httpfileserver-serve-data '/bye:Goodbye world!' \
                       --httpfileserver-serve-data '/bye:Hello afterlife!:DEATH=true'

Serve requests can also specify the status code, default is 200::

    zk2 httpfileserver --httpfileserver-port 8888 \
                       --httpfileserver-serve-data '/hi:Hello world!:201' \
                       --httpfileserver-serve-data '/bye:Goodbye world!:202' \
                       --httpfileserver-serve-data '/bye:Hello afterlife!:203:DEATH=true'

Deny requests on http://localhost:8888/not_found::

    zk2 httpfileserver --httpfileserver-port 8888 --httpfileserver-deny '/not_found'

Deny requests on http://localhost:8888/unauthorized with status code 401::

    zk2 httpfileserver --httpfileserver-port 8888 --httpfileserver-deny '/unauthorized:401'


More complicated example to:
    - Serve data on http://localhost:8888/secret,
    - deny requests on http://localhost:8888/secret?PASSWORD=qwerty123 (or any url
      that has PASSWORD=qwerty123 as part of their queries)

.. code-block:: python

    zk2 httpfileserver --httpfileserver-port 8888 \
                       --httpfileserver-serve-data '/secret:You must provide password' \
                       --httpfileserver-deny '/secret:401:PASSWORD=qwerty123'

It is also possible to filter on multiple queries::

    zk2 httpfileserver --httpfileserver-port 8888 --httpfileserver-serve-data '/secret:42:LOGIN=user:PASSWORD=password'

The content will be available on http://localhost:8888/secret?PASSWORD=password&LOGIN=user
"""

import logging
import os
import threading
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, urlparse

from zaf.commands.command import CommandId
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'httpfileserver'))
logger.addHandler(logging.NullHandler())

HTTP_CODE_200 = 200  # OK
HTTP_CODE_302 = 302  # Redirection
HTTP_CODE_404 = 404  # Not found error
HTTP_CODE_500 = 500  # Server error


class ServerContent(object):
    """
    POD class for keeping track of served content.

    Only path and queries are used for equality and hash.
    """

    def __init__(self, path, queries, status_code):
        self.path = path
        self.queries = queries
        self.status_code = status_code

    def __eq__(self, other):
        return self.path == other.path and self.queries == other.queries and self.status_code == other.status_code

    def __hash__(self):
        return hash((self.path, self.queries, self.status_code))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.__dict__)


class ServerDenial(ServerContent):
    """Contains status code for denied paths."""

    def __init__(self, path, queries, status_code=HTTP_CODE_404):
        super().__init__(path, queries, status_code)


class ServerData(ServerContent):
    """Contains data for serviced paths."""

    def __init__(self, path, queries, data, status_code=HTTP_CODE_200):
        super().__init__(path, queries, status_code)
        self.data = data


class ServerFile(ServerContent):
    """Contains local file path for serviced paths."""

    def __init__(self, path, queries, local_path, status_code=HTTP_CODE_200):
        super().__init__(path, queries, status_code)
        self.local_path = local_path


class RequestHandler(BaseHTTPRequestHandler):

    def _find_best_match(self, content_list, path, queries):
        matching_content = [c for c in content_list if c.path == path]
        if len(matching_content) == 1:
            if matching_content[0].queries <= queries:
                return matching_content[0]
        elif len(matching_content) > 1:
            # multiple hits, check queries
            matching_content = [c for c in matching_content if c.queries <= queries]
            if len(matching_content) == 1:
                return matching_content[0]
            else:
                # sort based on number of common queries, highest first
                matching_content = sorted(
                    matching_content, key=lambda c: len(queries & c.queries), reverse=True)
                return matching_content[0]
        raise KeyError

    def do_GET(self):
        logger.debug('Server Thread: Got GET request for {path}'.format(path=self.path))
        url = urlparse(self.path)
        # hacky workaround for TDG mock
        path = url.path.split('&')[0]
        # extract queries and convert to set of tuples
        queries = {(key, value[0]) for key, value in parse_qs(url.query).items()}

        try:
            content = self._find_best_match(self.server.denied_paths, path, queries)
            logger.info('denying request to {path}'.format(path=path))
            self.send_response(content.status_code)
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            return
        except KeyError:
            pass

        try:
            new_path = self.server.redirected_paths[path]
            logger.info('redirecting to {path}'.format(path=new_path))
            self.send_response(HTTP_CODE_302)
            self.send_header('Location', new_path)
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            return

        except KeyError:
            pass

        try:
            content = self._find_best_match(self.server.serviced_paths, path, queries)
            self.send_response(content.status_code)
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Content-type', 'application/octet-stream')

            if type(content) is ServerFile:
                file_path = content.local_path
                if not os.path.isfile(file_path):
                    raise Exception('local file no longer exist')
                stat_info = os.stat(file_path)
                logger.info(
                    'serving local file "{file}" ({bytes} bytes) on {path}'.format(
                        file=file_path, bytes=stat_info.st_size, path=path))
                self.send_header('Content-Length', stat_info.st_size)
                self.end_headers()
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            elif type(content) is ServerData:
                length = len(content.data)
                logger.info(
                    'serving content ({bytes} bytes) on {path}'.format(bytes=length, path=path))
                self.send_header('Content-Length', length)
                self.end_headers()
                self.wfile.write(content.data)
            else:
                raise ValueError('unhandled server content, please contact ES')

        except KeyError:
            # path not served
            self.send_response(HTTP_CODE_200)
            self.send_header('Cache-Control', 'no-cache')
            logger.debug(
                'path not serviced: {path}, queries={queries}'.format(path=path, queries=url.query))
            self.end_headers()
        except Exception as e:
            # other exception
            self.send_response(HTTP_CODE_500)
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            raise e

    def do_POST(self):
        logger.debug(
            'Server Thread: serve POST request\nPath: {path}\nHeaders:\n{header}\n\n'.format(
                path=self.path, header=self.headers))
        try:
            content = self._find_best_match(self.server.denied_paths, self.path, set())
            logger.info('denying request to {path}'.format(path=self.path))
            self.send_response(content.status_code)
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            return
        except KeyError:
            pass
        try:
            content = self._find_best_match(self.server.accepted_paths, self.path, set())
            if type(content) is ServerFile:
                self.process_upload_file(content.local_path)
                self.send_response(HTTP_CODE_200)
                self.end_headers()
            else:
                raise ValueError('unhandled server content, please contact ES')
        except KeyError:
            # path not accepted
            self.send_response(HTTP_CODE_200)
            logger.info(
                'path not accepted: {path}, queries={queries}'.format(
                    path=self.path, queries=set()))
            self.end_headers()
        except Exception as e:
            # other exception
            self.send_response(HTTP_CODE_500)
            self.end_headers()
            raise e

    def do_PUT(self):
        logger.debug('message Server Thread: Ignoring PUT request to ' + self.path)
        self.send_response(HTTP_CODE_200)
        self.end_headers()

    # silence it
    def log_message(self, format, *args):
        return

    def process_upload_file(self, local_path):
        r"""
        Process POST request for uploading a file.

        The request is sent by the client via
            curl -F 'file=@hello_world' <server_ip>[:port][path]
        The request header should have the format as below example,
        {
            Host: 127.0.0.1:8000
            User-Agent: curl/7.57.0
            Accept: */*
            Content-Length: 207
            Content-Type: multipart/form-data; boundary=------------------------ac1269968687ee38
        }

        The request data body should the format as below example,
        {
            b'--------------------------ac1269968687ee38\r\n
            Content-Disposition: form-data; name="file"; filename="hello_world"\r\n
            Content-Type: application/octet-stream\r\n\r\n
            Hello world!\r\n
            --------------------------ac1269968687ee38--\r\n'
        }

        """
        boundary = self.headers['Content-Type'].split('=')[1]
        remainbytes = int(self.headers['Content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if boundary not in line.decode('utf-8'):
            msg = 'HTTP POST request format error: illegal content without leading boundary'
            logger.error(msg)
            raise Exception(msg)
        line = self.rfile.readline()
        remainbytes -= len(line)
        if os.path.isdir(local_path):
            # Use client original file name
            fn = re.findall(
                r'Content-Disposition.*name=".*"; filename="(.*)"', line.decode('utf-8'))
            if not fn:
                msg = 'File name is undefined and HTTP POST request is without filename field'
                logger.error(msg)
                raise Exception(msg)
            fn = os.path.join(local_path, fn[0])
        else:
            # Use specified file name
            fn = local_path

        # Skip two lines for "Content-Type: *" + an empty line
        remainbytes -= len(self.rfile.readline()) + len(self.rfile.readline())
        try:
            out_file = open(fn, 'wb')
        except IOError:
            msg = 'Could not open file to write, do you have write permission on {path}?'.format(
                path=fn)
            logger.error(msg)
            raise Exception(msg)
        preline = self.rfile.readline()
        remainbytes -= len(preline)

        while remainbytes > 0:
            line = self.rfile.readline()
            # Find end boundary
            if boundary.encode('utf-8') in line:
                preline = preline[0:-1]
                if chr(preline[-1]) == '\r':
                    preline = preline[0:-1]
                out_file.write(preline)
                out_file.close()
                logger.debug('File "{file}" is uploaded successfully!'.format(file=fn))
                return
            else:
                out_file.write(preline)
                preline = line
        msg = 'HTTP POST request format error: unexpected end of data'
        logger.error(msg)
        raise Exception(msg)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


@requires(host_ip='SutFacingHostIpAddress')
@component(name='HttpFileServer', provided_by_extension='httpfileserver')
class HttpFileServer(object):
    """
    Simple HTTP server for serving file requests.

    The server will listen for GET requests and answer with file content
    (Content-type: application/octet-stream). Content can be provided in memory or
    through file I/O. Different content is provided based on path and queries in the
    request URL.

    It is also possible to setup redirects (302) and to respond with a status code
    (default is 404 Not found).

    Examples (from *test_httpupgradesearch.py*):

    .. code-block:: python

        @requires(server='HttpFileServer')
        @requires(swupgrade='SwUpgrade')
        def test_search_get_no_result_on_404_response(server, swupgrade):
            server.deny('/EDS/upgrade.ini')
            search_url = '{url}/EDS/upgrade.ini'.format(url=server.base_url)
            result = swupgrade.search(search_url)
            assert not result.upgrade_available

    .. code-block:: python

        @requires(server='HttpFileServer')
        @requires(swupgrade='SwUpgrade')
        def test_search_get_no_result_on_404_response_after_redirect(server, swupgrade):
            server.redirect(redirect_from='/EDS/upgrade.ini', to='/UPGRADE/upgrade.ini')
            server.deny('/UPGRADE/upgrade.ini')
            search_url = '{url}/EDS/upgrade.ini'.format(url=server.base_url)
            result = swupgrade.search(search_url)
            assert not result.upgrade_available

    Example with queries (from *httpupgradeservermock.py*, somewhat reduced):

    .. code-block:: python

        @requires(server='HttpFileServer')
        @requires(sys_info='SystemInfo')
        @component
        class HttpUpgradeServerMock(object):

            def __init__(self, server, sys_info):
                self.server = server
                self.sys_info = sys_info.get()
                self.search_url = ''
                assert self.sys_info

            def serve_new_version(self, forced=False, kfs=None):
                upgrade_file = get_upgrade_detection_file(
                    self.sys_info.SwVersion + 1, self.sys_info.ProductID, self.sys_info.OUI, forced)
                self.server.redirect(redirect_from='/EDS/upgrade.ini', to='/UPGRADE/upgrade.ini')
                self.server.serve_data('/UPGRADE/upgrade.ini', data=upgrade_file)
                self.server.serve_data('/UPGRADE/jsp/getBootPackage.jsp', data=generate_lead_file())
                if kfs:
                    self.server.serve_file('/UPGRADE/upgrade.ini', kfs, queries={('FILENAME', 'kfs.zmg')})
                else:
                    self.server.deny('/UPGRADE/upgrade.ini', queries={('FILENAME', 'kfs.zmg')})
                self.search_url = '{url}/EDS/upgrade.ini'.format(url=self.server.base_url)

    """

    def __init__(self, host_ip, port=0):
        # Port 0 means to select an arbitrary unused port
        self.server = ThreadedHTTPServer((host_ip, port), RequestHandler)
        self.server.denied_paths = []
        self.server.serviced_paths = []
        self.server.redirected_paths = {}
        self.server.accepted_paths = []
        self.host, self.port = self.server.server_address
        self.base_url = 'http://{host}:{port}'.format(host=self.host, port=self.port)

        def serve_fn():
            logger.info(
                'HttpFileServer Thread: Started HTTP server on port {port}'.format(port=self.port))
            self.server.serve_forever()
            logger.info(
                'HttpFileServer Thread: Stopped HTTP server on port {port}'.format(port=self.port))

        self.server_thread = threading.Thread(target=serve_fn)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.received = None

    def __enter__(self):
        # Start a thread with the server. That thread will then start one
        # more thread for each request
        self.server_thread.start()
        return self

    def __exit__(self, *exc_info):
        # Tell the serve_forever() loop to stop and wait until it does
        self.server.shutdown()
        # Clean up the server
        self.server.server_close()

    def deny(self, path, queries=set(), status_code=HTTP_CODE_404):
        """
        Deny the request to the url matching the path and query parameters.

        :param path: the path to deny
        :param status_code: the status code to use, default 404
        :param queries: the request query parameters to match on
        """
        logger.info(
            'HttpFileServer: Denying requests to {base_url}{path} ({status_code})'.format(
                base_url=self.base_url, path=path, status_code=status_code))
        if type(queries) is dict:
            queries = set(queries.items())
        self._add_content(
            self.server.denied_paths, ServerDenial(path, queries, status_code=status_code))
        return self

    def serve_data(self, path, data, queries=set(), status_code=HTTP_CODE_200):
        """
        Serve data for requests to the url matching the path and query parameters.

        :param path: the path to serve data
        :param data: the data to serve
        :param status_code: the status code to use, default 200
        :param queries: the request queries to match on
        """
        logger.info(
            'HttpFileServer: Servicing {base_url}{path}, queries={queries}'.format(
                base_url=self.base_url, path=path, queries=queries))
        if type(queries) is dict:
            queries = set(queries.items())
        self._add_content(
            self.server.serviced_paths, ServerData(path, queries, data, status_code=status_code))
        return self

    def serve_file(self, path, local_path, queries=set(), status_code=HTTP_CODE_200):
        """
        Serve file for requests to the url matching the path and query parameters.

        :param path: the path to serve file
        :param local_path: the local path of the file to serve
        :param status_code: the status code to use, default 200
        :param queries: the request queries to match on
        """
        if not os.path.isfile(local_path):
            raise Exception('local file "{file}" does not exist'.format(file=local_path))
        logger.info(
            'HttpFileServer: Servicing {base_url}{path}, queries={queries}'.format(
                base_url=self.base_url, path=path, queries=queries))
        if type(queries) is dict:
            queries = set(queries.items())
        self._add_content(
            self.server.serviced_paths,
            ServerFile(path, queries, local_path, status_code=status_code))
        return self

    def accept_upload(self, path, local_path, status_code=HTTP_CODE_200):
        """
        Accept uploading file for requests to the url matching the path.

        :param path: the path to accept uploading
        :param local_path: the host local file path where the uploaded file(s) are
                           saved. If local_path is a directory, uploaded files will
                           use the names found in POST header.
        :param status_code: the status code to use, default 200
        """
        host_dir = local_path
        if not os.path.isdir(local_path):
            host_dir = os.path.dirname(local_path)
            if not host_dir:
                # For current folder
                host_dir = '.'
                local_path = os.path.join('.', local_path)
                logger.debug(
                    'Server local path is under the current folder, add prefix "./", {local_path}"'.
                    format(local_path=local_path))
        # check folder write permission
        if not os.access(host_dir, os.W_OK):
            raise Exception(
                'Host local folder "{dir}" has no write permission'.format(dir=host_dir))

        logger.info(
            'HttpFileServer: Uploading {base_url}{path}'.format(base_url=self.base_url, path=path))
        self._add_content(
            self.server.accepted_paths, ServerFile(
                path, set(), local_path, status_code=status_code))
        return self

    def redirect(self, redirect_from, to):
        """
        Redirect requests to the url matching the path and query parameters.

        :param redirect_from: the path to redirect
        :param to: the path to redirect to
        """

        self.server.redirected_paths[redirect_from] = to

    def _add_content(self, content_list, content):
        if content in content_list:
            # update existing value in list. This works since ServerContent only
            # check equality for path and queries
            for k, v in enumerate(content_list):
                if v == content:
                    content_list[k] = content
        else:
            content_list.append(content)


def list_of_queries_to_set(queries):
    return {(k, v) for k, v in dict(q.split('=') for q in queries).items()}


def httpfileserver_command(core):
    """
    Spin up a HTTP file server.

    The file server will be running in the foreground and will by default not
    service any kind of data. Setup data to be served with the
    --httpfileserver-serve-data and --httpfileserver-serve-file commands. These
    commands also accept queries that need to be part of the url before serving
    the data.
    See the examples below.

    All data is served as "Content-type: application/octet-stream"

    If no port is specified, a random available port will be used.
    """
    port = core.config.get(FILE_SERVER_PORT)
    ip = core.config.get(FILE_SERVER_IP)

    with HttpFileServer(ip, port) as server:
        for opt in core.config.get(FILE_SERVER_SERVE_DATA):
            args = opt.split(':')
            path = args[0]
            data = args[1]
            status_code = None
            queries = set()
            try:
                status_code = int(args[2])
                queries = list_of_queries_to_set(args[3:])
            except IndexError:
                pass
            except ValueError:
                queries = list_of_queries_to_set(args[2:])

            if status_code is not None:
                server.serve_data(path, data.encode('utf-8'), queries, status_code=status_code)
            else:
                server.serve_data(path, data.encode('utf-8'), queries)

        for opt in core.config.get(FILE_SERVER_SERVE_FILE):
            args = opt.split(':')
            path = args[0]
            file = args[1]
            status_code = None
            queries = set()
            try:
                status_code = int(args[2])
                queries = list_of_queries_to_set(args[3:])
            except IndexError:
                pass
            except ValueError:
                queries = list_of_queries_to_set(args[2:])

            if status_code is not None:
                server.serve_file(path, file, queries, status_code=status_code)
            else:
                server.serve_file(path, file, queries)

        for opt in core.config.get(FILE_SERVER_DENY):
            args = opt.split(':')
            path = args[0]
            status_code = None
            queries = set()
            try:
                status_code = int(args[1])
                queries = list_of_queries_to_set(args[2:])
            except IndexError:
                pass
            except ValueError:
                queries = list_of_queries_to_set(args[1:])

            if status_code is not None:
                server.deny(path, queries=queries, status_code=status_code)
            else:
                server.deny(path, queries=queries)

        for opt in core.config.get(FILE_SERVER_REDIRECT):
            args = opt.split(':')
            redirect_from = args[0]
            redirect_to = args[1]
            server.redirect(redirect_from, redirect_to)

        for opt in core.config.get(FILE_SERVER_ACCEPT_UPLOAD):
            args = opt.split(':')
            path = args[0]
            file = args[1]
            status_code = None
            try:
                status_code = int(args[2])
            except Exception:
                pass

            if status_code is not None:
                server.accept_upload(path, file, status_code=status_code)
            else:
                server.accept_upload(path, file)

        server.server_thread.join()


FILE_SERVER_IP = ConfigOptionId(
    'ip', 'The ip to use for the file server', default='localhost', namespace='httpfileserver')

FILE_SERVER_PORT = ConfigOptionId(
    'port',
    'The port to use for the file server',
    option_type=int,
    default=0,
    namespace='httpfileserver')

FILE_SERVER_SERVE_DATA = ConfigOptionId(
    'serve.data',
    'Serve data on a specific path. path:string[:status code][:queries]',
    multiple=True,
    namespace='httpfileserver')

FILE_SERVER_SERVE_FILE = ConfigOptionId(
    'serve.file',
    'Serve a local file on a specific path. path:file[:status code][:queries]',
    multiple=True,
    namespace='httpfileserver')

FILE_SERVER_ACCEPT_UPLOAD = ConfigOptionId(
    'accept.upload',
    'Accept uploading file to a specific path. path:file[:status code]',
    multiple=True,
    namespace='httpfileserver')

FILE_SERVER_DENY = ConfigOptionId(
    'deny',
    'Deny access to server on a specific url. path[:status code][:queries]',
    multiple=True,
    namespace='httpfileserver')

FILE_SERVER_REDIRECT = ConfigOptionId(
    'redirect', 'Redirect path to another. from:to', multiple=True, namespace='httpfileserver')

FILE_SERVER = CommandId(
    'httpfileserver',
    httpfileserver_command.__doc__,
    httpfileserver_command,
    config_options=[
        ConfigOption(FILE_SERVER_IP, required=True),
        ConfigOption(FILE_SERVER_PORT, required=True),
        ConfigOption(FILE_SERVER_SERVE_DATA, required=False),
        ConfigOption(FILE_SERVER_SERVE_FILE, required=False),
        ConfigOption(FILE_SERVER_ACCEPT_UPLOAD, required=False),
        ConfigOption(FILE_SERVER_DENY, required=False),
        ConfigOption(FILE_SERVER_REDIRECT, required=False),
    ])


@FrameworkExtension(
    name='httpfileserver', config_options=[], commands=[FILE_SERVER], endpoints_and_messages={})
class HttpFileServerAddon(AbstractExtension):

    def __init__(self, config, instances):
        pass
