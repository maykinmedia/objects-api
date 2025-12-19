from opentelemetry import metrics

object_meter = metrics.get_meter("objects.api")

objects_create_counter = object_meter.create_counter(
    "objects.object.creates",
    description="Amount of objects created (via the API).",
    unit="1",
)
objects_update_counter = object_meter.create_counter(
    "objects.object.updates",
    description="Amount of objects updated (via the API).",
    unit="1",
)
objects_delete_counter = object_meter.create_counter(
    "objects.object.deletes",
    description="Amount of objects deleted (via the API).",
    unit="1",
)

objecttype_meter = metrics.get_meter("objecttypes.api.v2")

objecttype_create_counter = objecttype_meter.create_counter(
    "objecttypes.objecttype.creates",
    description="Amount of objecttypes created (via the API).",
    unit="1",
)
objecttype_update_counter = objecttype_meter.create_counter(
    "objecttypes.objecttype.updates",
    description="Amount of objecttypes updated (via the API).",
    unit="1",
)
objecttype_delete_counter = objecttype_meter.create_counter(
    "objecttypes.objecttype.deletes",
    description="Amount of objecttypes deleted (via the API).",
    unit="1",
)
