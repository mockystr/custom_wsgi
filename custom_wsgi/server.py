import io
import socket
import sys

from typing import Dict, List
from multiprocessing.pool import ThreadPool
from threading import current_thread

from django.http import HttpResponse

from custom_wsgi.utils.app_utils import (
    wsgi_config,
    server_config,
    application_from_path
)
from custom_wsgi.utils.logging import wsgi_logger


class Response:
    def __init__(self):
        self.logger = wsgi_logger
        self._headers = []

    @property
    def headers(self):
        return self._headers

    def _collect_response(self, result: HttpResponse) -> str:
        status, headers = self._headers

        status_line = f'HTTP/1.1 {status}'
        headers = '\r\n'.join({'{0}: {1}'.format(*h) for h in headers})
        data_to_response = list(iter(result))[0].decode('utf-8')
        response = f'{status_line}\r\n{headers}\r\n\r\n{data_to_response}'
        return response

    def start_response(self, status: str, response_headers: List[tuple]):
        self._headers = [status, response_headers]

    def get_response_text(self, result_data):
        return self._collect_response(result_data).encode()


class Server:
    def __init__(self, application):
        self.logger = wsgi_logger

        self._wsgi_config = wsgi_config()
        self._server_config = server_config()

        self.application = application

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self._server_config.queue_size)

        self.pool = ThreadPool(processes=self.wsgi_config.threads)

    @property
    def server_config(self):
        return self._server_config

    @property
    def wsgi_config(self):
        return self._wsgi_config

    @property
    def host(self):
        return self._server_config.host

    @property
    def port(self):
        return self._server_config.port

    def execute(self):
        self._run_forever()

    def _run_forever(self):
        self.logger.info(f'RUNNING {self.host}:{self.port}')

        while True:
            try:
                conn, addr = self.socket.accept()
                response = Response()
                self.pool.apply_async(self.handle_request, (conn, response))
            except KeyboardInterrupt:
                self.pool.close()
                self.pool.join()
                self.pool.terminate()
                self.socket.close()

    def handle_request(self, conn, response):
        data = conn.recv(self._server_config.buffer_size).decode('utf-8')
        method, path, http_version = self._parse_request_info(data)
        environ = self._form_environment(data, method, path)

        result = self.application(environ, response.start_response)
        conn.sendall(response.get_response_text(result))
        conn.close()

        tid = current_thread().ident
        self.logger.info(f'{method} {response.headers[0]} {tid}')

    def _form_environment(self, data: str, method: str, path: str) -> Dict:
        split_path = path.split('?')
        path_info = split_path[0]
        query_sting = ''
        if len(split_path) >= 2:
            query_sting = '?'.join(split_path[1:])

        return {
            'REQUEST_METHOD': method,
            'PATH_INFO': path_info,
            'QUERY_STRING': query_sting,
            'SERVER_NAME': self.host,
            'SERVER_PORT': str(self.port),

            'wsgi.input': io.StringIO(data),
            'wsgi.errors': sys.stderr,

            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': self.wsgi_config.url_scheme,
        }

    @staticmethod
    def _parse_request_info(request_data: str) -> List[str]:
        return request_data.splitlines()[0].rstrip('\r\n').split()


def make_server(app_path):
    application = application_from_path(app_path)
    return Server(application)
