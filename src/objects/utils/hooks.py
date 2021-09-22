from django.conf import settings


def postprocess_versions(result, generator, **kwargs):
    major_version = result["info"]["version"]
    result["info"]["version"] = f"{settings.VERSIONS[major_version]} ({major_version})"
    return result


def postprocess_servers(result, generator, **kwargs):
    major_version = result["info"]["version"]
    result["servers"] = settings.OAS_SERVERS[major_version]
    return result
