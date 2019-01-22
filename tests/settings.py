# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import
import os
import django

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "8&afbjor18ncs9bo5kzfxv1pufu(t-t(4wle2hp_6l=4kvx+1("

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    os.path.join(SETTINGS_PATH, '../quartet_4nt4r3s/templates'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
]

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    'quartet_epcis.apps.QuartetEPCISConfig',
    'quartet_templates.apps.QuartetTemplatesConfig',
    'quartet_output.apps.QuartetOutputConfig',
    'quartet_capture.apps.QuartetCaptureConfig',
    "serialbox",
    'list_based_flavorpack.apps.ListBasedFlavorpackConfig',
    "quartet_4nt4r3s",
]

SITE_ID = 1

if django.VERSION >= (1, 10):
    MIDDLEWARE = ()
else:
    MIDDLEWARE_CLASSES = ()

DEFAULT_ANTARES_RULE='epcis'
