import urlparse
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient


# TODO: this should either be an actual class or named differently
def TRSClient(host, auth, proto):
    """
    Build a :class:`SwaggerClient` from a url to the Swagger
    specification for the GA4GH Tool Registry Service RESTful API.
    """
    http_client = RequestsClient()
    split = urlparse.urlsplit("%s://%s/" % (proto, host))

    http_client.set_api_key(
        split.hostname, auth,
        param_name='Authorization', param_in='header'
    )

    return SwaggerClient.from_url(
        "%s://%s/swagger.json" % (proto, host),
        http_client=http_client,
        config={'use_models': False, 'validate_swagger_spec': False}
    )
