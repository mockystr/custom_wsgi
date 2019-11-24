from time import sleep

from django.http import HttpResponse


def index(request):
    ...
    return HttpResponse('This is index', content_type='text/plain')


def sleep_index(request):
    ...
    sleep(500)
    return HttpResponse('This is index', content_type='text/plain')
