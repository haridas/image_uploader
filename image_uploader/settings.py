"""
@date: 27/Nov/2014
@author: Haridas N<haridas.nss@gmail.com>

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

    # We are on fully restfull system, no need of these middlewares.
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
# Handle Python logging.
#
LOG_ROOT = os.path.join(os.path.dirname(__file__), "../logs")
if not os.path.exists(LOG_ROOT):
    os.makedirs(LOG_ROOT)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file_img_op_logger': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_ROOT, "image_resize.log"),
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_ROOT, "debug.log"),
        },
    },

    'loggers': {
        'log_img_operations': {
            'handlers': ['file_img_op_logger'],
            'level': 'INFO',
        },

        # Catch all logger.
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        }
    }
}

#
# Celery queue settings.
#
# resize_image     - Jobs are placed here for resize operation.
# logger           - Log the image details or uploaded img details.
# cdn_sync         - Then place it on a queue to sync with CDN.
#
# NOTE: All using the default Exchange of type  direct.
#

CELERY_QUEUES = {
    "logger": {
        "routing_key": "logger",
    },
    "resize_image": {
        "routing_key": "resize_image"
    },
    "cdn_sync": {
        "routing_key": "cdn_sync"
    }
}

CELERYD_HIJACK_ROOT_LOGGER = False


#
# AWS S3 Access details.
#
AWS_ACCESS_KEY_ID = '<your-access-key-id>'
AWS_SECRET_ACCESS_KEY = '<your-secret-access-kye>'
AWS_REGION_NAME = 'us-east-1'
S3_IMAGE_BUCKET_NAME = "sync_images"

#
# The CDN task retry settings.
#
TASK_MAX_RETRIES = 3
TASK_RETRY_DELAY = 60  # in sec.
