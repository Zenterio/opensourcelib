import filecmp
import os
import stat

import requests
from requests import ConnectionError
from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_no_arguments(zk2):
    """
    Check the server behaviour when not serving any files.

    It should give an empty response for paths that it is not setup to serve.
    """
    process = zk2(
        ['httpfileserver'], '--log-info k2.extension.httpfileserver '
        'httpfileserver', wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        r = requests.get('http://localhost:{port}/test_content'.format(port=port))
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    assert not r.content


@requires(zk2='Zk2')
def test_serve_data(zk2):
    """Test that server can serve data."""
    data = 'Hello world!'
    path = '/test_content'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-serve-data '{path}:{data}'".format(path=path, data=data),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    assert r.content == data.encode('utf-8')


@requires(zk2='Zk2')
def test_serve_data_with_modified_status_code(zk2):
    """Test that server can serve data with modified response code."""
    data = 'Hello world!'
    path = '/test_content'
    code = 404
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-serve-data '{path}:{data}:{code}'".format(
            path=path, data=data, code=code),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == 404, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=404)
    assert r.content == data.encode('utf-8')


@requires(zk2='Zk2')
def test_serve_data_after_redirect(zk2):
    """Test that server can serve data on redirected paths."""
    data = 'Hello world!'
    redirect_path = '/redirect_me'
    path = '/test_content'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-data '{path}:{data}' "
        "--httpfileserver-redirect '{redirect}:{path}'".format(
            path=path, data=data, redirect=redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=redirect_path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    assert r.history
    assert redirect_path in r.history[0].url
    assert r.content == data.encode('utf-8')


@requires(zk2='Zk2')
def test_serve_data_with_multiple_redirected_paths(zk2):
    """Test that server can serve data on multiple redirected paths."""
    data = 'Hello world!'
    path = '/test_content'
    first_redirect_path = '/redirect_me_first'
    second_redirect_path = '/redirect_me_also'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-data '{path}:{data}' "
        "--httpfileserver-redirect '{first}:{path}' "
        "--httpfileserver-redirect '{second}:{path}'".format(
            path=path, data=data, first=first_redirect_path, second=second_redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        r_first = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=first_redirect_path))
        r_second = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=second_redirect_path))
    finally:
        process.kill()
    assert r_first.status_code == r_second.status_code == 200
    assert r_first.history and r_second.history
    assert first_redirect_path in r_first.history[0].url
    assert second_redirect_path in r_second.history[0].url
    assert r_first.content == r_second.content == data.encode('utf-8')


@requires(zk2='Zk2')
def test_serve_data_with_queries(zk2):
    """Test that the server can serve data based on input queries."""
    data = 'Hello world!'
    path = '/test_content'
    query = 'FILENAME=test'
    extra_queries = 'CHECKSUM=1234567890ABCDEF'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-data '{path}:{data}:{query}'".format(
            path=path, data=data, query=query),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        r_no_query = requests.get('http://localhost:{port}{path}'.format(port=port, path=path))
        r_wrong_query = requests.get(
            'http://localhost:{port}{path}?{extra}'.format(
                port=port, path=path, extra=extra_queries))
        r_exact_query = requests.get(
            'http://localhost:{port}{path}?{query}'.format(port=port, path=path, query=query))
        r_extra_query = requests.get(
            'http://localhost:{port}{path}?{query}&{extra}'.format(
                port=port, path=path, query=query, extra=extra_queries))
    finally:
        process.kill()
    assert r_no_query.status_code == r_wrong_query.status_code == 200
    assert r_exact_query.status_code == r_extra_query.status_code == 200
    assert not r_no_query.content
    assert not r_wrong_query.content
    assert r_exact_query.content == r_extra_query.content == data.encode('utf-8')


@requires(zk2='Zk2')
def test_serve_different_data_based_on_queries(zk2):
    """Test that the server can serve different data based on input queries."""
    data_1 = 'Hello world!'
    data_2 = 'Goodbye world!'
    fallback_data = 'Hello afterlife!'
    path = '/test_content'
    query_1 = 'FILENAME=test'
    query_2 = 'FORCED=true'
    extra_queries = 'CHECKSUM=1234567890ABCDEF'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-data '{path}:{data_1}:{first_query_list}' "
        "--httpfileserver-serve-data '{path}:{data_2}:{second_query_list}' "
        "--httpfileserver-serve-data '{path}:{fallback}'".format(
            path=path,
            data_1=data_1,
            data_2=data_2,
            fallback=fallback_data,
            first_query_list=query_1,
            second_query_list=':'.join([query_1, query_2])),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        r_no_query = requests.get('http://localhost:{port}{path}'.format(port=port, path=path))
        r_unmatched_query = requests.get(
            'http://localhost:{port}{path}?{extra}'.format(
                port=port, path=path, extra=extra_queries))
        r_first_query = requests.get(
            'http://localhost:{port}{path}?{query_list}'.format(
                port=port, path=path, query_list=query_1))
        r_second_query = requests.get(
            'http://localhost:{port}{path}?{query_list}'.format(
                port=port, path=path, query_list='&'.join([query_1, query_2])))
    finally:
        process.kill()
    assert r_no_query.status_code == r_unmatched_query.status_code == 200
    assert r_first_query.status_code == r_second_query.status_code == 200
    assert r_no_query.content == r_unmatched_query.content == fallback_data.encode('utf-8')
    assert r_first_query.content == data_1.encode('utf-8')
    assert r_second_query.content == data_2.encode('utf-8')


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_serve_file(zk2, workspace):
    """Test that server can serve a file."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    path = '/test_content'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-serve-file '{path}:{file}'".format(
            path=path, file=file_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    with open(file_path, 'rb') as file:
        assert r.content == file.read()


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_serve_file_after_redirect(zk2, workspace):
    """Test that server can serve a file on redirected paths."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    redirect_path = '/redirect_me'
    path = '/test_content'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-file '{path}:{file}' "
        "--httpfileserver-redirect '{redirect}:{path}'".format(
            path=path, file=file_path, redirect=redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=redirect_path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    assert r.history
    assert redirect_path in r.history[0].url
    with open(file_path, 'rb') as file:
        assert r.content == file.read()


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_serve_file_with_multiple_redirected_paths(zk2, workspace):
    """Test that server can serve a file on multiple redirected paths."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    path = '/test_content'
    first_redirect_path = '/redirect_me_first'
    second_redirect_path = '/redirect_me_also'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-file '{path}:{file}' "
        "--httpfileserver-redirect '{first}:{path}' "
        "--httpfileserver-redirect '{second}:{path}'".format(
            path=path, file=file_path, first=first_redirect_path, second=second_redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        r_first = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=first_redirect_path))
        r_second = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=second_redirect_path))
    finally:
        process.kill()
    assert r_first.status_code == r_second.status_code == 200
    assert r_first.history and r_second.history
    assert first_redirect_path in r_first.history[0].url
    assert second_redirect_path in r_second.history[0].url
    with open(file_path, 'rb') as file:
        assert r_first.content == r_second.content == file.read()


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_serve_file_with_queries(zk2, workspace):
    """Test that the server can serve files based on input queries."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    path = '/test_content'
    query = 'FILENAME=test'
    extra_queries = 'CHECKSUM=1234567890ABCDEF'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-file '{path}:{file}:{query}'".format(
            path=path, file=file_path, query=query),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        r_no_query = requests.get('http://localhost:{port}{path}'.format(port=port, path=path))
        r_wrong_query = requests.get(
            'http://localhost:{port}{path}?{extra}'.format(
                port=port, path=path, extra=extra_queries))
        r_exact_query = requests.get(
            'http://localhost:{port}{path}?{query}'.format(port=port, path=path, query=query))
        r_extra_query = requests.get(
            'http://localhost:{port}{path}?{query}&{extra}'.format(
                port=port, path=path, query=query, extra=extra_queries))
    finally:
        process.kill()
    assert r_no_query.status_code == r_wrong_query.status_code == 200
    assert r_exact_query.status_code == r_extra_query.status_code == 200
    assert not r_no_query.content
    assert not r_wrong_query.content
    with open(file_path, 'rb') as file:
        assert r_exact_query.content == r_extra_query.content == file.read()


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_serve_data_or_file_based_on_query(zk2, workspace):
    """Test that the server can serve either data or file based on input queries."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    data = 'Goodbye world!'
    fallback_data = 'Hello afterlife!'
    path = '/test_content'
    query_1 = 'FILENAME=test'
    query_2 = 'FORCED=true'
    extra_queries = 'CHECKSUM=1234567890ABCDEF'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-serve-file '{path}:{file}:{first_query_list}' "
        "--httpfileserver-serve-data '{path}:{data}:{second_query_list}' "
        "--httpfileserver-serve-data '{path}:{fallback}'".format(
            path=path,
            data=data,
            file=file_path,
            fallback=fallback_data,
            first_query_list=query_1,
            second_query_list=':'.join([query_1, query_2])),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Servicing', timeout=3)
        r_no_query = requests.get('http://localhost:{port}{path}'.format(port=port, path=path))
        r_unmatched_query = requests.get(
            'http://localhost:{port}{path}?{extra}'.format(
                port=port, path=path, extra=extra_queries))
        r_file_query = requests.get(
            'http://localhost:{port}{path}?{query_list}'.format(
                port=port, path=path, query_list=query_1))
        r_data_query = requests.get(
            'http://localhost:{port}{path}?{query_list}'.format(
                port=port, path=path, query_list='&'.join([query_1, query_2])))
    finally:
        process.kill()
    assert r_no_query.status_code == r_unmatched_query.status_code == 200
    assert r_file_query.status_code == r_data_query.status_code == 200
    assert r_no_query.content == r_unmatched_query.content == fallback_data.encode('utf-8')
    assert r_data_query.content == data.encode('utf-8')
    with open(file_path, 'rb') as file:
        assert r_file_query.content == file.read()


@requires(zk2='Zk2')
def test_deny_path_with_default_status_code(zk2):
    """
    Test that the server can deny a path.

    The default return status code should be 404 Not Found for paths that we ask
    it to deny.
    """
    expected_status_code = 404
    path = '/not_found'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-deny '{path}'".format(path=path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Denying requests', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == expected_status_code, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=expected_status_code)
    assert not r.content


@requires(zk2='Zk2')
def test_deny_path_with_default_status_code_after_redirect(zk2):
    """
    Test that the server can deny a path, including redirected paths.

    The default return status code should be 404 Not Found for paths that we ask
    it to deny.
    """
    expected_status_code = 404
    redirect_path = '/redirect_me'
    path = '/not_found'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-deny '{path}' "
        "--httpfileserver-redirect '{redirect}:{path}'".format(path=path, redirect=redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Denying requests', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=redirect_path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == expected_status_code, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=expected_status_code)
    assert r.history
    assert redirect_path in r.history[0].url
    assert not r.content


@requires(zk2='Zk2')
def test_deny_path_with_default_status_code_and_multiple_redirected_paths(zk2):
    """
    Test that the server can deny a path, including multiple redirected paths.

    The default return status code should be 404 Not Found for paths that we ask
    it to deny.
    """
    expected_status_code = 404
    path = '/not_found'
    first_redirect_path = '/redirect_me_first'
    second_redirect_path = '/redirect_me_also'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-deny '{path}' "
        "--httpfileserver-redirect '{first}:{path}' "
        "--httpfileserver-redirect '{second}:{path}'".format(
            path=path, first=first_redirect_path, second=second_redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Denying requests', timeout=3)
        r_first = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=first_redirect_path))
        r_second = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=second_redirect_path))
    finally:
        process.kill()
    assert r_first.status_code == r_second.status_code == expected_status_code
    assert r_first.history and r_second.history
    assert first_redirect_path in r_first.history[0].url
    assert second_redirect_path in r_second.history[0].url
    assert not r_first.content and not r_second.content


@requires(zk2='Zk2')
def test_deny_path_with_custom_status_code(zk2):
    """
    Test that a custom return status code can be specified.

    Checks that the server replies with custom code 401 Unauthorized for paths
    that we ask it to deny.
    """
    expected_status_code = 401
    path = '/unauthorized'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-deny '{path}:{code}'".format(
            path=path, code=expected_status_code),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Denying requests', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == expected_status_code, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=expected_status_code)
    assert not r.content


@requires(zk2='Zk2')
def test_deny_path_with_custom_status_code_after_redirect(zk2):
    """
    Test that a custom return status code and a redirect path can be specified.

    Checks that the server replies with custom code 401 Unauthorized for paths
    that we ask it to deny, including redirected paths.
    """
    expected_status_code = 401
    redirect_path = '/redirect_me'
    path = '/unauthorized'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-deny '{path}:{code}' "
        "--httpfileserver-redirect '{redirect}:{path}' ".format(
            path=path, code=expected_status_code, redirect=redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Denying requests', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=redirect_path)
        r = requests.get(url)
    finally:
        process.kill()
    assert r.status_code == expected_status_code, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=expected_status_code)
    assert r.history
    assert redirect_path in r.history[0].url
    assert not r.content


@requires(zk2='Zk2')
def test_deny_path_with_custom_status_code_and_multiple_redirected_paths(zk2):
    """
    Test that a custom return status code and multiple redirected paths can be specified.

    Checks that the server replies with custom code 401 Unauthorized for paths
    that we ask it to deny, including redirected paths.
    """
    expected_status_code = 401
    path = '/not_found'
    first_redirect_path = '/redirect_me_first'
    second_redirect_path = '/redirect_me_also'
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        'httpfileserver '
        "--httpfileserver-deny '{path}:{code}' "
        "--httpfileserver-redirect '{first}:{path}' "
        "--httpfileserver-redirect '{second}:{path}'".format(
            path=path,
            code=expected_status_code,
            first=first_redirect_path,
            second=second_redirect_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Denying requests', timeout=3)
        r_first = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=first_redirect_path))
        r_second = requests.get(
            'http://localhost:{port}{path}'.format(port=port, path=second_redirect_path))
    finally:
        process.kill()
    assert r_first.status_code == r_second.status_code == expected_status_code
    assert r_first.history and r_second.history
    assert first_redirect_path in r_first.history[0].url
    assert second_redirect_path in r_second.history[0].url
    assert not r_first.content and not r_second.content


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_upload_text_file(zk2, workspace):
    """Test that server can accept uploading a text file."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    path = '/test_upload'
    local_path = os.path.join(workspace.create_dir('dst'), 'new_testfile.bin')
    os.system('rm -rf {local_path}'.format(local_path=local_path))
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-accept-upload '{path}:{file}'".format(
            path=path, file=local_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Uploading', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        files = {'file': (os.path.basename(file_path), open(file_path, 'r'), 'text/plain')}
        r = requests.post(url, files=files)
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    assert filecmp.cmp(file_path, local_path)


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_upload_text_file_to_folder(zk2, workspace):
    """Test that server can accept uploading a text file to a folder."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    file_name = os.path.basename(file_path)
    path = '/test_upload'
    local_dir = workspace.create_dir('dst')
    local_path = os.path.join(local_dir, file_name)
    os.system('rm -rf {local_path}'.format(local_path=local_path))
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-accept-upload '{path}:{dir}'".format(
            path=path, dir=local_dir),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Uploading', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        files = {'file': (file_name, open(file_path, 'r'), 'text/plain')}
        r = requests.post(url, files=files)
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    assert filecmp.cmp(file_path, local_path)


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_upload_file_without_write_permission_in_host_folder(zk2, workspace):
    """Test that server can not accept uploading a file without write permission in server host folder."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    path = '/test_upload'
    local_dir = workspace.create_dir('dst_read_only')
    os.chmod(local_dir, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    local_path = os.path.join(local_dir, 'HelloWorld.txt')
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-accept-upload '{path}:{dir}'".format(
            path=path, dir=local_dir),
        wait=False)

    expected_exception_occurred = False
    try:
        url = 'http://localhost:{port}{path}'.format(port=1234, path=path)
        files = {'file': (file_path, open(file_path, 'r'), 'text/plain')}
        requests.post(url, files=files)
    except ConnectionError:
        expected_exception_occurred = True
    finally:
        process.wait()

    assert expected_exception_occurred, 'Expected a ConnectionError but it did not occur'
    assert not os.path.exists(local_path)


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_upload_file_and_existing_file_without_write_permission(zk2, workspace):
    """Test that server can not accept uploading a existing file without write permission."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    file_name = os.path.basename(file_path)
    path = '/test_upload'
    local_dir = 'dst'
    workspace.create_dir(local_dir)
    local_path = workspace.create_file(os.path.join(local_dir, file_name), 'dummy text')
    os.chmod(local_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-accept-upload '{path}:{dir}'".format(
            path=path, dir=local_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Uploading', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        files = {'file': (file_name, open(file_path, 'r'), 'text/plain')}
        r = requests.post(url, files=files)
    finally:
        process.kill()
    assert r.status_code == 500, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=500)
    assert not filecmp.cmp(file_path, local_path)


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_upload_binary_file(zk2, workspace):
    """Test that server can accept uploading a binary file."""
    file_path = os.path.join(workspace.create_dir('src'), 'random.bin')
    with open(file_path, 'wb') as fout:
        fout.write(os.urandom(1024))
    path = '/test_upload'
    local_path = os.path.join(workspace.create_dir('dst'), 'new_upload.bin')
    os.system('rm -rf {local_path}'.format(local_path=local_path))
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-accept-upload '{path}:{file}'".format(
            path=path, file=local_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Uploading', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        files = {
            'file': (os.path.basename(file_path), open(file_path, 'rb'), 'multipart/form-data')
        }
        r = requests.post(url, files=files)
    finally:
        process.kill()
    assert r.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r.status_code, expected=200)
    assert filecmp.cmp(file_path, local_path)


@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_upload_text_file_to_folder_and_deny_another_path(zk2, workspace):
    """Test that server can accept uploading a text file to a folder and deny another upload path."""
    file_path = workspace.create_file('src/HelloWorld.txt', 'Hello World!')
    file_name = os.path.basename(file_path)
    path = '/test_upload'
    local_dir = workspace.create_dir('dst')
    local_path = os.path.join(local_dir, file_name)
    deny_path = '/test_upload/denyfile'
    os.system('rm -rf {local_path}'.format(local_path=local_path))
    process = zk2(
        ['httpfileserver'],
        '--log-info k2.extension.httpfileserver '
        "httpfileserver --httpfileserver-accept-upload '{path}:{dir}' "
        "--httpfileserver-deny '{deny}'".format(path=path, dir=local_dir, deny=deny_path),
        wait=False)

    try:
        prefix = r'HttpFileServer Thread: Started HTTP server on port (\d+)'
        line = process.wait_for_match_in_stderr(prefix, timeout=8).group(1)
        port = int(line)
        process.wait_for_match_in_stderr('HttpFileServer: Uploading', timeout=3)
        url = 'http://localhost:{port}{path}'.format(port=port, path=path)
        files = {'file': (file_name, open(file_path, 'r'), 'text/plain')}
        r_ok = requests.post(url, files=files)
        url = 'http://localhost:{port}{path}'.format(port=port, path=deny_path)
        r_deny = requests.post(url, files=files)
    finally:
        process.kill()
    assert r_ok.status_code == 200, 'Status code was {actual}, expected {expected}'.format(
        actual=r_ok.status_code, expected=200)
    assert filecmp.cmp(file_path, local_path)
    assert r_deny.status_code == 404, 'Status code was {actual}, expected {expected}'.format(
        actual=r_deny.status_code, expected=404)
