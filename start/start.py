import sys
from secrets import token_urlsafe
from django.http import HttpResponse
from django.urls import path
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from decouple import config, Csv

secret_key = token_urlsafe(64)

settings.configure(
	DEBUG=config('DEBUG', default=False, cast=bool),
	SECRET_KEY=config('SECRET_KEY', default=secret_key),
	ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv()),
	ROOT_URLCONF=__name__,
	MIDDLEWARE=[
		'django.middleware.common.CommonMiddleware',
		'django.middleware.csrf.CsrfViewMiddleware',
		'django.middleware.clickjacking.XFrameOptionsMiddleware',
	],
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': ('db.sqlite3'),
		}
	}
)

def index(request):
	return HttpResponse("Hello, this is a warm up project!")

urlpatterns = [
	path('', index, name='index')
]

application = get_wsgi_application()

if __name__ == "__main__":
	from django.core.management import execute_from_command_line
	execute_from_command_line(sys.argv)