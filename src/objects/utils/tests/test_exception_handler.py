import logging  # noqa: TID251
from unittest.mock import patch

import sentry_sdk
from rest_framework.test import APITestCase
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.transport import Transport

from ..views import exception_handler


class InMemoryTransport(Transport):
    """
    Mock transport class to test if Sentry works
    """

    def __init__(self, options):
        self.envelopes = []

    def capture_envelope(self, envelope):
        self.envelopes.append(envelope)


class ExceptionHandlerTests(APITestCase):
    @patch.dict("os.environ", {"DEBUG": "no"})
    def test_error_is_forwarded_to_sentry(self):
        transport = InMemoryTransport({})
        sentry_sdk.init(
            dsn="https://12345@sentry.local/1234",
            transport=transport,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,
                    # Avoid sending logger.exception calls to Sentry
                    event_level=None,
                ),
            ],
        )
        assert len(transport.envelopes) == 0

        exc = Exception("Something went wrong")

        result = exception_handler(exc, context={})

        self.assertIsNotNone(result)

        # Error should be forwarded to sentry
        assert len(transport.envelopes) == 1

        event = transport.envelopes[0]
        assert event.items[0].payload.json["level"] == "error"
        exception = event.items[0].payload.json["exception"]["values"][-1]
        assert exception["value"] == "Something went wrong"
