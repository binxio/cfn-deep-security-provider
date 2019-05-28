import os
import logging
import boto3
import requests
from cfn_resource_provider import ResourceProvider


log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

request_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "Connection": {
            "type": "object",
            "properties": {
                "URL": {
                    "type": "string",
                    "default": "https://app.deepsecurity.trendmicro.com/api",
                    "description": "endpoint of the deep security API",
                },
                "Version": {
                    "type": "string",
                    "default": "v1",
                    "description": "of the api to use",
                },
                "ApiKeyParameterName": {
                    "type": "string",
                    "default": "/cfn-deep-security-provider/api_key",
                    "description": "Name of the parameter in the Parameter Store for the API key",
                },
            },
        }
    },
    "Value": {"type": "object", "description": "values for this resource"},
}


class DeepSecurityProvider(ResourceProvider):
    def __init__(self):
        super(DeepSecurityProvider, self).__init__()
        self.headers = {}
        self.ssm = boto3.client("ssm")

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def is_supported_resource_type(self):
        return self.resource_type.startswith("Custom::DeepSecurity")

    @property
    def property_name(self):
        return self.resource_type.replace("Custom::DeepSecurity", "")

    @property
    def property_name_plural(self):
        name = self.property_name.lower()
        if name[-1] == 'y':
                return '{}ies'.format(name[0:-1])
        else:
                return '{}s'.format(name)

    @property
    def resource_url(self):
        return "{}/{}s".format(
            self.get("Connection", {}).get(
                "URL", "https://app.deepsecurity.trendmicro.com/api"
            ),
            self.property_name.lower(),
        )

    @property
    def api_key_parameter_name(self):
        return self.get("Connection", {}).get(
            "ApiKeyParameterName", "/cfn-deep-security-provider/api_key"
        )

    def get_ssm_parameter(self, name):
        value = self.ssm.get_parameter(Name=name, WithDecryption=True)
        return value["Parameter"]["Value"]

    def add_api_key(self):
        self.headers["api-secret-key"] = self.get_ssm_parameter(
            self.api_key_parameter_name
        )
        self.headers["api-version"] = self.get("Connection", {}).get("Version", "v1")

    def create(self):
        self.add_api_key()
        try:
            response = requests.post(
                self.resource_url, headers=self.headers, json=self.get("Value")
            )
            if response.status_code in (200, 201):
                r = response.json()
                self.physical_resource_id = str(r["ID"])
            else:
                self.physical_resource_id = "failed-to-create"
                self.fail(
                    "Could not create the %s, %s" % (self.property_name, response.text)
                )
        except IOError as e:
            self.physical_resource_id = "failed-to-create"
            self.fail("Could not create the %s, %s" % (self.property_name, str(e)))

    def update(self):
        self.add_api_key()
        url = "%s/%s" % (self.resource_url, self.physical_resource_id)

        try:
            response = requests.post(url, headers=self.headers, json=self.get("Value"))
            if response.status_code in (200, 201):
                r = response.json()
                self.physical_resource_id = str(r["ID"])
            else:
                self.fail(
                    "Could not update the %s, %s" % (self.property_name, response.text)
                )
        except IOError as e:
            self.fail("Could not update the %s, %s" % (self.property_name, str(e)))

    def delete(self):
        self.add_api_key()
        url = "%s/%s" % (self.resource_url, self.physical_resource_id)

        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204, 404):
                pass
            elif response.status_code == 400:
                self.success("delete failed, %s" % response.text)
            else:
                self.fail(
                    "Could not delete the %s, %s" % (self.property_name, response.text)
                )
        except IOError as e:
            self.fail("Could not delete the %s, %s" % (self.property_name, str(e)))


provider = DeepSecurityProvider()


def handler(request, context):
    return provider.handle(request, context)
