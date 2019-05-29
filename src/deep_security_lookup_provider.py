import os
import logging
import requests
from deep_security_provider import DeepSecurityProvider
import copy


log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


request_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "required": ["Type"],
    "properties": {
        "Connection": {
            "type": "object",
            "properties": {
                "URL": {
                    "type": "string",
                    "default": "https://app.deepsecurity.trendmicro.com/api",
                    "description": "endpoint of the deep security API",
                },
                "Version": {
                    "type": "string",
                    "default": "v1",
                    "description": "of the api to use",
                },
                "ApiKeyParameterName": {
                    "type": "string",
                    "default": "/cfn-deep-security-provider/api_key",
                    "description": "Name of the parameter in the Parameter Store for the API key",
                },
            },
        },
        "Type": {
            "type": "string",
            "description": "to lookup",
            "enum": [
                "macList",
                "firewallRule",
                "context",
                "statefulConfiguration",
                "ipList",
                "interfaceType",
                "portList",
                "schedule",
                "policy",
            ],
        },
        "Search": {
            "type": "object",
            "description": "as defined by deep security /search api for this type",
        },
        "Name": {
            "type": "string",
            "description": "of resource to lookup (eg shorthand searchCriterium)",
        },
    },
}


class DeepSecurityLookupProvider(DeepSecurityProvider):
    def __init__(self):
        super(DeepSecurityLookupProvider, self).__init__()

    def is_supported_resource_type(self):
        return self.resource_type == "Custom::DeepSecurityLookup"

    def is_valid_cfn_request(self):
        if not super(DeepSecurityLookupProvider, self).is_valid_cfn_request():
            return False

        if not self.get("Name") and not self.get("Search"):
            self.fail("either 'Name' or 'Search or both must be present")
            return False

        return True

    @property
    def search_type(self):
        return self.get("Type")

    @property
    def search_type_plural(self):
        if self.search_type[-1] == "y":
            return f"{self.search_type[0:-1]}ies"
        else:
            return f"{self.search_type}s"

    @property
    def resource_url(self):
        return f"{self.api_endpoint}/{self.search_type_plural.lower()}/search"

    @property
    def search_criteria(self):
        result = copy.deepcopy(self.get("Search", {}))
        if self.get("Name"):
            if "searchCriteria" not in result:
                result["searchCriteria"] = []
            result["searchCriteria"].append(
                {"fieldName": "name", "stringValue": self.get("Name")}
            )
        return result

    def search(self):
        self.add_api_key()
        try:
            response = requests.post(
                self.resource_url, headers=self.headers, json=self.search_criteria
            )
            if response.status_code in (200, 201):
                results = response.json()
                if self.search_type_plural in results:
                    ids = list(
                        map(
                            lambda r: r["ID"],
                            filter(
                                lambda r: "ID" in r, results[self.search_type_plural]
                            ),
                        )
                    )
                    if not ids or len(ids) > 1:
                        self.fail(f"expected precisely 1 result, got {len(ids)}")
                    else:
                        self.physical_resource_id = str(ids[0])
                else:
                    self.fail(
                        f"no {self.search_type_plural} found in search result, did find {results.keys()}"
                    )
            else:
                self.fail(f"Search for {self.search_type} failed, {response.text}")
        except IOError as e:
            self.fail(f"Search for {self.search_type} failed, {e}")

    def create(self):
        self.search()
        if self.status == "FAILED":
            self.physical_resource_id = "search-failed"

    def update(self):
        self.search()

    def delete(self):
        pass


provider = DeepSecurityLookupProvider()


def handler(request, context):
    return provider.handle(request, context)
