from django.apps import AppConfig
import json
# from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExportResult,
    SpanExporter,
)
import sys
from os import linesep
from elasticapm.contrib.opentelemetry import trace

# class CustomSpanExporter(SpanExporter):
#     def __init__(
#         self,
#         service_name=None,
#         out=sys.stdout,
#         formatter=lambda span: span.to_json()
#         + linesep,
#     ):
#         self.out = out
#         self.formatter = formatter
#         self.service_name = service_name

#     def export(self, spans) -> SpanExportResult:
#         for span in spans:
#             data = json.loads(span.to_json())
#             print(data)
#             self.out.write(self.formatter(span))
#         self.out.flush()
#         return SpanExportResult.SUCCESS


class UtilsConfig(AppConfig):
    name = "objects.utils"

    def ready(self):
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )

        from . import checks  # noqa
        from . import oas_extensions  # noqa

        provider = TracerProvider()
        trace.set_tracer_provider(provider)

        provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter(service_name="Objects API"))
        )
