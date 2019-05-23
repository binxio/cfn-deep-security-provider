import os
import logging

from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider

log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

request_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object"
}

class DeepSecurityProvider(ResourceProvider):

    def __init__(self):
        super(DeepSecurityProvider, self).__init__()

provider = DeepSecurityProvider()


def handler(request, context):
    return provider.handle(request, context)
