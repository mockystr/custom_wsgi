from time import sleep

from django.http import HttpResponse


def index(request):
    message = 'This is index.'
    if request.method == 'GET':
        data = request.META.get('QUERY_STRING')
        message += f' Data {data}'
    return HttpResponse(message, content_type='text/plain')


def sleep_index(request):
    ...
    sleep(500)
    return HttpResponse('This is sleep index', content_type='text/plain')
