# fleethub/settings/development.py
from .base import *

# Development specific settings
DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'