import jsonschema
from azureml.core import Dataset


class AMLConfigurationException(Exception):
    pass


class AMLDeploymentException(Exception):
    pass


def validate_json(data, schema, input_name):
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    if len(errors) > 0:
        for error in errors:
            print(f"::error::JSON validation error: {error}")
        raise AMLConfigurationException(f"JSON validation error for '{input_name}'. Provided object does not match schema. Please check the output for more details.")
    else:
        print(f"::debug::JSON validation passed for '{input_name}'. Provided object does match schema.")


def get_resource_config(config, resource_config, config_name):
    if config is not None:
        return config
    elif resource_config is not None:
        return resource_config.serialize().get(config_name, None)
    return None


def mask_parameter(parameter):
    print(f"::add-mask::{parameter}")


def get_dataset(workspace, name):
    try:
        dataset = Dataset.get_by_name(
            workspace=workspace,
            name=name,
            version="latest"
        )
    except Exception:
        dataset = None
    return dataset
