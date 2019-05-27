import os
import logging
import deep_security_provider


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def handler(request, context):
    return deep_security_provider.handler(request, context)
