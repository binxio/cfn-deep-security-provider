import os
import logging
import boto3
import requests
from deep_security_provider import DeepSecurityProvider


log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class DeepSecuritySystemSettingProvider(DeepSecurityProvider):
    def __init__(self):
        super(DeepSecuritySystemSettingProvider, self).__init__()

    def is_supported_resource_type(self):
        return self.resource_type.startswith("Custom::DeepSecuritySystemSetting")

    def do_update(self):
        self.add_api_key()
        try:
            response = requests.post(
                self.resource_url, headers=self.headers, json=self.get("Value")
            )
            if response.status_code in (200, 201):
                r = response.json()
            else:
                self.fail(
                    "Could not update the %s, %s" % (self.property_name, response.text)
                )
        except IOError as e:
            self.fail("Could not update the %s, %s" % (self.property_name, str(e)))

    def create(self):
        self.do_update()
        self.physical_resource_id = "global"  ## system systems is not a resource
        if self.status == "FAILED":
            self.physical_resource_id = "failed-to-create"

    def update(self):
        self.do_update()

    def delete(self):
        pass


provider = DeepSecuritySystemSettingProvider()


def handler(request, context):
    return provider.handle(request, context)
