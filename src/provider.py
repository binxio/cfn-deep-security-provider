import os
import logging
import deep_security_provider
import deep_security_system_settings_provider


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def handler(request, context):
    request_type = request["ResourceType"]
    if request_type == "Custom::DeepSecuritySystemSetting":
        return deep_security_system_settings_provider.handler(request, context)
    else:
        return deep_security_provider.handler(request, context)
