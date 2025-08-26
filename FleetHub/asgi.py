import os
from django.core.asgi import get_asgi_application

# Cambiar esta línea también:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FleetHub.settings.development')

application = get_asgi_application()