import re
from io import StringIO
import requests
from typing import List


class TemplateSubstitutor(object):
    """
    substitutes all references to {{ lookup "<typename>" "<name>" }} with the ID of the object in
    Deep Security. The type name is case sensitive, and an exact match is required.

    For example: {{ lookup "firewallRule" "" }}

    """

    def __init__(self, api_endpoint, api_key, api_version):
        super(TemplateSubstitutor, self).__init__()
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.pattern = re.compile(
            r'{{\s*(lookup)\s+"(?P<type>[^"]*)"\s+"(?P<name>[^"]*)"\s*}}', re.MULTILINE
        )

    def plural(self, name):
        if name[-1] == "y":
            return f"{name[0:-1]}ies"
        else:
            return f"{name}s"

    def _do_lookup(self, type, name):
        search = {
            "maxItems": 2,
            "searchCriteria": [{"fieldName": "name", "stringValue": name}],
        }
        headers = {"api-version": self.api_version, "api-secret-key": self.api_key}
        try:
            key_name = self.plural(type)
            url = f"{self.api_endpoint}/{self.plural(type).lower()}/search"
            response = requests.post(url, headers=headers, json=search)

            if response.status_code != 200:
                return (
                    None,
                    f"no type '{type}' found with the name '{name}'\n{response.status_code} - {response.text}",
                )

            results = response.json()
            if key_name not in results:
                return (
                    None,
                    f"no field '{key_name}' expected in response, but it is missing.",
                )

            if not results[key_name] or len(results[key_name]) > 1:
                return (
                    None,
                    f"expected single {type} with name {name}, found {len(results[key_name])}",
                )

            if "ID" not in results[key_name][0]:
                return None, f"no field ID in in search result {key_name}"

            return results[key_name][0]["ID"], None
        except IOError as e:
            return None, f"search for {type} with name {name} failed, {e}"

    def replace_references(self, value) -> (object, List[str]):
        if isinstance(value, str):
            errors = []
            matches: List[re.MatchObject] = [m for m in self.pattern.finditer(value)]
            if matches:
                result = StringIO()
                previous = 0
                for m in matches:
                    new_value, err = self._do_lookup(**m.groupdict())
                    if not err:
                        result.write(value[previous : m.start()])
                        result.write(f"{new_value}")
                    else:
                        result.write(value[previous : m.end()])
                        errors.append(err)
                    previous = m.end()
                result.write(value[previous:])
                return result.getvalue(), errors
            else:
                return value, []
        else:
            return value, []

    def replace_lookups(self, obj: object) -> (object, List[str]):
        errors = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_value, err = self.replace_lookups(value)
                if not err:
                    obj[key] = new_value
                else:
                    errors.extend(err)
            return obj, errors
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                new_value, err = self.replace_lookups(value)
                if not err:
                    obj[i] = new_value
                else:
                    errors.extend(err)
            return obj, errors
        else:
            return self.replace_references(obj)
