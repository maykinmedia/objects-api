import pytest
from furl import furl

BASE_URL = furl("http://localhost:8000/api/v2/")
AUTH_HEADERS = {"Authorization": "Token secret"}


@pytest.mark.django_db
@pytest.mark.benchmark(max_time=60, min_rounds=5)
def test_objects_api_list(benchmark, benchmark_assertions, client, setup):
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
        return client.get((BASE_URL / "objects").set(params), headers=AUTH_HEADERS)

    result = benchmark(make_request)

    assert result.status_code == 200
    assert result.json()["count"] == 5000

    benchmark_assertions(mean=1, max=1)
