from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'custom runserver'

    def handle(self, *args, **options):
        from custom_wsgi.server import make_server

        make_server(args[0]).execute()

    def add_arguments(self, parser):
        parser.add_argument(
            nargs='+',
            type=str,
            dest='args'
        )
