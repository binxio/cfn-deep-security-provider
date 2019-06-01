import pytest
import re
import boto3
import logging
from template_substitutor import TemplateSubstitutor


@pytest.fixture
def expander():
    ssm = boto3.client("ssm")
    api_key = ssm.get_parameter(
        Name="/cfn-deep-security-provider/api_key", WithDecryption=True
    )["Parameter"]["Value"]
    return TemplateSubstitutor(
        "https://app.deepsecurity.trendmicro.com/api", api_key, "v1"
    )


def test_simple(expander):
    simple = '{{lookup "firewallRule" "FTP Server"}}'
    result, err = expander.replace_lookups(simple)
    assert not err, err

    assert re.fullmatch(r"[0-9]*", result), f"expected an integer, got '{result}'"

    simple = '{{lookup "directory" "My Name"}}'
    result, err = expander.replace_lookups(simple)
    assert err
    assert result == simple


def test_multiple(expander):
    simple = (
        '{{lookup "firewallRule" "FTP Server"}}|{{lookup "firewallRule" "SMTP Server"}}'
    )
    result, err = expander.replace_lookups(simple)
    assert not err, err

    assert re.fullmatch(
        r"[0-9]+\|[0-9]+", result
    ), f"expected two integers separated by |, got '{result}'"


def test_array(expander):
    array = [
        '{{lookup "firewallRule" "FTP Server"}}',
        '{{lookup "firewallRule" "SMTP Server"}}',
    ]
    result, err = expander.replace_lookups(array)
    assert not err, err

    for i, v in enumerate(result):
        assert re.fullmatch(r"[0-9]+", v), f"expected integer at offset {i}, got '{v}'"


def test_dict(expander):
    d = {
        "ftp-id": '{{lookup "firewallRule" "FTP Server"}}',
        "stmp-id": '{{lookup "firewallRule" "SMTP Server"}}',
    }
    result, err = expander.replace_lookups(d)
    assert not err, err

    for k, v in result.items():
        assert re.fullmatch(r"[0-9]+", v), f"expected integer in field {k}, got '{v}'"


def test_nested_array(expander):
    d = {
        "ftp-id": ['{{lookup "firewallRule" "FTP Server"}}'],
        "mail": {"stmp-id": '{{lookup "firewallRule" "SMTP Server"}}'},
    }
    result, err = expander.replace_lookups(d)
    assert not err, err

    for i, v in enumerate(result["ftp-id"]):
        assert re.fullmatch(r"[0-9]+", v), f"expected integer at offset {i}, got '{v}'"
    for k, v in result["mail"].items():
        assert re.fullmatch(r"[0-9]+", v), f"expected integer in field {k}, got '{v}'"
