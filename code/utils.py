class AMLConfigurationException(Exception):
    pass


def required_parameters_provided(parameters, keys, message="Required parameter(s) not found in your parameters file. Please provide a value for the following key(s): "):
    missing_keys = []
    for key in keys:
        if key not in parameters:
            err_msg = f"{message} {key}"
            print(f"::error::{err_msg}")
            missing_keys.append(key)
    if len(missing_keys) > 0:
        raise AMLConfigurationException(f"{message} {missing_keys}")


def get_resource_config(config, resource_config, config_name):
    if config is not None:
        return config
    elif resource_config is not None:
        return resource_config.serialize().get(config_name, None)
    return None
