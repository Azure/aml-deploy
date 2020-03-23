import os
import json

from azureml.core import Workspace, Model, ContainerRegistry
from azureml.core.compute import ComputeTarget, AksCompute
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AksWebservice, AciWebservice
from azureml.exceptions import ComputeTargetException, AuthenticationException, ProjectSystemException, WebserviceException
from azureml.core.authentication import ServicePrincipalAuthentication
from adal.adal_error import AdalError
from msrest.exceptions import AuthenticationError
from json import JSONDecodeError
from utils import AMLConfigurationException, required_parameters_provided, get_resource_config


def main():
    # Loading input values
    print("::debug::Loading input values")
    parameters_file = os.environ.get("INPUT_PARAMETERSFILE", default="compute.json")
    azure_credentials = os.environ.get("INPUT_AZURECREDENTIALS", default="{}")
    model_name = os.environ.get("INPUT_MODELNAME", default=None)
    model_version = int(os.environ.get("INPUT_MODELVERSION", default=None))
    try:
        azure_credentials = json.loads(azure_credentials)
    except JSONDecodeError:
        print("::error::Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS")
        raise AMLConfigurationException(f"Incorrect or poorly formed output from azure credentials saved in AZURE_CREDENTIALS secret. See setup in https://github.com/Azure/aml-compute/blob/master/README.md")

    # Checking provided parameters
    print("::debug::Checking provided parameters")
    required_parameters_provided(
        parameters=azure_credentials,
        keys=["tenantId", "clientId", "clientSecret"],
        message="Required parameter(s) not found in your azure credentials saved in AZURE_CREDENTIALS secret for logging in to the workspace. Please provide a value for the following key(s): "
    )

    # Loading parameters file
    print("::debug::Loading parameters file")
    parameters_file_path = os.path.join(".ml", ".azure", parameters_file)
    try:
        with open(parameters_file_path) as f:
            parameters = json.load(f)
    except FileNotFoundError:
        print(f"::error::Could not find parameter file in {parameters_file_path}. Please provide a parameter file in your repository (e.g. .ml/.azure/workspace.json).")
        raise AMLConfigurationException(f"Could not find parameter file in {parameters_file_path}. Please provide a parameter file in your repository (e.g. .ml/.azure/workspace.json).")

    # Loading Workspace
    print("::debug::Loading AML Workspace")
    sp_auth = ServicePrincipalAuthentication(
        tenant_id=azure_credentials.get("tenantId", ""),
        service_principal_id=azure_credentials.get("clientId", ""),
        service_principal_password=azure_credentials.get("clientSecret", "")
    )
    config_file_path = os.environ.get("GITHUB_WORKSPACE", default=".ml/.azure")
    config_file_name = "aml_arm_config.json"
    try:
        ws = Workspace.from_config(
            path=config_file_path,
            _file_name=config_file_name,
            auth=sp_auth
        )
    except AuthenticationException as exception:
        print(f"::error::Could not retrieve user token. Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS: {exception}")
        raise AuthenticationException
    except AuthenticationError as exception:
        print(f"::error::Microsoft REST Authentication Error: {exception}")
        raise AuthenticationError
    except AdalError as exception:
        print(f"::error::Active Directory Authentication Library Error: {exception}")
        raise AdalError
    except ProjectSystemException as exception:
        print(f"::error::Workspace authorizationfailed: {exception}")
        raise ProjectSystemException

    # Loading deployment target
    print("::debug::Loading deployment target")
    try:
        deployment_target = ComputeTarget(
            workspace=ws,
            name=parameters.get("deployment_target", "")
        )
    except ComputeTargetException:
        deployment_target = None
    
    # Loading model
    print("::debug::Loading model")
    try:
        model = Model(
            workspace=ws,
            name=model_name,
            version=model_version
        )
    except WebserviceException as exception:
        print(f"::error::Could not load model with provided details: {exception}")
        raise AMLConfigurationException(f"Could not load model with provided details: {exception}")
    
    # Creating inference config
    print("::debug::Creating inference config")
    if parameters.get("custom_container_registry_address", None) is not None:
        container_registry = ContainerRegistry()
        container_registry.address = os.environ.get("CONTAINERREGISTRYADRESS", None)
        container_registry.username = os.environ.get("CONTAINERREGISTRYUSERNAME", None)
        container_registry.password = os.environ.get("CONTAINERREGISTRYPASSWORD", None)
    else:
        container_registry = None

    inference_config = InferenceConfig(
        entry_script=parameters.get("inference_entry_script", None),
        runtime=parameters.get("runtime", None),
        conda_file=parameters.get("conda_file", None),
        extra_docker_file_steps=parameters.get("extra_docker_file_steps", None),
        source_directory=parameters.get("inference_source_directory", None),
        enable_gpu=parameters.get("enable_gpu", None),
        description=parameters.get("description", None),
        base_image=parameters.get("base_image", None),
        base_image_registry=container_registry,
        cuda_version=parameters.get("cuda_version", None)
    )

    # Loading run config
    print("::debug::Loading run config")
    model_resource_config = model.resource_configuration
    cpu_cores = get_resource_config(
        config=parameters.get("cpu_cores", None),
        resource_config=model_resource_config,
        config_name="cpu"
    )
    memory_gb = get_resource_config(
        config=parameters.get("memory_gb", None),
        resource_config=model_resource_config,
        config_name="memory_in_gb"
    )
    gpu_cores = get_resource_config(
        config=parameters.get("gpu_cores", None),
        resource_config=model_resource_config,
        config_name="gpu"
    )


    # Creating deployment config
    print("::debug::Creating deployment config")
    if type(deployment_target) is AksCompute:
        deployment_config = AksWebservice.deploy_configuration(
            autoscale_enabled="",
            autoscale_min_replicas="",
            autoscale_max_replicas="",
            autoscale_refresh_seconds="",
            autoscale_target_utilization="",
            collect_model_data=parameters.get("model_data_collection_enabled", None),
            auth_enabled=parameters.get("authentication_enabled", None),
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            enable_app_insights=parameters.get("app_insights_enabled", None),
            scoring_timeout_ms="",
            replica_max_concurrent_requests="",
            max_request_wait_time="",
            num_replicas="",
            primary_key=os.environ.get("PRIMARYKEY", None),
            secondary_key=os.environ.get("SECONDARYKEY", None),
            tags=parameters.get("tags", None),
            properties=parameters.get("properties", None),
            description=parameters.get("description", None),
            gpu_cores=gpu_cores,
            period_seconds="",
            initial_delay_seconds="",
            timeout_seconds="",
            success_threshold="",
            failure_threshold="",
            namespace="",
            token_auth_enabled=""
        )
    else:
        deployment_config = AciWebservice.deploy_configuration(
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            tags=parameters.get("tags", None),
            properties=parameters.get("properties", None),
            description=parameters.get("description", None),
            location=parameters.get("location", None),
            auth_enabled=parameters.get("authentication_enabled", None),
            ssl_enabled=parameters.get("ssl_enabled", None),
            enable_app_insights=parameters.get("app_insights_enabled", None),
            ssl_cert_pem_file=parameters.get("ssl_cert_pem_file", None),
            ssl_key_pem_file=parameters.get("ssl_key_pem_file", None),
            ssl_cname=parameters.get("ssl_cname", None),
            dns_name_label=parameters.get("dns_name_label", None),
            primary_key=os.environ.get("PRIMARYKEY", None),
            secondary_key=os.environ.get("SECONDARYKEY", None),
            collect_model_data=parameters.get("model_data_collection_enabled", None),
            cmk_vault_base_url=parameters.get("cmk_vault_base_url", None),
            cmk_key_name=parameters.get("cmk_key_name", None),
            cmk_key_version=parameters.get("cmk_key_version", None)
        )

    try:
        service = Model.deploy(
            workspace=ws,
            name=parameters.get("name", None),
            models=[],
            inference_config=inference_config,
            deployment_config=deployment_config,
            deployment_target=deployment_target,
            overwrite=True
        )
    except expression as identifier:
        pass
    print("::debug::Successfully finished Azure Machine Learning Deploy Action")


if __name__ == "__main__":
    main()
