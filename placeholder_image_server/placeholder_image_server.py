import hashlib, os, sys
from secrets import token_urlsafe
from django.conf import settings
from django.core.cache import cache # for server-side caching
from django.urls import reverse
from django.core.wsgi import get_wsgi_application
from django import forms
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import path
# from django.views.decorators.http import etag # uncomment for client-side caching
from decouple import config, Csv
from io import BytesIO
from PIL import Image, ImageDraw


# Settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings.configure(
	DEBUG = config('DEBUG', default=False, cast=bool),
	SECRET_KEY = config('SECRET_KEY', default='o-juj2#oyhz^=2xp*s4^k-64%hk^t)ceyyo7_kkuvbvk1ldr10'),
	ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv()),
	ROOT_URLCONF = __name__,
	INSTALLED_APPS = [
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.staticfiles',
	],
	MIDDLEWARE = [
		'django.middleware.common.CommonMiddleware',
		'django.middleware.csrf.CsrfViewMiddleware',
		'django.middleware.clickjacking.XFrameOptionsMiddleware',
	],
	TEMPLATES = [
		{
			'BACKEND': 'django.template.backends.django.DjangoTemplates',
			'DIRS': [
				os.path.join(BASE_DIR, 'templates'),
			],
			'APP_DIRS': True,
			'OPTIONS': {
				'context_processors': [
					'django.template.context_processors.debug',
					'django.template.context_processors.request',
					'django.contrib.auth.context_processors.auth',
					'django.contrib.messages.context_processors.messages',
				],
			},
		},
	],
	STATIC_URL = '/static/',
	STATICFILES_DIRS = [
    	os.path.join(BASE_DIR, 'static'),
	],
)


# Form to validate requested placeholder
class ImageForm(forms.Form):
	width = forms.IntegerField(min_value=1, max_value=2000)
	height = forms.IntegerField(min_value=1, max_value=2000)

	def create(self, image_format='PNG'):
		# Make an image of the given type and return as raw bytes
		width = self.cleaned_data['width']
		height = self.cleaned_data['height']
		key = '{}.{}.{}'.format(width, height, image_format)
		content = cache.get(key)
		if content is None:
			image = Image.new('RGB', (width, height))
			draw = ImageDraw.Draw(image)
			text = '{} * {}'.format(width, height)
			text_width, text_height = draw.textsize(text)
			if text_width < width and text_height < height:
				text_left = (width - text_width) // 2
				text_top = (height - text_height) // 2
				draw.text((text_left, text_top), text, fill=(255, 255, 255))
			content = BytesIO()
			image.save(content, image_format)
			content.seek(0)
			cache.set(key, content, 60 * 60)
		return content


# Views
"""Uncomment if using client-side caching. This calculates 
an opaque eTag value to be passed to the @etag decorator."""
# def generate_etag(request, width, height):
# 	content = 'Placeholder: {0} x {1}'.format(width, height)
# 	return hashlib.sha1(content.encode('utf-8')).hexdigest()

def index(request):
	example = reverse('placeholder', kwargs={'width': 150, 'height': 120})
	return render(request, 'home.html', {'example': request.build_absolute_uri(example)})

"""Uncomment the @etag decorator below if using client-side caching."""
# @etag(generate_etag)
def placeholder(request, width, height):
	form = ImageForm({'width': width, 'height': height})
	if form.is_valid():
		# height = form.cleaned_data['height']
		# width = form.cleaned_data['width']
		image = form.create()
		# return HttpResponse("<h1>All good!</h1>")
		return HttpResponse(image, content_type='image/png')
	else:
		return HttpResponseBadRequest('Invalid Image Request!')


# URLs
urlpatterns = [
	path('', index, name='index'),
	path('placeholder/<int:width>x<int:height>/', placeholder, name='placeholder'),
]


# wsgi
application = get_wsgi_application()

if __name__ == "__main__":
	from django.core.management import execute_from_command_line
	execute_from_command_line(sys.argv)
