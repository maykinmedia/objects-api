from django.conf import settings


def postprocess_servers(result, generator, **kwargs):
    major_version = result["info"]["version"]
    result["servers"] = settings.OAS_SERVERS[major_version]
    return result
