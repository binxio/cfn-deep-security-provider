import json
import logging
import os
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import List
from urllib.parse import parse_qs, urlparse
from io import StringIO

import boto3
import datadog
from botocore.exceptions import ClientError
from ruamel.yaml import YAML

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger()


def tags(tags: str = os.environ.get("DATADOG_TAGS", "")) -> List[str]:
    """
    converts environment variable TAGS in the format tag=value,tag=value,tag=value to
    [ "tag:value", "tag:value", "tag:value" ]
    """
    if not tags:
        return []

    return list(
        map(
            lambda tag: f"{tag[0]}:{tag[1] if len(tag) > 1 else ''}",
            map(lambda tag: tag.strip().split("=", 1), tags.split(",")),
        )
    )


def date_happened(message: dict) -> int:
    if "LogDate" in message:
        return int(
            datetime.fromisoformat(
                message.get("LogDate").replace("Z", "+00:00")
            ).timestamp()
        )
    else:
        return int(datetime.now().timestamp())


def ossec_level_to_log_level(message: dict) -> str:
    """
    converts OSSEC_Level to log level
    OSSEC level. An integer in the range 0 to 15 inclusive. 0-3=Low severity, 4-7=Medium severity, 8-11=High severity, 12-15=Critical severity.
    """
    level = message.get("OSSEC_Level", 0)
    if level >= 8:
        return "error"
    elif level >= 4:
        return "warning"
    else:
        return "info"


def log_level(message: dict) -> str:
    """
    converts DeepSecurity to Datadog log level info, warning or error.

    SystemEvent.Severity	1=Info, 2=Warning, 3=Error
    Integrity monitoring events, intrusion prevention events Severity	1=Low, 2=Medium, 3=High, 4=Critical
    """
    if "Severity" in message:
        severity_to_log_level = {1: "info", 2: "warning", 3: "error", 4: "error"}
        return severity_to_log_level[(message.get("Severity", 1))]
    elif "OSSEC_Level" in message:
        return ossec_level_to_log_level(message)
    else:
        log.error(
            "received an DeepSecurity Event of type %s without Severity or OSSEC_Level attribute",
            message.get("EventType"),
        )
        return "info"


def message_to_text(message: dict) -> str:
    yaml = YAML()
    result = StringIO()
    if message.get("Description"):
        result.write(message.get("Description"))
        result.write("\n")
    yaml.dump(message, result)
    return result.getvalue()


def message_to_title(message_id, message: dict) -> str:
    event_type = message.get("EventType", "Unknown")
    title = message.get("Title", "message id " + message_id)
    return f"{event_type} : {title}"


def send_datadog_event(message_id: str, message: dict):
    log.debug("forwarding event %s to datadog", message_id)
    yaml = YAML()
    response = datadog.api.Event.create(
        priority="normal",
        alert_type=log_level(message),
        title=message_to_title(message_id, message),
        text=message_to_text(message),
        date_happened=date_happened(message),
        tags=tags(),
        host=message.get("Hostname", "app.deepsecurity.trendmicro.com"),
        source_type_name="DeepSecurity",
    )

    if response["status"] != "ok":
        log.error("Failed to forward event to datadog: %s", response)


def load_ssm_parameters(env: dict):
    ssm = boto3.client("ssm")
    for name, url in map(
        lambda n: (n, urlparse(env[n], scheme="ssm")),
        filter(lambda n: env[n].startswith("ssm:"), env.keys()),
    ):
        if url.path:
            parameters = parse_qs(url.query)
            try:
                response = ssm.get_parameter(Name=url.path, WithDecryption=True)
                env[name] = response["Parameter"]["Value"]
                log.debug(
                    "replacing environment variable %s with value from ssm://%s",
                    name,
                    url.path,
                )
            except ClientError as e:
                if parameters.get("default"):
                    env[name] = parameters.get("default")[0]
                    log.warning(
                        "default set for environment variable %s with value from %s, %s",
                        name,
                        url.path,
                        e,
                    )
                else:
                    log.error(
                        "environment variable %s with value from ssm://%s, could not be retrieved, %s",
                        name,
                        url.path,
                        e,
                    )
        else:
            log.error(
                "environment variable %s with value from %s, does not specify a parameter name",
                name,
                env[name],
            )


def connect_to_datadog():
    if not datadog.api._api_host:
        load_ssm_parameters(os.environ)
        datadog.initialize(host_name="app.deepsecurity.trendmicro.com")


def handler(event, context):
    connect_to_datadog()

    for sns in map(
        lambda r: r["Sns"], filter(lambda r: "Sns" in r, event.get("Records", []))
    ):
        try:
            message_id = sns.get("MessageId")
            event = json.loads(sns.get("Message"))
            if event and isinstance(event, list):
                send_datadog_event(message_id, event[0])
            else:
                log.error(
                    "message %s expected array as message got a %s",
                    message_id,
                    type(event),
                )
        except JSONDecodeError as e:
            log.error(
                "message %s received does not contain a json  message, %s",
                message_id,
                e,
            )
