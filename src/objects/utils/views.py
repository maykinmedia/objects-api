from django.db.utils import DatabaseError
from django.utils.translation import gettext_lazy as _

import sentry_sdk
import structlog
from open_api_framework.conf.utils import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = structlog.stdlib.get_logger(__name__)

DEFAULT_CODE = "invalid"
DEFAULT_DETAIL = _("Invalid input.")


def exception_handler(exc, context):
    """
    Transform 5xx errors into DSO-compliant shape.
    """
    response = drf_exception_handler(exc, context)
    if not response:
        if config("DEBUG", default=False):
            return None

        data = {
            "code": "error",
            "title": "Internal Server Error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": _("A server error has occurred."),
        }
        event = "api.uncaught_exception"

        if isinstance(exc, DatabaseError) and "jsonpath" in exc.args[0]:
            # provide user-friendly response if data_icontains was used but DB couldn't process it
            data["detail"] = (
                "This search operation is not supported by the underlying data store."
            )
            event = "api.database_exception"

        sentry_sdk.capture_exception(exc)

        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)
        logger.exception(event, exc_info=exc)

        return response

    # exception logger event
    logger.exception(
        "api.handled_exception",
        title=getattr(exc, "default_detail", DEFAULT_DETAIL).strip("'"),
        code=getattr(exc, "default_code", DEFAULT_CODE),
        status=getattr(response, "status_code", status.HTTP_400_BAD_REQUEST),
        data=getattr(response, "data", {}),
        exc_info=False,
    )

    return response
