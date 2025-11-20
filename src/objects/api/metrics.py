from opentelemetry import metrics

meter = metrics.get_meter("objects.api")

objects_create_counter = meter.create_counter(
    "objects.objects.creates",
    description="Amount of objects created (via the API).",
    unit="1",
)
objects_update_counter = meter.create_counter(
    "objects.objects.updates",
    description="Amount of objects updated (via the API).",
    unit="1",
)
objects_delete_counter = meter.create_counter(
    "objects.objects.deletes",
    description="Amount of objects deleted (via the API).",
    unit="1",
)
