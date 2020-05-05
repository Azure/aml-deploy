import os
import sys
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, "..", "code"))

from utils import validate_json, AMLConfigurationException
from schemas import azure_credentials_schema


def test_validate_json_valid_inputs():
    """
    Unit test to check the validate_json function with valid inputs
    """
    json_object = {
        "clientId": "",
        "clientSecret": "",
        "subscriptionId": "",
        "tenantId": ""
    }
    schema_object = azure_credentials_schema
    validate_json(
        data=json_object,
        schema=schema_object,
        input_name="PARAMETERS_FILE"
    )


def test_validate_json_invalid_json():
    """
    Unit test to check the validate_json function with invalid json_object inputs
    """
    json_object = {
        "clientId": "",
        "clientSecret": "",
        "subscriptionId": ""
    }
    schema_object = azure_credentials_schema
    with pytest.raises(AMLConfigurationException):
        assert validate_json(
            data=json_object,
            schema=schema_object,
            input_name="PARAMETERS_FILE"
        )


def test_validate_json_invalid_schema():
    """
    Unit test to check the validate_json function with invalid schema inputs
    """
    json_object = {}
    schema_object = {}
    with pytest.raises(Exception):
        assert validate_json(
            data=json_object,
            schema=schema_object,
            input_name="PARAMETERS_FILE"
        )
