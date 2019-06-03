import os
import argparse
import re
import sys
import logging

import boto3
from ruamel.yaml import YAML

from template_substitutor import TemplateSubstitutor

if __name__ == "__main__":

    logging.basicConfig(
        format="%(level_name}s: %(message)s", level=os.getenv("LOG_LEVEL", "ERROR")
    )
    log = logging.getLogger()
    parser = argparse.ArgumentParser(description="search DeepSecurity types.")
    parser.add_argument(
        "--url",
        default="https://app.deepsecurity.trendmicro.com/api",
        help="of the DeepSecurity API",
    )
    parser.add_argument("--api-version", default="v1", help="of the DeepSecurity API")
    parser.add_argument("--api-key", help="to use when calling the DeepSecurity API")
    parser.add_argument(
        "--api-key-parameter-name",
        default="/cfn-deep-security-provider/api_key",
        help="in the parameter store",
    )
    parser.add_argument("--max-items", default=10, type=int, help="to return")
    parser.add_argument(
        "--type", required=True, help="to search for, eg policy, firewallRule, .."
    )
    parser.add_argument(
        "--query", help="to execute, only supported format: field == value"
    )

    args = parser.parse_args()
    if not args.api_key:
        try:
            ssm = boto3.client("ssm")
            args.api_key = ssm.get_parameter(
                Name=args.api_key_parameter_name, WithDecryption=True
            )["Parameter"]["Value"]
        except Exception as e:
            parser.error(
                f"failed to retrieve api key from parameter store {args.api_key_parameter_name}, {e}"
            )

    main = TemplateSubstitutor(
        api_endpoint=args.url, api_key=args.api_key, api_version=args.api_version
    )

    search = {"maxItems": args.max_items}
    if args.query:
        match = re.fullmatch(
            r"\s*(?P<fieldname>[^\s=]*)\s*(?P<operator>==)\s*\"(?P<value>[^\"]*)\"",
            args.query,
        )
        if not match:
            parser.error(f"unsupported query syntax '{args.query}'")

        query = match.groupdict()
        if query["operator"] != "==":
            parser.error(f"expected operator ==, found '{query['operator']}'")
        if not query["fieldname"]:
            parser.error("no fieldname found, {}".format(query["fieldname"]))
        search["searchCriteria"] = {
            "fieldName": query["fieldname"],
            "stringValue": query["value"],
        }

    log.debug(f"{search} for {main.search_url(args.type)}\n")

    results, err = main.search(args.type, search)
    if err:
        sys.stderr.write(f"ERROR: {err}")
        sys.exit(1)

    yaml = YAML()
    yaml.dump(results, sys.stdout)
