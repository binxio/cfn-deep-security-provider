import boto3
import os
import uuid
import json
from copy import copy
from datetime import datetime
import logging
from datadog_event_forwarder import load_ssm_parameters
from datadog_event_forwarder import connect_to_datadog
from datadog_event_forwarder import handler
from datadog_event_forwarder import tags
from datadog_event_forwarder import date_happened
from datadog_event_forwarder import ossec_level_to_log_level
from datadog_event_forwarder import log_level


logging.basicConfig(level=logging.INFO)


def test_load_ssm_parameters():
    name = f"n{uuid.uuid4()}"
    value = f"value for {name}"
    ssm = boto3.client("ssm")
    try:
        ssm.put_parameter(Name=name, Type="String", Value=value)
        os.environ["LOAD_ME_FROM_SSM"] = f"ssm:///{name}?default=load-me"
        load_ssm_parameters(os.environ)
        assert os.getenv("LOAD_ME_FROM_SSM") == value
    finally:
        ssm.delete_parameter(Name=name)


def test_load_ssm_parameter_default():
    name = f"n{uuid.uuid4()}"
    os.environ["LOAD_ME_FROM_SSM"] = f"ssm:///{name}?default=load-me"
    load_ssm_parameters(os.environ)
    assert os.getenv("LOAD_ME_FROM_SSM") == "load-me"


def test_failed_load_ssm_parameter_no_default():
    name = f"n{uuid.uuid4()}"
    value = f"ssm:///{name}"
    os.environ["LOAD_ME_FROM_SSM"] = value
    load_ssm_parameters(os.environ)
    assert os.getenv("LOAD_ME_FROM_SSM") == value


def test_invalid_load_ssm_parameter():
    name = f"n{uuid.uuid4()}"
    value = f"ssm://{name}"
    os.environ["LOAD_ME_FROM_SSM"] = value
    load_ssm_parameters(os.environ)
    assert os.getenv("LOAD_ME_FROM_SSM") == value


def test_send_event_to_datadog():
    event = sns_event(system_event)
    handler(event, {})

    event = sns_event(anti_malware_event)
    handler(event, {})


def test_invalid_message():
    event = sns_event({})
    handler(event, {})

    event["Records"][0]["Sns"]["Message"] = "{"
    handler(event, {})


def test_tags():
    result = tags("A=1, B=2, D, C=3")
    assert len(result) == 4
    assert result[0] == "A:1"
    assert result[1] == "B:2"
    assert result[2] == "D:"
    assert result[3] == "C:3"


def test_date_happened():
    log_date = datetime.now()
    message = {"LogDate": log_date.isoformat()}
    result = date_happened(message)
    assert result == int(log_date.timestamp())

    message = {}
    result = date_happened(message)
    assert result >= datetime.now().timestamp() - 1


def test_ossec_level_to_log_level():
    message = {"OSSEC_Level": -1}
    assert ossec_level_to_log_level(message) == "info"
    message = {"OSSEC_Level": 1}
    assert ossec_level_to_log_level(message) == "info"
    message = {"OSSEC_Level": 5}
    assert ossec_level_to_log_level(message) == "warning"
    message = {"OSSEC_Level": 13}
    assert ossec_level_to_log_level(message) == "error"
    message = {"OSSEC_Level": 116}
    assert ossec_level_to_log_level(message) == "error"


def test_log_level():
    message = {"Severity": 1}
    assert log_level(message) == "info"
    message = {"Severity": 2}
    assert log_level(message) == "warning"
    message = {"Severity": 3}
    assert log_level(message) == "error"
    message = {"Severity": 4}
    assert log_level(message) == "error"
    message = {"OSSEC_Level": 15}
    assert log_level(message) == "error"
    message = {}
    assert log_level(message) == "info"


def sns_event(message) -> dict:
    return copy(
        {
            "Records": [
                {
                    "EventVersion": "1.0",
                    "EventSubscriptionArn": "arn:aws:sns:EXAMPLE",
                    "EventSource": "aws:sns",
                    "Sns": {
                        "SignatureVersion": "1",
                        "Timestamp": datetime.now().isoformat(),
                        "Signature": "EXAMPLE",
                        "SigningCertUrl": "EXAMPLE",
                        "MessageId": f"{uuid.uuid4()}",
                        "Message": json.dumps(message),
                        "MessageAttributes": {
                            "Test": {"Type": "String", "Value": "TestString"},
                            "TestBinary": {"Type": "Binary", "Value": "TestBinary"},
                        },
                        "Type": "Notification",
                        "UnsubscribeUrl": "EXAMPLE",
                        "TopicArn": "arn:aws:sns:EXAMPLE",
                        "Subject": "TestInvoke",
                    },
                }
            ]
        }
    )


system_event = [
    {
        "ActionBy": "System",
        "Description": "Alert: New Pattern Update is Downloaded and Available\\nSeverity: Warning\\n",
        "EventID": 6813,
        "EventType": "SystemEvent",
        "LogDate": "2018-12-04T15:54:24.086Z",
        "ManagerNodeID": 123,
        "ManagerNodeName": "job7-123",
        "Number": 192,
        "Origin": 3,
        "OriginString": "Manager",
        "Severity": 1,
        "SeverityString": "Info",
        "Tags": "",
        "TargetID": 1,
        "TargetName": "ec2-12-123-123-123.us-west-2.compute.amazonaws.com",
        "TargetType": "Host",
        "TenantID": 123,
        "TenantName": "Umbrella Corp.",
        "Title": "Alert Ended",
    }
]

anti_malware_event = [
    {
        "AMTargetTypeString": "N/A",
        "ATSEDetectionLevel": 0,
        "CreationTime": "2018-12-04T15:57:18.000Z",
        "EngineType": 1_207_959_848,
        "EngineVersion": "10.0.0.1040",
        "ErrorCode": 0,
        "EventID": 1,
        "EventType": "AntiMalwareEvent",
        "HostAgentGUID": "4A5BF25A-4446-DD8B-DFB7-564C275F5F6B",
        "HostAgentVersion": "11.1.0.163",
        "HostID": 1,
        "HostOS": "Amazon Linux (64 bit) (4.14.62-65.117.amzn1.x86_64)",
        "HostSecurityPolicyID": 3,
        "HostSecurityPolicyName": "PolicyA",
        "Hostname": "ec2-12-123-123-123.us-west-2.compute.amazonaws.com",
        "InfectedFilePath": "/tmp/eicar_1543939038890.txt",
        "LogDate": "2018-12-04T15:57:19.000Z",
        "MajorVirusType": 2,
        "MajorVirusTypeString": "Virus",
        "MalwareName": "Eicar_test_file",
        "MalwareType": 1,
        "ModificationTime": "2018-12-04T15:57:18.000Z",
        "Origin": 0,
        "OriginString": "Agent",
        "PatternVersion": "14.665.00",
        "Protocol": 0,
        "Reason": "Default Real-Time Scan Configuration",
        "ScanAction1": 4,
        "ScanAction2": 3,
        "ScanResultAction1": -81,
        "ScanResultAction2": 0,
        "ScanResultString": "Quarantined",
        "ScanType": 0,
        "ScanTypeString": "Real Time",
        "Tags": "",
        "TenantID": 123,
        "TenantName": "Umbrella Corp.",
    },
    {
        "AMTargetTypeString": "N/A",
        "ATSEDetectionLevel": 0,
        "CreationTime": "2018-12-04T15:57:21.000Z",
    },
    {
        "AMTargetTypeString": "N/A",
        "ATSEDetectionLevel": 0,
        "CreationTime": "2018-12-04T15:57:29.000Z",
    },
]
