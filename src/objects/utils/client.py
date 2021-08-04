from typing import Optional

from zgw_consumers.client import ZGWClient
from zgw_consumers.models import Service


def get_client(url: str) -> Optional[ZGWClient]:
    client = Service.get_client(url)
    return client
