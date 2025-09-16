from django.db.utils import DatabaseError

import structlog
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = structlog.stdlib.get_logger(__name__)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    # provide user-friendly response if data_icontains was used but DB couldn't process it
    if not response and isinstance(exc, DatabaseError) and "jsonpath" in exc.args[0]:
        data = {
            "detail": "This search operation is not supported by the underlying data store."
        }
        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)
        logger.exception("search_failed_for_datastore", exc_info=exc)

    return response
