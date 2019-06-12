import os
import json
import logging
import boto3
import requests
from cfn_resource_provider import ResourceProvider
from template_substitutor import TemplateSubstitutor

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
                    "default": "https://app.deepsecurity.trendmicro.com/rest",
                    "description": "endpoint of the deep security API",
                },
                "UserNameParameterName": {
                    "type": "string",
                    "default": "/cfn-deep-security-provider/user",
                    "description": "Name of the parameter in the Parameter Store for the username",
                },
                "PasswordParameterName": {
                    "type": "string",
                    "default": "/cfn-deep-security-provider/password",
                    "description": "Name of the parameter in the Parameter Store for the password",
                },
                "TenantParameterName": {
                    "type": "string",
                    "default": "/cfn-deep-security-provider/tenant",
                    "description": "Name of the parameter in the Parameter Store for the tenant",
                },
            },
        },
        "AWSAccountRequest": {
            "type": "object",
            "description": "values for this resource",
        },
    },
}


class DeepSecurityAWSCloudAccountProvider(ResourceProvider):
    def __init__(self):
        super(DeepSecurityAWSCloudAccountProvider, self).__init__()
        self.cookies = {}
        self.ssm = boto3.client("ssm")

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def is_supported_resource_type(self):
        return self.resource_type.startswith("Custom::DeepSecurityAWSCloudAccount")

    @property
    def api_endpoint(self):
        return self.get("Connection", {}).get(
            "URL", "https://app.deepsecurity.trendmicro.com/rest"
        )

    @property
    def resource_url(self):
        return f"{self.api_endpoint}/cloudaccounts/aws"

    @property
    def user_parameter_name(self):
        return self.get("Connection", {}).get(
            "UserParameterName", "/cfn-deep-security-provider/user"
        )

    @property
    def password_parameter_name(self):
        return self.get("Connection", {}).get(
            "PasswordParameterName", "/cfn-deep-security-provider/password"
        )

    @property
    def tenant_parameter_name(self):
        return self.get("Connection", {}).get(
            "PasswordParameterName", "/cfn-deep-security-provider/tenant"
        )

    def get_ssm_parameter(self, name):
        value = self.ssm.get_parameter(Name=name, WithDecryption=True)
        return value["Parameter"]["Value"]

    @property
    def credentials(self):
        return {
            "dsCredentials": {
                "userName": self.user,
                "password": self.password,
                "tenantName": self.tenant,
            }
        }

    @property
    def user(self):
        return self.get_ssm_parameter(self.user_parameter_name)

    @property
    def password(self):
        return self.get_ssm_parameter(self.password_parameter_name)

    @property
    def tenant(self):
        return self.get_ssm_parameter(self.tenant_parameter_name)

    @property
    def session_id(self):
        return self.cookies.get("sID")

    @session_id.setter
    def session_id(self, value):
        if value:
            self.cookies["sID"] = value
        elif "sID" in self.cookies:
            self.cookies.pop("sID")

    def login(self):
        self.session_id = None
        response = requests.post(
            f"{self.api_endpoint}/authentication/login", json=self.credentials
        )
        if response.status_code == 200:
            self.cookies["sID"] = response.text
        else:
            self.fail(
                f"login failed with status code {response.status_code}, {response.text}"
            )

    def logout(self):
        if self.session_id:
            response = requests.delete(
                f"{self.api_endpoint}/authentication/logout",
                cookies=self.cookies,
                params={"sID": self.session_id},
            )
            if response.status_code == 200:
                self.session_id = None
            else:
                log.error(
                    f"failed to logout with status code {response.status_code}, {response.text}"
                )

    @property
    def body(self):
        if self.request_type == "Create":
            return {"AddAwsAccountRequest": self.get("AWSAccountRequest")}
        elif self.request_type == "Update":
            return {"UpdateAwsAccountRequest": self.get("AWSAccountRequest")}
        else:
            return None

    def create(self):
        self.login()
        if self.status == "FAILED":
            return

        try:
            response = requests.post(
                self.resource_url, cookies=self.cookies, json=self.body
            )
            if response.status_code in (200, 201):
                r = response.json()
                self.physical_resource_id = str(
                    r["AddAwsAccountResponse"]["internalId"]
                )
            else:
                self.physical_resource_id = "failed-to-create"
                self.fail(
                    f"Could not create the cloud account with code {response.status_code}, {response.text}"
                )
        except IOError as e:
            self.physical_resource_id = "failed-to-create"
            self.fail(f"failed to create the cloud account, {e}")

        self.logout()

    def update(self):
        self.login()
        if self.status == "FAILED":
            return

        try:
            response = requests.post(
                f"{self.resource_url}/{self.physical_resource_id}/update",
                cookies=self.cookies,
                json=self.body,
            )
            if response.status_code not in (200, 201, 204):
                self.fail(
                    f"Could not update the cloud account with code {response.status_code}, {response.text}"
                )
        except IOError as e:
            self.fail(f"failed to update the cloud account, {e}")
        self.logout()

    def delete(self):
        if (
            not self.physical_resource_id
            or self.physical_resource_id == "failed-to-create"
        ):
            return

        self.login()
        if self.status == "FAILED":
            return

        try:
            response = requests.delete(
                f"{self.resource_url}/{self.physical_resource_id}", cookies=self.cookies
            )
            if response.status_code not in (200, 204, 404):
                self.fail(
                    f"Could not delete the cloud account with code {response.status_code}, {response.text}"
                )
        except IOError as e:
            self.fail(f"failed to delete the cloud account, {e}")

        self.logout()


provider = DeepSecurityAWSCloudAccountProvider()


def handler(request, context):
    return provider.handle(request, context)
