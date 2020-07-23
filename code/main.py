import os
import sys
import json
import importlib

from azureml.contrib.functions import package_http, package_blob, package_service_bus_queue
from azureml.core import Workspace, Model, ContainerRegistry
from azureml.core.compute import ComputeTarget, AksCompute
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AksWebservice, AciWebservice
from azureml.exceptions import ComputeTargetException, AuthenticationException, ProjectSystemException, WebserviceException
from azureml.core.authentication import ServicePrincipalAuthentication
from adal.adal_error import AdalError
from msrest.exceptions import AuthenticationError
from json import JSONDecodeError
from utils import AMLConfigurationException, AMLDeploymentException, get_resource_config, mask_parameter, validate_json, get_dataset
from schemas import azure_credentials_schema, parameters_schema


def main():
    # Loading input values
    print("::debug::Loading input values")
    model_name = os.environ.get("INPUT_MODEL_NAME", default=None)
    model_version = os.environ.get("INPUT_MODEL_VERSION", default=None)

    # Casting input values
    print("::debug::Casting input values")
    try:
        model_version = int(model_version)
    except TypeError as exception:
        print(f"::debug::Could not cast model version to int: {exception}")
        model_version = None
    except ValueError as exception:
        print(f"::debug::Could not cast model version to int: {exception}")
        model_version = None

    # Loading azure credentials
    print("::debug::Loading azure credentials")
    azure_credentials = os.environ.get("INPUT_AZURE_CREDENTIALS", default="{}")
    try:
        azure_credentials = json.loads(azure_credentials)
    except JSONDecodeError:
        print("::error::Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS")
        raise AMLConfigurationException("Incorrect or poorly formed output from azure credentials saved in AZURE_CREDENTIALS secret. See setup in https://github.com/Azure/aml-compute/blob/master/README.md")

    # Checking provided parameters
    print("::debug::Checking provided parameters")
    validate_json(
        data=azure_credentials,
        schema=azure_credentials_schema,
        input_name="AZURE_CREDENTIALS"
    )

    # Mask values
    print("::debug::Masking parameters")
    mask_parameter(parameter=azure_credentials.get("tenantId", ""))
    mask_parameter(parameter=azure_credentials.get("clientId", ""))
    mask_parameter(parameter=azure_credentials.get("clientSecret", ""))
    mask_parameter(parameter=azure_credentials.get("subscriptionId", ""))

    # Loading parameters file
    print("::debug::Loading parameters file")
    parameters_file = os.environ.get("INPUT_PARAMETERS_FILE", default="deploy.json")
    parameters_file_path = os.path.join(".cloud", ".azure", parameters_file)
    try:
        with open(parameters_file_path) as f:
            parameters = json.load(f)
    except FileNotFoundError:
        print(f"::debug::Could not find parameter file in {parameters_file_path}. Please provide a parameter file in your repository  if you do not want to use default settings (e.g. .cloud/.azure/deploy.json).")
        parameters = {}

    # Checking provided parameters
    print("::debug::Checking provided parameters")
    validate_json(
        data=parameters,
        schema=parameters_schema,
        input_name="PARAMETERS_FILE"
    )

    # Define target cloud
    if azure_credentials.get("resourceManagerEndpointUrl", "").startswith("https://management.usgovcloudapi.net"):
        cloud = "AzureUSGovernment"
    elif azure_credentials.get("resourceManagerEndpointUrl", "").startswith("https://management.chinacloudapi.cn"):
        cloud = "AzureChinaCloud"
    else:
        cloud = "AzureCloud"

    # Loading Workspace
    print("::debug::Loading AML Workspace")
    sp_auth = ServicePrincipalAuthentication(
        tenant_id=azure_credentials.get("tenantId", ""),
        service_principal_id=azure_credentials.get("clientId", ""),
        service_principal_password=azure_credentials.get("clientSecret", ""),
        cloud=cloud
    )
    config_file_path = os.environ.get("GITHUB_WORKSPACE", default=".cloud/.azure")
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
    if os.environ.get("CONTAINER_REGISTRY_ADRESS", None) is not None:
        container_registry = ContainerRegistry()
        container_registry.address = os.environ.get("CONTAINER_REGISTRY_ADRESS", None)
        container_registry.username = os.environ.get("CONTAINER_REGISTRY_USERNAME", None)
        container_registry.password = os.environ.get("CONTAINER_REGISTRY_PASSWORD", None)
    else:
        container_registry = None

    try:
        inference_config = InferenceConfig(
            entry_script=parameters.get("inference_entry_script", "score.py"),
            runtime=parameters.get("runtime", "python"),
            conda_file=parameters.get("conda_file", "environment.yml"),
            extra_docker_file_steps=parameters.get("extra_docker_file_steps", None),
            source_directory=parameters.get("inference_source_directory", "code/deploy/"),
            enable_gpu=parameters.get("enable_gpu", None),
            description=parameters.get("description", None),
            base_image=parameters.get("custom_base_image", None),
            base_image_registry=container_registry,
            cuda_version=parameters.get("cuda_version", None)
        )
    except WebserviceException as exception:
        print(f"::debug::Failed to create InferenceConfig. Trying to create no code deployment: {exception}")
        inference_config = None
    except TypeError as exception:
        print(f"::debug::Failed to create InferenceConfig. Trying to create no code deployment: {exception}")
        inference_config = None

    # Skip deployment if only Docker image should be created
    if not parameters.get("skip_deployment", False):
        # Default service name
        repository_name = os.environ.get("GITHUB_REPOSITORY").split("/")[-1]
        branch_name = os.environ.get("GITHUB_REF").split("/")[-1]
        default_service_name = f"{repository_name}-{branch_name}".lower().replace("_", "-")
        service_name = parameters.get("name", default_service_name)[:32]

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

        # Profiling model
        print("::debug::Profiling model")
        if parameters.get("profiling_enabled", False):
            # Getting profiling dataset
            profiling_dataset = get_dataset(
                workspace=ws,
                name=parameters.get("profiling_dataset", None)
            )
            if profiling_dataset is None:
                profiling_dataset = model.sample_input_dataset

            # Profiling model
            try:
                model_profile = Model.profile(
                    workspace=ws,
                    profile_name=f"{service_name}-profile"[:32],
                    models=[model],
                    inference_config=inference_config,
                    input_dataset=profiling_dataset
                )
                model_profile.wait_for_completion(show_output=True)

                # Overwriting resource configuration
                cpu_cores = model_profile.recommended_cpu
                memory_gb = model_profile.recommended_memory

                # Setting output
                profiling_details = model_profile.get_details()
                print(f"::set-output name=profiling_details::{profiling_details}")
            except Exception as exception:
                print(f"::warning::Failed to profile model. Skipping profiling and moving on to deployment: {exception}")

        # Loading deployment target
        print("::debug::Loading deployment target")
        try:
            deployment_target = ComputeTarget(
                workspace=ws,
                name=parameters.get("deployment_compute_target", "")
            )
        except ComputeTargetException:
            deployment_target = None
        except TypeError:
            deployment_target = None

        # Creating deployment config
        print("::debug::Creating deployment config")
        if type(deployment_target) is AksCompute:
            deployment_config = AksWebservice.deploy_configuration(
                autoscale_enabled=parameters.get("autoscale_enabled", None),
                autoscale_min_replicas=parameters.get("autoscale_min_replicas", None),
                autoscale_max_replicas=parameters.get("autoscale_max_replicas", None),
                autoscale_refresh_seconds=parameters.get("autoscale_refresh_seconds", None),
                autoscale_target_utilization=parameters.get("autoscale_target_utilization", None),
                collect_model_data=parameters.get("model_data_collection_enabled", None),
                auth_enabled=parameters.get("authentication_enabled", None),
                cpu_cores=cpu_cores,
                memory_gb=memory_gb,
                enable_app_insights=parameters.get("app_insights_enabled", None),
                scoring_timeout_ms=parameters.get("scoring_timeout_ms", None),
                replica_max_concurrent_requests=parameters.get("replica_max_concurrent_requests", None),
                max_request_wait_time=parameters.get("max_request_wait_time", None),
                num_replicas=parameters.get("num_replicas", None),
                primary_key=os.environ.get("PRIMARY_KEY", None),
                secondary_key=os.environ.get("SECONDARY_KEY", None),
                tags=parameters.get("tags", None),
                properties=parameters.get("properties", None),
                description=parameters.get("description", None),
                gpu_cores=gpu_cores,
                period_seconds=parameters.get("period_seconds", None),
                initial_delay_seconds=parameters.get("initial_delay_seconds", None),
                timeout_seconds=parameters.get("timeout_seconds", None),
                success_threshold=parameters.get("success_threshold", None),
                failure_threshold=parameters.get("failure_threshold", None),
                namespace=parameters.get("namespace", None),
                token_auth_enabled=parameters.get("token_auth_enabled", None)
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
                primary_key=os.environ.get("PRIMARY_KEY", None),
                secondary_key=os.environ.get("SECONDARY_KEY", None),
                collect_model_data=parameters.get("model_data_collection_enabled", None),
                cmk_vault_base_url=os.environ.get("CMK_VAULT_BASE_URL", None),
                cmk_key_name=os.environ.get("CMK_KEY_NAME", None),
                cmk_key_version=os.environ.get("CMK_KEY_VERSION", None)
            )

        # Deploying model
        print("::debug::Deploying model")
        try:
            service = Model.deploy(
                workspace=ws,
                name=service_name,
                models=[model],
                inference_config=inference_config,
                deployment_config=deployment_config,
                deployment_target=deployment_target,
                overwrite=True
            )
            service.wait_for_deployment(show_output=True)
        except WebserviceException as exception:
            print(f"::error::Model deployment failed with exception: {exception}")
            service_logs = service.get_logs()
            raise AMLDeploymentException(f"Model deployment failed logs: {service_logs} \nexception: {exception}")

        # Checking status of service
        print("::debug::Checking status of service")
        if service.state != "Healthy":
            service_logs = service.get_logs()
            print(f"::error::Model deployment failed with state '{service.state}': {service_logs}")
            raise AMLDeploymentException(f"Model deployment failed with state '{service.state}': {service_logs}")

        if parameters.get("test_enabled", False):
            # Testing service
            print("::debug::Testing service")
            root = os.environ.get("GITHUB_WORKSPACE", default=None)
            test_file_path = parameters.get("test_file_path", "code/test/test.py")
            test_file_function_name = parameters.get("test_file_function_name", "main")

            print("::debug::Adding root to system path")
            sys.path.insert(1, f"{root}")

            print("::debug::Importing module")
            test_file_path = f"{test_file_path}.py" if not test_file_path.endswith(".py") else test_file_path
            try:
                test_spec = importlib.util.spec_from_file_location(
                    name="testmodule",
                    location=test_file_path
                )
                test_module = importlib.util.module_from_spec(spec=test_spec)
                test_spec.loader.exec_module(test_module)
                test_function = getattr(test_module, test_file_function_name, None)
            except ModuleNotFoundError as exception:
                print(f"::error::Could not load python script in your repository which defines theweb service tests (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")
                raise AMLConfigurationException(f"Could not load python script in your repository which defines the web service tests (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")
            except FileNotFoundError as exception:
                print(f"::error::Could not load python script or function in your repository which defines the web service tests (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")
                raise AMLConfigurationException(f"Could not load python script or function in your repository which defines the web service tests (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")
            except AttributeError as exception:
                print(f"::error::Could not load python script or function in your repository which defines the web service tests (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")
                raise AMLConfigurationException(f"Could not load python script or function in your repository which defines the web service tests (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")

            # Load experiment config
            print("::debug::Loading experiment config")
            try:
                test_function(service)
            except TypeError as exception:
                print(f"::error::Could not load experiment config from your module (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")
                raise AMLConfigurationException(f"Could not load experiment config from your module (Script: /{test_file_path}, Function: {test_file_function_name}()): {exception}")
            except Exception as exception:
                print(f"::error::The webservice tests did not complete successfully: {exception}")
                raise AMLDeploymentException(f"The webservice tests did not complete successfully: {exception}")

        # Deleting service if desired
        if parameters.get("delete_service_after_deployment", False):
            service.delete()
        else:
            # Creating outputs
            print("::debug::Creating outputs")
            print(f"::set-output name=service_scoring_uri::{service.scoring_uri}")
            print(f"::set-output name=service_swagger_uri::{service.swagger_uri}")

    # Creating Docker image
    if parameters.get("create_image", None) is not None:
        try:
            # Packaging model
            if parameters.get("create_image", None) == "docker":
                package = Model.package(
                    workspace=ws,
                    models=[model],
                    inference_config=inference_config,
                    generate_dockerfile=False
                )
            if parameters.get("create_image", None) == "function_blob":
                package = package_blob(
                    workspace=ws,
                    models=[model],
                    inference_config=inference_config,
                    generate_dockerfile=False,
                    input_path=os.environ.get("FUNCTION_BLOB_INPUT"),
                    output_path=os.environ.get("FUNCTION_BLOB_OUTPUT")
                )
            if parameters.get("create_image", None) == "function_http":
                package = package_http(
                    workspace=ws,
                    models=[model],
                    inference_config=inference_config,
                    generate_dockerfile=False,
                    auth_level=os.environ.get("FUNCTION_HTTP_AUTH_LEVEL")
                )
            if parameters.get("create_image", None) == "function_service_bus_queue":
                package = package_service_bus_queue(
                    workspace=ws,
                    models=[model],
                    inference_config=inference_config,
                    generate_dockerfile=False,
                    input_queue_name=os.environ.get("FUNCTION_SERVICE_BUS_QUEUE_INPUT"),
                    output_queue_name=os.environ.get("FUNCTION_SERVICE_BUS_QUEUE_OUTPUT")
                )

            # Getting container registry details
            acr = package.get_container_registry()
            mask_parameter(parameter=acr.address)
            mask_parameter(parameter=acr.username)
            mask_parameter(parameter=acr.password)

            # Wait for completion and pull image
            package.wait_for_creation(show_output=True)

            # Creating additional outputs
            print("::debug::Creating outputs")
            print(f"::set-output name=acr_address::{acr.address}")
            print(f"::set-output name=acr_username::{acr.username}")
            print(f"::set-output name=acr_password::{acr.password}")
            print(f"::set-output name=package_location::{package.location}")
        except WebserviceException as exception:
            print(f"::error::Image creation failed with exception: {exception}")
            package_logs = package.get_logs()
            raise AMLDeploymentException(f"Image creation failed with logs: {package_logs}")
    print("::debug::Successfully finished Azure Machine Learning Deploy Action")


if __name__ == "__main__":
    main()
