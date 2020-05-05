import os
import sys
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, "..", "code"))

from main import main
from utils import AMLConfigurationException


def test_main_no_input():
    """
    Unit test to check the main function with no inputs
    """
    with pytest.raises(AMLConfigurationException):
        assert main()


def test_main_invalid_azure_credentials():
    os.environ["INPUT_AZURE_CREDENTIALS"] = ""
    with pytest.raises(AMLConfigurationException):
        assert main()


def test_main_invalid_parameters_file():
    os.environ["INPUT_AZURE_CREDENTIALS"] = """{
        'clientId': 'test',
        'clientSecret': 'test',
        'subscriptionId': 'test',
        'tenantId': 'test'
    }"""
    os.environ["INPUT_PARAMETERS_FILE"] = "wrongfile.json"
    with pytest.raises(AMLConfigurationException):
        assert main()
