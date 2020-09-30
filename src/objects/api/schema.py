from django.conf import settings

from drf_yasg import openapi

description = """An API to access Objects"""

info = openapi.Info(
    title=f"{settings.PROJECT_NAME} API",
    default_version=settings.API_VERSION,
    description=description,
)
