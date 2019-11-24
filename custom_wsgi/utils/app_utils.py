import dataclasses
import yaml
from typing import Mapping


def application_from_path(application_path: str):
    module, application = application_path.split(':')
    _temp = __import__(module, globals(), locals(),
                       [application], 0)
    application = getattr(_temp, application)
    return application


@dataclasses.dataclass
class WSGIConfig:
    url_scheme: str
    threads: int

    @classmethod
    def from_dict(cls, d: Mapping) -> 'WSGIConfig':
        return cls(
            url_scheme=d.get('url_scheme'),
            threads=d.get('threads'),
        )


def wsgi_config():
    with open('config.yml', 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return WSGIConfig.from_dict(cfg.get('wsgi'))


@dataclasses.dataclass
class ServerConfig:
    host: str
    port: int
    queue_size: int
    buffer_size: str

    @classmethod
    def from_dict(cls, d: Mapping) -> 'ServerConfig':
        return cls(
            host=d.get('host'),
            port=d.get('port'),
            queue_size=d.get('queue_size'),
            buffer_size=d.get('buffer_size')
        )


def server_config():
    with open('config.yml', 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return ServerConfig.from_dict(cfg.get('server'))
