import uuid
import logging
from provider import handler
import boto3
from cfn import cfn

logging.basicConfig(level=logging.INFO)


ssm = boto3.client("ssm")
sts = boto3.client("sts")


def test_crud():
    response = {"PhysicalResourceId": "could-not-create"}
    try:
        account_id = sts.get_caller_identity()["Account"]
        sts_external_id = ssm.get_parameter(
            Name="/cfn-deep-security-provider/sts-external-id", WithDecryption=True
        )["Parameter"]["Value"]
        aws_account_request = {
            "useInstanceRole": False,
            "crossAccountRole": {
                "roleArn": f"arn:aws:iam::{account_id}:role/DeepSecurity",
                "externalId": sts_external_id,
            },
            "workspacesEnabled": False,
        }
        request = Request("Create", aws_account_request)
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert "PhysicalResourceId" in response
        assert response["PhysicalResourceId"] is not None

        request = Request("Update", aws_account_request)
        request = Request("Update", aws_account_request, response["PhysicalResourceId"])
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]
        assert "PhysicalResourceId" in response
        assert response["PhysicalResourceId"] is not None

    finally:
        request = Request("Delete", {}, response["PhysicalResourceId"])
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]

        # duplicate delete should be oke..
        request = Request("Delete", {}, response["PhysicalResourceId"])
        response = cfn(handler, request, {})
        assert response["Status"] == "SUCCESS", response["Reason"]


class Request(dict):
    def __init__(self, request_type, value, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": f"Custom::DeepSecurityAWSCloudAccount",
                "LogicalResourceId": f"MyCustomCloudAccount",
                "ResourceProperties": {"AWSAccountRequest": value},
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
