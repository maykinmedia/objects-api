from django.conf import settings
from django.http import HttpRequest

from furl import furl


def get_domain() -> str:
    """
    Obtain the domain/netloc according to settings or configuration.
    """
    from django.contrib.sites.models import Site

    if settings.OBJECTS_DOMAIN:
        return settings.OBJECTS_DOMAIN

    return Site.objects.get_current().domain


def build_absolute_url(path: str, request: HttpRequest | None = None) -> str:
    if request is not None:
        return request.build_absolute_uri(path)

    domain = get_domain()
    _furl = furl(
        scheme="https" if settings.IS_HTTPS else "http",
        netloc=domain,
        path=path,
    )
    return _furl.url
