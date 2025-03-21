import requests
from furl import furl

BASE_URL = furl("http://localhost:8000/api/v2/")
AUTH_HEADERS = {"Authorization": "Token secret"}


def test_objects_api_list(benchmark):
    """
    Regression test for maykinmedia/objects-api#538
    """
    params = {
        "pageSize": 1000,
        "type": "http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662",
        "data_attrs": "kiemjaar__exact__1234",
        "ordering": "-record__data__contactmoment__datumContact",
    }

    def make_request():
        return requests.get((BASE_URL / "objects").set(params), headers=AUTH_HEADERS)

    result = benchmark(make_request)

    assert result.status_code == 200
    assert result.json()["count"] == 5000
