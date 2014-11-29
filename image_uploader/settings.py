"""
Django settings for image_uploader project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#89#j(%on%f-h@9wj##5tngep&6s!u53s277(hw140p!1&xuqv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'djcelery',
    'uploader'
)

MIDDLEWARE_CLASSES = (
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'image_uploader.urls'

WSGI_APPLICATION = 'image_uploader.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "../media")
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

#
# We will create these many variants of one single image uploaded by a user.
#
# Format:-
#   ('label', (width, height), cache_it)
#
# We can use this for CSS style class definitions.
# The Third flag is reserved for future usage, Caching certain type of images
# right after the resize operation.
#
IMAGE_VARIANTS = [
    ('thumbnail', (20, 40), True),
    ('small', (40, 30), True),
    ('medium', (100, 60), False),
    ('large', (200, 100), False)
]


#
# Celery queue settings.
#
# img_resize_queue - Jobs are placed here for resize operation.
# img_log          - Log the image details or uploaded img details.
# sync_cdn         - Then place it on a queue to sync with CDN.
#

CELERY_QUEUE = {
}
