from datadog_event_forwarder import hostname_tags, dict_to_datadog_tags
from collections import OrderedDict


def test_full_match():
    ds_name = "10.0.5.82 (ecs-instance.dev-api) [i-0dc90ac2a869a8c8e]"
    h, tags = hostname_tags(ds_name)
    assert tags == ["name:ecs-instance.dev-api", f"dsname:{ds_name}"]


def test_half_match():
    ds_name = "10.0.5.82 () [i-0dc90ac2a869a8c8e]"
    h, tags = hostname_tags(ds_name)
    assert h == "i-0dc90ac2a869a8c8e"
    assert tags == [f"dsname:{ds_name}"]


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
