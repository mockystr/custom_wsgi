from django.urls import path

from django_app.core.views import *

app_name = 'core'

urlpatterns = [
    path('index', index),
    path('sleep_index', sleep_index),
]
