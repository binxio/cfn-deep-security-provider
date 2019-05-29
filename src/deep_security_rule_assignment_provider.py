import os
import logging
import boto3
import requests
from deep_security_provider import DeepSecurityProvider


log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


request_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "required": ["PolicyID", "Type"],
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
        },
        "Type": {
            "type": "string",
            "description": "to of rule to assign",
            "enum": [
                "firewall",
                "integritymonitoring",
                "intrusionprevention",
                "loginspection",
            ],
        },
        "PolicyID": {"type": "string", "description": "to assign the rule to"},
        "RuleID": {"type": "string", "description": "to assign to the policy"},
        "RuleName": {"type": "string", "description": "to assign to the policy"},
    },
    "definitions": {
        "connection": {
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
}


class DeepSecurityRuleAssignmentProvider(DeepSecurityProvider):
    def __init__(self):
        super(DeepSecurityRuleAssignmentProvider, self).__init__()

    def is_supported_resource_type(self):
        return self.resource_type == "Custom::DeepSecurityPolicyRuleAssignment"

    def is_valid_cfn_request(self):
        if not super(DeepSecurityRuleAssignmentProvider, self).is_valid_cfn_request():
            return False

        if not self.get("RuleID") and not self.get("RuleName"):
            self.fail("either 'RuleID' or 'RuleName' or both must be present")
            return False

        return True

    def assignment_id_names(self):
        return

    @property
    def assignment_type(self):
        return self.get("Type")

    @property
    def policy_id(self):
        return self.get("PolicyID")

    @property
    def rule_id(self):
        return self.get("RuleID")

    @property
    def rule_name(self):
        return self.get("RuleName")

    def resource_arn(self, rule_id):
        return f"{self.api_endpoint}/policies/{self.policy_id}/{self.assignment_type}/assignments/{rule_id}"

    @property
    def resource_url(self):
        return f"{self.api_endpoint}/policies/{self.policy_id}/{self.assignment_type}/assignments/"

    @property
    def search_url(self):
        return f"{self.api_endpoint}/{self.assignment_type}rules/search"

    def get_rule_id_by_name(self):
        search = {
            "maxItems": 2,
            "searchCriteria": [{"fieldName": "name", "stringValue": self.rule_name}],
        }
        try:
            response = requests.post(self.search_url, headers=self.headers, json=search)
            if response.status_code == 200:
                key_name = f"{self.assignment_type}Rules"
                results = response.json()
                if (
                    key_name in results
                    and results[key_name]
                    and len(results[key_name]) == 1
                ):
                    return results[key_name][0]["ID"]
                else:
                    if key_name not in results:
                        self.fail(
                            f"program error: field {key_name} not found in results."
                        )
                    else:
                        self.fail(
                            f"no {self.assignment_type}Rule found with the name {self.rule_name}"
                        )
            else:
                self.fail(
                    f"no {self.assignment_type}Rule found with the name {self.rule_name}"
                )
        except IOError as e:
            self.fail(
                f"search for {self.assignment_type}Rule with the name {self.rule_name} failed, {e}"
            )
        return None

    def assign(self):
        self.add_api_key()
        try:
            rule_id = self.rule_id
            if not rule_id:
                rule_id = self.get_rule_id_by_name()

            if not rule_id:
                return

            response = requests.post(
                self.resource_url, headers=self.headers, json={"ruleIDs": [rule_id]}
            )
            if response.status_code in (200, 201):
                self.physical_resource_id = self.resource_arn(rule_id)
            else:
                self.fail(
                    "rule assignment for %s failed, %s"
                    % (self.assignment_type, response.text)
                )
        except IOError as e:
            self.fail(f"rule assignment for {self.assignment_type} failed, {e}")

    def create(self):
        self.assign()
        if self.status == "FAILED":
            self.physical_resource_id = "search-failed"

    def update(self):
        self.assign()

    def delete(self):
        if (
            self.physical_resource_id == "could-not-create"
            or not self.physical_resource_id
        ):
            return

        self.add_api_key()
        try:
            response = requests.delete(self.physical_resource_id, headers=self.headers)
            if response.status_code in (200, 204, 404):
                pass
            else:
                self.fail(
                    "Could not unassign {self.assignment_type} rule {self.rule_id} from policy {self.policy_id}, {response.text}"
                )
        except IOError as e:
            self.fail(
                "Could not unassign {self.assignment_type} rule {self.rule_id} from policy {self.policy_id}, {e}"
            )


provider = DeepSecurityRuleAssignmentProvider()


def handler(request, context):
    return provider.handle(request, context)
