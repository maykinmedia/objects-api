from django import http
from django.db.utils import DatabaseError
from django.template import TemplateDoesNotExist, loader
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME

import structlog
from open_api_framework.conf.utils import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = structlog.stdlib.get_logger(__name__)

DEFAULT_CODE = "invalid"
DEFAULT_DETAIL = _("Invalid input.")


@requires_csrf_token
def server_error(request, template_name=ERROR_500_TEMPLATE_NAME):
    """
    500 error handler.

    Templates: :template:`500.html`
    Context: None
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        if template_name != ERROR_500_TEMPLATE_NAME:
            # Reraise if it's a missing custom template.
            raise
        return http.HttpResponseServerError(
            "<h1>Server Error (500)</h1>", content_type="text/html"
        )
    context = {"request": request}
    return http.HttpResponseServerError(template.render(context))


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
