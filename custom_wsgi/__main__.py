import argparse

from custom_wsgi.server import make_server

parser = argparse.ArgumentParser(description='WSGI server')
parser.add_argument(
    nargs=1,
    type=str,
    dest='app_path'
)
args = parser.parse_args()

make_server(args.app_path[0]).execute()
