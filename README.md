![Integration Test](https://github.com/Azure/aml-deploy/workflows/Integration%20Test/badge.svg)
![Lint](https://github.com/Azure/aml-deploy/workflows/Lint/badge.svg)

# Azure Machine Learning Deploy Action

The Azure Machine Learning Register Model action will register your model on AML for use in deployment and testing. This action is designed to only register the model that corresponds to the run reporting the highest metrics. This can be overruled by passing the `force_registration` as true. You will need to have azure credentials that allow you to connect to a workspace, view experiment or pipeline runs and register a model.

This action requires an AML workspace to be created or attached to via the [aml-workspace](https://github.com/Azure/aml-workspace) action as well as a model to be registered with the [aml-registermodel](https://github.com/Azure/aml-registermodel) action.

This action is one in a series of actions that are used to make ML Ops systems. Examples of these can be found at [ml-template-azure](https://github.com/machine-learning-apps/ml-template-azure) and [aml-template](https://github.com/Azure/aml-template).

## Usage

Description

### Example workflow

```yaml
name: My Workflow
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
    - name: Check Out Repository
      id: checkout_repository
      uses: actions/checkout@v2

    # AML Workspace Action
    - uses: Azure/aml-workspace
      id: aml_workspace
      with:
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}

    # AML Register Model Action
    - uses: Azure/deploy
      id: aml_deploy
      with:
        # required inputs as secrets
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
        # optional
        parameters_file: "registermodel.json"
```

### Inputs

| Input | Required | Default | Description |
| ----- | -------- | ------- | ----------- |
| azure_credentials | x | - | Output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth`. This should be stored in your secrets |
| parameters_file |  | `"registermodel.json"` | JSON file in the `.ml/.azure` folder specifying your Azure Machine Learning model registration details. |

#### Azure Credentials

Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) and execute the following command to generate the credentials:

```sh
# Replace {service-principal-name}, {subscription-id} and {resource-group} with your Azure subscription id and resource group and any name
az ad sp create-for-rbac --name {service-principal-name} \
                         --role contributor \
                         --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
                         --sdk-auth
```

This will generate the following JSON output:

```sh
{
  "clientId": "<GUID>",
  "clientSecret": "<GUID>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>",
  (...)
}
```

Add the JSON output as [a secret](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets#creating-encrypted-secrets) with the name `AZURE_CREDENTIALS` in the GitHub repository.

#### Parameters File

The action expects a JSON file in the `.ml/.azure` folder in your repository, which specifies details for the model registration to your Azure Machine Learning Workspace. By default, the action expects a file with the name `registermodel.json`. If your JSON file has a different name, you can specify it with this parameter.

A sample file can be found in this repository in the folder `.ml/.azure`. There are separate parameters that are used for the ACI deployment, the AKS deployment and some that are for both deployments.

Documentation for the paramets can be found at the following links:
[inference](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.model.inferenceconfig?view=azure-ml-py)
[model](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.model(class)?view=azure-ml-py#deploy-workspace--name--models--inference-config-none--deployment-config-none--deployment-target-none--overwrite-false-)
[ACI](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aciwebservice?view=azure-ml-py#deploy-configuration-cpu-cores-none--memory-gb-none--tags-none--properties-none--description-none--location-none--auth-enabled-none--ssl-enabled-none--enable-app-insights-none--ssl-cert-pem-file-none--ssl-key-pem-file-none--ssl-cname-none--dns-name-label-none--primary-key-none--secondary-key-none--collect-model-data-none--cmk-vault-base-url-none--cmk-key-name-none--cmk-key-version-none-)
[AKS](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.akswebservice?view=azure-ml-py#deploy-configuration-autoscale-enabled-none--autoscale-min-replicas-none--autoscale-max-replicas-none--autoscale-refresh-seconds-none--autoscale-target-utilization-none--collect-model-data-none--auth-enabled-none--cpu-cores-none--memory-gb-none--enable-app-insights-none--scoring-timeout-ms-none--replica-max-concurrent-requests-none--max-request-wait-time-none--num-replicas-none--primary-key-none--secondary-key-none--tags-none--properties-none--description-none--gpu-cores-none--period-seconds-none--initial-delay-seconds-none--timeout-seconds-none--success-threshold-none--failure-threshold-none--namespace-none--token-auth-enabled-none--compute-target-name-none-)

##### Both Deplployments

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| name                    |          | str  | <REPOSITORY_NAME>-<BRANCH_NAME> | The name to give the deployed service. Must be unique to the workspace, only consist of lowercase letters, numbers, or dashes, start with a letter, and be between 3 and 32 characters long. |
| deployment_compute_target |        | str  | ACI | A ComputeTarget to deploy the Webservice to. As Azure Container Instances has no associated ComputeTarget, leave this parameter as None to deploy to Azure Container Instances. | 
| inference_source_directory |       | str  | | The path to the folder that contains all files to create the image. |
| inference_entry_script  |          | str  | | The path to a local file that contains the code to run for the image. | 
| test_enabled            |          | bool | | Whether to run tests for this model deployment |
| test_source_directory   |          | str  | | The source directory for the test file. If `test_enable=true` this is required |
| test_script_name        |          | str  | | Test file name. If `test_enable=true` this is required |
| test_function_name      |          | str   | | Test function name. If `test_enable=true` this is required |
| conda_file              |          | bool  | | The path to a local file containing a conda environment definition to use for the image. |
| extra_docker_file_steps |          | str   | | The path to a local file containing additional Docker steps to run when setting up image. |
| enable_gpu              |          | str   | False | Indicates whether to enable GPU support in the image. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. Defaults to False. |
| cuda_version            |          | str | | The Version of CUDA to install for images that need GPU support. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. Supported versions are 9.0, 9.1, and 10.0. If enable_gpu is set, this defaults to '9.1'. |
| model_data_collection_enabled |    | bool | | Whether or not to enabled model data collection for the Webservice. |
| authentication_enabled  |          | bool   | | Whether or not to enable auth for this Webservice. Defaults to False. |
| app_insights_enabled    |          | bool  | `None` | Whether or not AppInsights logging is enabled for the Webservice. |
| runtime                 |          | str  | `'python'` or `'spark-py'` | The runtime to use for the image. Current supported runtimes are 'spark-py' and 'python'. |
| custom_base_image       |          | str  | | A custom image to be used as base image. If no base image is given then the base image will be used based off of given runtime parameter. |
| cpu_cores               |          | float  | | The number of cpu cores reequired for the model |
| memory_gb               |          | float  | | the amount of memory, in Gb, required for the model |
| delete_service_after_test |          | bool  | | Whether to delete the service after test deployment |
| no_code_deployment_enabled |          | bool  | |  |
| tags                    |          | dict  | | An optional list of tags used to filter returned results. Results are filtered based on the provided list, searching by either 'key' or '[key, value]'. Ex. ['key', ['key2', 'key2 value']] |
| properties              |          | dict  | | An optional list of properties used to filter returned results. Results are filtered based on the provided list, searching by either 'key' or '[key, value]'. Ex. ['key', ['key2', 'key2 value']] |
| description             |          | str  | | A description to give this image. |

##### ACI Deployment

ACI is the default deployment resource.

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| location               |           | str   |  | The location to provision cluster in. If not specified, will default to workspace location. Available regions for this compute can be found here: https://azure.microsoft.com/global-infrastructure/services/?regions=all&products=kubernetes-service |
| gpu_cores              |           | float |  | The number of GPU cores requested for the deployment | 
| ssl_enabled            |           | bool  |  | `true` to enable ssl | 
| ssl_cert_pem_file      |           | str   |  | A file path to a file containing cert information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. | 
| ssl_key_pem_file       |           | st    | | A file path to a file containing key information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_cname              |           | str   | | A CName to use if enabling SSL validation on the cluster. Must provide all three CName, cert file, and key file to enable SSL validation. |
| dns_name_label         |           | str   | | The DNS name label for the scoring endpoint. If not specified a unique DNS name label will be generated for the scoring endpoint. |
| cmk_vault_base_url     |           | str   | | customer managed key vault base url |
| cmk_key_name           |           | str   | | customer managed key name. |
| cmk_key_value          |           | str   | | customer managed key version. |

##### AKS Deployment

During the deployment of the model to AKS, you may also configure an AKS resource. Additional parameters must be set for this like whether to enable autoscaling and the liveness probe requiremente. These will be set to default parameters if not provided. More Information on autoscaling parameters can be found [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.autoscaler?view=azure-ml-py) and for liveness probe [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.livenessproberequirements?view=azure-ml-py).

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| autoscale_enabled       |          | bool  |    | Indicates whether the AutoScaler is enabled or disabled. |
| autoscale_min_replicas  |          | int   |    | The minimum number of containers for the AutoScaler to use | 
| autoscale_max_replicas  |          | int   |    | The maximum number of containers for the AutoScaler to use. |
| autoscale_refresh_seconds |        | int   |    | refresh_period_seconds | 
| autoscale_target_utilization|      | int   |    | The target utilization (in percent out of 100) the AutoScaler should attempt to maintain for the Webservice. |
| scoring_timeout_ms      |          | int   |    | The scoring timeout for the Webservice, in milliseconds. |
| replica_max_concurrent_requests|   | float |    | The maximum number of concurrent requests per container for the Webservice. |
| max_request_wait_time   |          | int   |    | The maximum request wait time for the Webservice, in milliseconds. |
| num_replicas            |          | int   |    | The number of replicas for the Webservice. |
| period_seconds          |          | int   | 10 | How often (in seconds) to perform the liveness probe. Defaults to 10 seconds. Minimum value is 1. |
| initial_delay_seconds   |          | int   |    | The number of seconds after the container has started before liveness probes are initiated. |
| timeout_seconds         |          | int   | 1  | The number of seconds after which the liveness probe times out. Defaults to 1 second. Minimum value is 1. |
| success_threshold       |          | int   | 3  | When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold times before giving up. Defaults to 3. Minimum value is 1. |
| failure_threshold       |          | int   | 1  | The minimum consecutive successes for the liveness probe to be considered successful after having failed. Defaults to 1. Minimum value is 1.|
| namespace               |          | str   |    | The AKS namespace of the Webservice. |
| token_auth_enabled      |          | bool  |    | Whether or not token auth is enabled for the Webservice. |

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

