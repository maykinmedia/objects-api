import pytest
import requests
from furl import furl

BASE_URL = furl("http://localhost:8000/api/v2/")
AUTH_HEADERS = {"Authorization": "Token secret"}


@pytest.mark.benchmark(max_time=60, min_rounds=5)
def test_objects_api_list_large_page_size_page_1(benchmark, benchmark_assertions):
    """
    Regression test for maykinmedia/objects-api#538
    """
    params = {
        "pageSize": 1000,
        "type": "http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662",
        "data_attrs": "identifier__exact__63f473de-a7a6-4000-9421-829e146499e3",
        "ordering": "-record__data__nested__timestamp",
    }

    def make_request():
        return requests.get((BASE_URL / "objects").set(params), headers=AUTH_HEADERS)

    result = benchmark(make_request)

    assert result.status_code == 200
    assert result.json()["count"] == 5000

    benchmark_assertions(mean=1, max=1)


@pytest.mark.benchmark(max_time=60, min_rounds=5)
def test_objects_api_list_large_page_size_page_5(benchmark, benchmark_assertions):
    """
    Regression test for maykinmedia/objects-api#538
    """
    params = {
        "pageSize": 1000,
        "page": 5,
        "type": "http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662",
        "data_attrs": "identifier__exact__63f473de-a7a6-4000-9421-829e146499e3",
        "ordering": "-record__data__nested__timestamp",
    }

    def make_request():
        return requests.get((BASE_URL / "objects").set(params), headers=AUTH_HEADERS)

    result = benchmark(make_request)

    assert result.status_code == 200
    assert result.json()["count"] == 5000

    benchmark_assertions(mean=1, max=1)


@pytest.mark.benchmark(max_time=60, min_rounds=5)
def test_objects_api_list_small_page_size_page_20(benchmark, benchmark_assertions):
    """
    Regression test for maykinmedia/objects-api#538
    """
    params = {
        "pageSize": 20,
        "page": 50,
        "type": "http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662",
        "data_attrs": "identifier__exact__63f473de-a7a6-4000-9421-829e146499e3",
        "ordering": "-record__data__nested__timestamp",
    }

    def make_request():
        return requests.get((BASE_URL / "objects").set(params), headers=AUTH_HEADERS)

    result = benchmark(make_request)

    assert result.status_code == 200
    assert result.json()["count"] == 5000

    benchmark_assertions(mean=1, max=1)


@pytest.mark.benchmark(max_time=60, min_rounds=5)
def test_objects_api_list_filter_one_result(benchmark, benchmark_assertions):
    """
    Regression test for maykinmedia/objects-api#538
    """
    params = {
        "pageSize": 1,
        "type": "http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662",
        "data_attrs": "identifier__exact__ec5cde18-40a0-4135-8d97-3500d1730e60",
        "ordering": "-record__data__nested__timestamp",
    }

    def make_request():
        return requests.get((BASE_URL / "objects").set(params), headers=AUTH_HEADERS)

    result = benchmark(make_request)

    assert result.status_code == 200
    assert result.json()["count"] == 1

    benchmark_assertions(mean=1, max=1)


@pytest.mark.benchmark(max_time=60, min_rounds=5)
def test_objects_api_list_filter_by_object_type(benchmark, benchmark_assertions):
    """
    Regression test for maykinmedia/objects-api#677
    """
    params = {
        "pageSize": 100,
        "type": "http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662",
        "ordering": "-record__data__nested__timestamp",
    }

    def make_request():
        return requests.get((BASE_URL / "objects").set(params), headers=AUTH_HEADERS)

    result = benchmark(make_request)

    assert result.status_code == 200
    assert result.json()["count"] == 5001

    benchmark_assertions(mean=1, max=1)
