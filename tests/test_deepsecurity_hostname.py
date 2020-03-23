from datadog_event_forwarder import hostname_tags
from collections import OrderedDict


def test_full_match():
    ds_name = "ec2-3-123-36-92.eu-central-1.compute.amazonaws.com (ebms.prod-api) [i-0187d96402df8c28d]"
    h, tags = hostname_tags(ds_name)
    assert h == 'i-0187d96402df8c28d'
    assert tags == ["name:ebms.prod-api"]


def test_half_match():
    ds_name = "10.0.5.82 () [i-0dc90ac2a869a8c8e]"
    h, tags = hostname_tags(ds_name)
    assert h == "i-0dc90ac2a869a8c8e"
    assert tags == []


def test_empty_match():
    ds_name = "10.0.5.82 () []"
    h, tags = hostname_tags(ds_name)
    h == ds_name
    assert tags == []


def test_no_match():
    ds_name = "app.deepsecurity.com"
    h, tags = hostname_tags(ds_name)
    h == ds_name
    assert tags == []
