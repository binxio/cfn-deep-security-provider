import uuid
import boto3
import logging
from provider import handler
from test_deep_security_provider import Request as ResourceRequest
from test_deep_security_lookup_provider import Request as LookupRequest
from cfn import cfn, delete_all_resources

logging.basicConfig(level=logging.INFO)


def test_create_assignment():
    response = {"PhysicalResourceId": "could-not-create"}
    try:
        name = "u{}".format(uuid.uuid4())
        policy = {
            "name": name
        }
        request = ResourceRequest("Create", "Policy", policy)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        policy_id = response["PhysicalResourceId"]

        request = LookupRequest("Create", "firewallRule", name="SMTP Server")
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        rule_id = response["PhysicalResourceId"]

        request = Request("Create", "firewall", policy_id, rule_id)
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]

        request = Request("Update", "firewall", policy_id, rule_id)
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]

        request = Request("Create", "firewall", policy_id, rule_name="FTP Server")
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]

    finally:
        delete_all_resources(handler)



class Request(dict):
    def __init__(self, request_type, assignment_type, policy_id, rule_id=None, rule_name=None, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": "Custom::DeepSecurityPolicyRuleAssignment",
                "LogicalResourceId": f"MyCustom{assignment_type}",
                "ResourceProperties": {"Type": assignment_type, "PolicyID": policy_id}
            }
        )
        if rule_id:
            self["ResourceProperties"]["RuleID"] = rule_id
        if rule_name:
            self["ResourceProperties"]["RuleName"] = rule_name

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id