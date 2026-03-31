from opentelemetry import metrics

openobject_meter = metrics.get_meter("openobject.api")

objects_create_counter = openobject_meter.create_counter(
    "openobject.object.creates",
    description="Amount of objects created (via the API).",
    unit="1",
)
objects_update_counter = openobject_meter.create_counter(
    "openobject.object.updates",
    description="Amount of objects updated (via the API).",
    unit="1",
)
objects_delete_counter = openobject_meter.create_counter(
    "openobject.object.deletes",
    description="Amount of objects deleted (via the API).",
    unit="1",
)

objecttype_create_counter = openobject_meter.create_counter(
    "openobject.objecttype.creates",
    description="Amount of objecttypes created (via the API).",
    unit="1",
)
objecttype_update_counter = openobject_meter.create_counter(
    "openobject.objecttype.updates",
    description="Amount of objecttypes updated (via the API).",
    unit="1",
)
objecttype_delete_counter = openobject_meter.create_counter(
    "openobject.objecttype.deletes",
    description="Amount of objecttypes deleted (via the API).",
    unit="1",
)
