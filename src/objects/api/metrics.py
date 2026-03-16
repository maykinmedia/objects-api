from opentelemetry import metrics

openobjecten_meter = metrics.get_meter("openobjecten.api")

objects_create_counter = openobjecten_meter.create_counter(
    "openobjecten.object.creates",
    description="Amount of objects created (via the API).",
    unit="1",
)
objects_update_counter = openobjecten_meter.create_counter(
    "openobjecten.object.updates",
    description="Amount of objects updated (via the API).",
    unit="1",
)
objects_delete_counter = openobjecten_meter.create_counter(
    "openobjecten.object.deletes",
    description="Amount of objects deleted (via the API).",
    unit="1",
)

objecttype_create_counter = openobjecten_meter.create_counter(
    "openobjecten.objecttype.creates",
    description="Amount of objecttypes created (via the API).",
    unit="1",
)
objecttype_update_counter = openobjecten_meter.create_counter(
    "openobjecten.objecttype.updates",
    description="Amount of objecttypes updated (via the API).",
    unit="1",
)
objecttype_delete_counter = openobjecten_meter.create_counter(
    "openobjecten.objecttype.deletes",
    description="Amount of objecttypes deleted (via the API).",
    unit="1",
)
