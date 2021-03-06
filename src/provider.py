import os
import logging
import deep_security_provider
import deep_security_system_settings_provider
import deep_security_lookup_provider
import deep_security_aws_cloudaccount_provider


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def handler(request, context):
    request_type = request["ResourceType"]
    if request_type == "Custom::DeepSecuritySystemSetting":
        return deep_security_system_settings_provider.handler(request, context)
    elif request_type == "Custom::DeepSecurityLookup":
        return deep_security_lookup_provider.handler(request, context)
    elif request_type == "Custom::DeepSecurityAWSCloudAccount":
        return deep_security_aws_cloudaccount_provider.handler(request, context)
    else:
        return deep_security_provider.handler(request, context)
