import pytest
import uuid
import boto3
import logging
from deep_security_provider import handler, request_schema

logging.basicConfig(level=logging.INFO)

def test_dummy():
        response = handler({}, {})
        assert False, "not implemented"
