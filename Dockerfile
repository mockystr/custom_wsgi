FROM python:3.7

COPY requirements.txt /
RUN pip install -r /requirements.txt

WORKDIR /code
COPY . .

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["python", "manage.py", "custom_runserver", "django_app.application.wsgi:application"]
