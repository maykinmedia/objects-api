import pytest

from objects.core.tests.factories import ObjectRecordFactory, ObjectTypeFactory
from objects.token.tests.factories import TokenAuthFactory


@pytest.fixture
def benchmark_assertions(benchmark):
    def wrapper(**kwargs):
        stats = benchmark.stats["stats"]
        for name, value in kwargs.items():
            assert (
                getattr(stats, name) < value
            ), f"{name} {getattr(stats, name)}s exceeded {value}s"

    return wrapper


@pytest.fixture(scope="session")
def setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        object_type = ObjectTypeFactory.create(
            service__api_root="http://localhost:8001/api/v2/",
            uuid="f1220670-8ab7-44f1-a318-bd0782e97662",
        )

        TokenAuthFactory(token="secret", is_superuser=True)

        ObjectRecordFactory.create_batch(
            5000,
            object__object_type=object_type,
            start_at="2020-01-01",
            version=1,
            data={"kiemjaar": "1234"},
        )
