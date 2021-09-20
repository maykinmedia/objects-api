import logging

from django import http
from django.db.utils import DatabaseError
from django.template import TemplateDoesNotExist, loader
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


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
    response = drf_exception_handler(exc, context)

    # provide user-friendly response if data_icontains was used but DB couldn't process it
    if not response and isinstance(exc, DatabaseError) and "jsonpath" in exc.args[0]:
        data = {
            "detail": "This search operation is not supported by the underlying data store."
        }
        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)
        logger.exception(exc)

    return response
