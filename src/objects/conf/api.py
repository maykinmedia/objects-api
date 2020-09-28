from vng_api_common.conf.api import *  # noqa - imports white-listed

API_VERSION = "0.1.0"


# api settings
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    # test
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# OAS settings
SWAGGER_SETTINGS = BASE_SWAGGER_SETTINGS.copy()
SWAGGER_SETTINGS.update(
    {
        "DEFAULT_INFO": "objects.api.schema.info",
        "SECURITY_DEFINITIONS": None,
    }
)
