from zgw_consumers.client import ZGWClient
from zgw_consumers.models import Service


def get_client(url: str) -> ZGWClient | None:
    client = Service.get_client(url)
    return client
