import io
import socket
from typing import Dict, List

from django.http import HttpResponse

from custom_wsgi.utils.app_utils import (
    wsgi_config,
    server_config,
    application_from_path
)
from custom_wsgi.utils.logging import wsgi_logger


class Server:
    def __init__(self, application):
        self.logger = wsgi_logger

        self._wsgi_config = wsgi_config()
        self._server_config = server_config()

        self.application = application

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self._server_config.queue_size)

        self.headers = []

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

    def run(self):
        self.logger.info(f'RUNNING ON {self.host}:{self.port}')

        while True:
            conn, addr = self.socket.accept()
            self.handle_request(conn)

    def handle_request(self, conn):
        data = conn.recv(self._server_config.buffer_size).decode('utf-8')
        method, path, http_version = self._parse_request_info(data)
        environ = self._form_environment(data, method, path)
        result = self.application(environ, self.start_response)
        response = self._collect_response(result)

        conn.sendall(response.encode())
        conn.close()
        self.logger.info(f'{method} {self.headers[0]}')

    def _form_environment(self, data: str, method: str, path: str) -> Dict:
        return {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SERVER_NAME': self.host,
            'SERVER_PORT': str(self.port),

            'wsgi.input': io.StringIO(data),
            'wsgi.url_scheme': self.wsgi_config.url_scheme,
        }

    def start_response(self, status: str, response_headers: List[tuple]):
        self.headers = [status, response_headers]

    @staticmethod
    def _parse_request_info(request_data: str) -> List[str]:
        return request_data.splitlines()[0].rstrip('\r\n').split()

    def _collect_response(self, result: HttpResponse) -> str:
        status, headers = self.headers

        status_line = f'HTTP/1.1 {status}'
        headers = '\r\n'.join({'{0}: {1}'.format(*h) for h in headers})
        data_to_response = list(iter(result))[0].decode('utf-8')
        response = f'{status_line}\r\n{headers}\r\n\r\n{data_to_response}'
        return response


def make_server(app_path):
    application = application_from_path(app_path)
    return Server(application)
