from datetime import datetime

import factory

from objects.core.tests.factories import (
    ObjectRecordFactory as _ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory, TokenAuthFactory

object_type = ObjectTypeFactory.create(
    uuid="f1220670-8ab7-44f1-a318-bd0782e97662",
)

token = TokenAuthFactory.create(token="secret", is_superuser=False)
PermissionFactory.create(
    object_type=object_type,
    mode=PermissionModes.read_only,
    token_auth=token,
    use_fields=False,
)


class ObjectRecordFactory(_ObjectRecordFactory):
    @factory.post_generation
    def add_timestamp(obj, create, extracted, **kwargs):
        """
        This sets a unique datetime per object after creation.
        If you want, you can also merge shared fields here.
        """
        obj.data["nested"] = {"timestamp": datetime.now().isoformat()}
        if create:
            obj.save()


ObjectRecordFactory.create_batch(
    5000,
    object__object_type=object_type,
    _object_type=object_type,
    start_at="2020-01-01",
    version=1,
    data={"identifier": "63f473de-a7a6-4000-9421-829e146499e3", "foo": "bar"},
    add_timestamp=True,
)
ObjectRecordFactory.create(
    object__object_type=object_type,
    _object_type=object_type,
    start_at="2020-01-01",
    version=1,
    data={"identifier": "ec5cde18-40a0-4135-8d97-3500d1730e60", "foo": "bar"},
    add_timestamp=True,
)
