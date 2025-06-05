from objects.core.tests.factories import ObjectRecordFactory, ObjectTypeFactory
from objects.token.tests.factories import TokenAuthFactory

object_type = ObjectTypeFactory.create(
    service__api_root="http://localhost:8001/api/v2/",
    uuid="f1220670-8ab7-44f1-a318-bd0782e97662",
)

token = TokenAuthFactory(token="secret", is_superuser=True)

ObjectRecordFactory.create_batch(
    15000000,
    object__object_type=object_type,
    start_at="2020-01-01",
    version=1,
    data={"kiemjaar": "1234"},
)
