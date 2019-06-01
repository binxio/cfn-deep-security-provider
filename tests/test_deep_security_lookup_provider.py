import uuid
import boto3
import logging
from provider import handler

logging.basicConfig(level=logging.INFO)


def test_search_criteria():
    search = {
        "maxItems": 2,
        "searchCriteria": [{"fieldName": "name", "stringValue": "SMTP Server"}],
    }
    request = Request("Create", "firewallRule", search)
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "PhysicalResourceId" in response
    assert response["PhysicalResourceId"] is not None

    rule_id = response["PhysicalResourceId"]
    request = Request("Update", "firewallRule", search, physical_resource_id=rule_id)
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "PhysicalResourceId" in response
    assert response["PhysicalResourceId"] is not None
    assert response["PhysicalResourceId"] == rule_id


def test_search_shorthand():
    request = Request("Create", "firewallRule", name="SMTP Server")
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "PhysicalResourceId" in response
    assert response["PhysicalResourceId"] is not None


def test_search_combined():
    search = {
        "maxItems": 2,
        "searchCriteria": [
            {"fieldName": "name", "stringValue": "SMTP%", "stringWildcards": True}
        ],
    }
    request = Request("Create", "firewallRule", search=search, name="SMTP Server")
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "PhysicalResourceId" in response
    assert response["PhysicalResourceId"] is not None


class Request(dict):
    def __init__(
        self,
        request_type,
        resource_type,
        search=None,
        name=None,
        physical_resource_id=None,
    ):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": "Custom::DeepSecurityLookup",
                "LogicalResourceId": f"MyCustom{resource_type}",
                "ResourceProperties": {"Type": resource_type},
            }
        )
        if search:
            self["ResourceProperties"]["Search"] = search
        if name:
            self["ResourceProperties"]["Name"] = name

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
