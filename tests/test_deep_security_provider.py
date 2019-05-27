import uuid
import boto3
import logging
from provider import handler

logging.basicConfig(level=logging.INFO)


def test_crud():
    response = {"PhysicalResourceId": "could-not-create"}
    try:
        name = "u{}".format(uuid.uuid4())
        context = {
            "name": name,
            "description": f"test {name}",
            "minimumAgentVersion": "6.0.0.0",
            "localConnectionsEnabled": True,
            "remoteConnectionsEnabled": True,
            "noConnectionEnabled": True,
            "noInternetEnabled": True,
            "restrictedInterfacesEnabled": True,
        }
        request = Request("Create", "Context", context)
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert "PhysicalResourceId" in response
        assert response["PhysicalResourceId"] is not None

        context["localConnectionsEnabled"] = False
        request = Request("Update", "Context", context, response["PhysicalResourceId"])
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert "PhysicalResourceId" in response
        assert response["PhysicalResourceId"] is not None
    finally:
        request = Request("Delete", "Context", {}, response["PhysicalResourceId"])
        response = handler(request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]


class Request(dict):
    def __init__(self, request_type, resource_type, value, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": f"Custom::DeepSecurity{resource_type}",
                "LogicalResourceId": f"MyCustom{resource_type}",
                "ResourceProperties": {"Value": value},
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
