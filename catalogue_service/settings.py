"""
Django settings for catalogue_service project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
from settings_local import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=pygr69-)_vctwqfo-(09@n15h3z&byq9-m-(#+7a5k9jb5ew+'

# SECURITY WARNING: don't run with debug turned on in production!
# In Setting Local

ALLOWED_HOSTS = ['shopping-tool-web-dev.allume.co', 
                 'shopping-tool-stage.allume.co', 
                 'localhost', 
                 '127.0.0.1',
                 'dev.allume.co',
                 'shopping-tool-web-stage.allume.co', 
                 'shopping-tool-web-prod.allume.co',
                 'shopping-tool-cloudmaaya-web-stage.allume.co'
                 ]


# Application definition

INSTALLED_APPS = [
    # autocomplete
    'dal',
    'dal_select2',
    # -- end autocomplete
    'admin_views', # add customized link for admin, placed before admin site app.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'product_api',
    'shopping_tool',
    'shopping_tool_api',
    'rest_framework_swagger',
    'django_nose',
    'tasks',
    'weather_service',
    'django_celery_results',
    'django_celery_beat',
    'django_extensions',
    'massadmin',
    'stylist_management', # stylist management
    'auditlog', # detail logging
    'merchant_management', # merchant_management
    'order_management', # order_management for operation team to handle final sale or order issue
    'admin_reorder', # reoder admin window for better usability
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware', # detail logging
    'admin_reorder.middleware.ModelAdminReorder', # reoder admin window for better usability
]

ROOT_URLCONF = 'catalogue_service.urls'

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

CJ_HOST_KEY = 'AAAAB3NzaC1kc3MAAACBALaM0N9YqDxytsVkO+On3Ob7fnAM4H0cfxWAxco6dGeOimO7VhC7t9NK++EADh1ZOtm4zXQx9AFlER30vNgtH/Ev4RV6laq0fQQvRnb4B3g5FcVgD4TWm0GC6pGAoT6VRfl2vK6h8pYaS+P/5tnzavwckGoIwqUu6lXbHsC1ZWdzAAAAFQCUKVTBm/+erra+yXAeR3rOvqTrewAAAIEAsaqasLBjcUPoKM0xX2BiFOsezxOJUBDWSmILmZLgqiHU4SK10kiTRd8D7DUD+26xN1Ml/99KMl2OT3VsBb9zyLrvRL8nCx8OKyNjQUdtd4tac7ZDxdeJZSEC8NVFDtFf8R5AQYIj9s6YafzfFPqMhTMj4sJ2T6/vh9sajDsTS30AAACBAJ7k3TaeUP3xpa96DJ5j0kllCSOmjZjxxafpQdoGLZJynlPP0hteK3hGWLFZEtjV48EOPZaEiMaS3w/DGKupMpAeIazLVr0zqFKXoZDKTuj7RSQp7upCE3CjnEjJGs35O0N5P6bG2fbYV/oJSGFdJTAKMKPo+nV5lTKnSptN0ky3'


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework.authentication.SessionAuthentication'
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v1',
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

WSGI_APPLICATION = 'catalogue_service.wsgi.application'



SWAGGER_SETTINGS = {
    'JSON_EDITOR': True,
    'SHOW_REQUEST_HEADERS': True,
    'OPERATIONS_SORTER': 'alpha'
}




# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True


# Added this to remove warning on date fields when loading test fixtures
if 'test' in sys.argv:
    USE_TZ = False
else:
    USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'


LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

CELERY_RESULT_BACKEND = 'django-db'
CELERY_SEND_TASK_ERROR_EMAILS = True
ADMINS = (('Anna Task Failures', 'anna-failures-notification@allume.co'))

# Tell nose to measure coverage 
NOSE_ARGS = [
    '--with-coverage',
    '--exclude-dir-file=nose-exclude.txt',
    '--cover-package=shopping_tool_api, weather_service, shopping_tool',
    '--nocapture',
    '--nologcapture',
]

# Customized user table to WpUser
# AUTH_USER_MODEL = 'shopping_tool.WpUsers'

#Cors config
CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_REGEX_WHITELIST = [r'.*\.allume\.co']

# reorder admin windows
ADMIN_REORDER = (
    'auth',
    # Keep original label and models
    'stylist_management',
    # # Cross-linked models
    {'app': 'merchant_management', 'models': 
    (
    'merchant_management.ShippingPrice',
    'merchant_management.Coupon',
    'merchant_management.MerchantVisibility',
    'merchant_management.MerchantDetail',
    )},
    'django_celery_beat',
    {'app': 'product_api', 'models': 
    (
    'product_api.AllumeCategory',
    'product_api.AllumeRetailerSizeMapping',
    'product_api.CategoryMap',
    'product_api.ColorMap',
    'product_api.ExclusionTerm',
    'product_api.Network',
    'product_api.SynonymCategoryMap'
    )},
    'shopping_tool',
    'auditlog',
    'order_management',
)

# Slack
# Caution!
# Need to change slack credentials and put them in a more secure place in the future
SLACK_BASE_URL = 'https://hooks.slack.com/services/'
SLACK_IDENTIFIER = 'T0F5V1HED/B7N0FRFCN/Z9uiX9MgCQ0cNRcYZwyRmZw6'