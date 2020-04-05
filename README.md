![Integration Test](https://github.com/Azure/aml-deploy/workflows/Integration%20Test/badge.svg)
![Lint](https://github.com/Azure/aml-deploy/workflows/Lint/badge.svg)

# Azure Machine Learning Deploy Action

## Usage

The Azure Machine Learning Deploy action will deploy your model on Azure Machine Learning and create a real-time endpoint for use in other systems. The action currently supports Azure Container Instance and Azure Kubernetes Service as compute target and also supports the no-code deployment of Azure Machine Learning, if the model has been regiustered accordingly.

This GitHub Action also allows you to provide a python script that executes tests against the  Webservice endpoint after the model deplyoment has completed successfully. You can enable tests by setting the parameter `test_enabled` to true. In addition to that, you have to provide a python script (default `code/test/test.py`) which includes a function (default ` def main(webservice):`) that describes your tests that you want to execute against the service object. The python script gets the [webservice object](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice(class)?view=azure-ml-py) injected. The action fails, if the test script fails.

This action requires an Azure Machine Learning workspace to be created or attached to via the [aml-workspace](https://github.com/Azure/aml-workspace) action and an AKS cluster if you are planning to deploy your model to such a compute target. AKS clsuters can be managed via the [aml-compute](https://github.com/Azure/aml-compute) action.

## Template repositories

This action is one in a series of actions that can be used to setup an ML Ops process. Examples of these can be found at
1. Simple example: [ml-template-azure](https://github.com/machine-learning-apps/ml-template-azure) and
2. Comprehensive example: [aml-template](https://github.com/Azure/aml-template).

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
    - uses: Azure/aml-registermodel
      id: aml_registermodel
      with:
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
        run_id:  "<your-run-id>"
        experiment_name: "<your-experiment-name>"
    
    # Deploy model in Azure Machine Learning to ACI
    - name: Deploy model
      id: aml_deploy
      uses: Azure/aml-deploy@master
      with:
        # required inputs
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
        model_name:  ${{ steps.aml_registermodel.outputs.model_name }}
        model_version: ${{ steps.aml_registermodel.outputs.model_version }}
        # optional inputs
        parameters_file: "deploy.json"
```

### Inputs

| Input | Required | Default | Description |
| ----- | -------- | ------- | ----------- |
| azure_credentials | x | - | Output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth`. This should be stored in your secrets |
| model_name | x | - | Name of the model that will be deployed. |
| model_version | x | - | Version of the model that will be deployed. |
| parameters_file |  | `"registermodel.json"` | JSON file in the `.cloud/.azure` folder specifying your Azure Machine Learning model registration details. |

#### Azure Credentials

Azure credentials are required to connect to your Azure Machine Learning Workspace. These may have been created for an action you are already using in your repository, if so, you can skip the steps below.

Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) on your computer or use the Cloud CLI and execute the following command to generate the required credentials:

```sh
# Replace {service-principal-name}, {subscription-id} and {resource-group} with your Azure subscription id and resource group name and any name for your service principle
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

Add this JSON output as [a secret](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets#creating-encrypted-secrets) with the name `AZURE_CREDENTIALS` in your GitHub repository.

#### Parameters File

The action tries to load a JSON file in the `.cloud/.azure` folder in your repository, which specifies details for the model deployment to your Azure Machine Learning Workspace. By default, the action expects a file with the name `deploy.json`. If your JSON file has a different name, you can specify it with this parameter. Note that none of these values are required and in the absence, defaults will be created with a combination of the repo name and branch name.

A sample file can be found in this repository in the folder `.cloud/.azure`. There are separate parameters that are used for the ACI deployment, the AKS deployment and some that are common for both deployment options.

##### Common parameters

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| name                    |          | str  | <REPOSITORY_NAME>-<BRANCH_NAME> | The name to give the deployed service. Must be unique to the workspace, only consist of lowercase letters, numbers, or dashes, start with a letter, and be between 3 and 32 characters long. |
| deployment_compute_target | (for AKS deployment) | str  | null | Name of the compute target to deploy the webservice to. As Azure Container Instances has no associated ComputeTarget, leave this parameter as null to deploy to Azure Container Instances. |
| inference_source_directory |       | str  | `"code/deploy/"` | The path to the folder that contains all files to create the image. |
| inference_entry_script  |          | str  | `"score.py"` | The path to a local file in your repository that contains the code to run for the image and score the data. This path is relative to the specified source directory. The python script has to define an `init` and a `run` function. A sample can be found in the template repositories. |
| conda_file              |          | str  | `"environment.yml"` | The path to a local file in your repository containing a conda environment definition to use for the image. This path is relative to the specified source directory. |
| extra_docker_file_steps |          | str   | null | The path to a local file in your repository containing additional Docker steps to run when setting up image. This path is relative to the specified source directory. |
| enable_gpu              |          | str   | false | Indicates whether to enable GPU support in the image. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. |
| cuda_version            |          | str | `"9.1"` if `enable_gpu` is set to true | The Version of CUDA to install for images that need GPU support. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. Supported versions are 9.0, 9.1, and 10.0. |
| runtime                 |          | str: `"python"` or `"spark-py"` | `"python"` | The runtime to use for the image. |
| custom_base_image       |          | str  | null | A custom Docker image to be used as base image. If no base image is given then the base image will be used based off of given runtime parameter. |
| model_data_collection_enabled |    | bool | false | Whether or not to enable model data collection for this Webservice. |
| authentication_enabled  |          | bool | false for ACI, true for AKS | Whether or not to enable key auth for this Webservice. |
| app_insights_enabled    |          | bool  | false | Whether or not to enable Application Insights logging for this Webservice. |
| cpu_cores               |          | float | 0.1 | The number of CPU cores to allocate for this Webservice. Can be a decimal. |
| memory_gb               |          | float  | 0.5 | The amount of memory (in GB) to allocate for this Webservice. Can be a decimal. |
| delete_service_after_deployment |  | bool | false | Indicates whether the service gets deleted after the deployment completed successfully. |
| tags                    |          | dict: {"<your-run-tag-key>": "<your-run-tag-value>", ...} | null | Dictionary of key value tags to give this Webservice. |
| properties              |          | dict: {"<your-run-tag-key>": "<your-run-tag-value>", ...} | | Dictionary of key value properties to give this Webservice. These properties cannot be changed after deployment, however new key value pairs can be added. |
| description             |          | str  | null | A description to give this Webservice and image. |
| test_enabled            |          | bool | false | Whether to run tests for this model deployment and the created real-time endpoint. |
| test_file_path          |          | str  | `"code/test/test.py"` | Path to the python script in your repository in which you define your own tests that you want to run against the webservice endpoint. The GitHub Action fails, if your script fails. |
| test_file_function_name |          | str   | `"main"` | Name of the function in your python script in your repository in which you define your own tests that you want to run against the webservice endpoint. The function gets the webservice object injected and allows you to run tests against the scoring uri. The GitHub Action fails, if your script fails. |

Please visit [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.model.inferenceconfig?view=azure-ml-py) and [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.model(class)?view=azure-ml-py#deploy-workspace--name--models--inference-config-none--deployment-config-none--deployment-target-none--overwrite-false-) for more details.

##### ACI specific parameters

ACI is the default deployment resource. A sample file for an aci deployment can be found in the `.cloud/.azure` folder.

| Parameter              | Required | Allowed Values | Default    | Description |
| ---------------------- | -------- | -------------- | ---------- | ----------- |
| location               |           | str: [supported region](https://azure.microsoft.com/en-us/global-infrastructure/services/?products=container-instances) | workspace location | The Azure region to deploy this Webservice to. |
| ssl_enabled            |           | bool  | false | Whether or not to enable SSL for this Webservice. |
| ssl_cert_pem_file      |           | str   | null | A file path to a file containing cert information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_key_pem_file       |           | st    | null | A file path to a file containing key information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_cname              |           | str   | null | A CName to use if enabling SSL validation on the cluster. Must provide all three CName, cert file, and key file to enable SSL validation. |
| dns_name_label         |           | str   | null | The DNS name label for the scoring endpoint. If not specified a unique DNS name label will be generated for the scoring endpoint. |

Please visit [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aciwebservice?view=azure-ml-py#deploy-configuration-cpu-cores-none--memory-gb-none--tags-none--properties-none--description-none--location-none--auth-enabled-none--ssl-enabled-none--enable-app-insights-none--ssl-cert-pem-file-none--ssl-key-pem-file-none--ssl-cname-none--dns-name-label-none--primary-key-none--secondary-key-none--collect-model-data-none--cmk-vault-base-url-none--cmk-key-name-none--cmk-key-version-none-) for more details.

##### AKS Deployment

For the deployment of the model to AKS, you must configure an AKS resource and specify the name of the AKS cluster with the `deployment_compute_target` parameter. Additional parameters allow you to finetune your deployment on AKS with options like autoscaling and the liveness probe requirements. These will be set to default parameters if not provided.

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| gpu_cores              |           | float | 1 | The number of GPU cores to allocate for this Webservice. |
| autoscale_enabled       |          | bool  | true if `num_replicas` is null | Whether or not to enable autoscaling for this Webservice. |
| autoscale_min_replicas  |          | int   | 1 | The minimum number of containers to use when autoscaling this Webservice. | 
| autoscale_max_replicas  |          | int   | 10 | The maximum number of containers to use when autoscaling this Webservice. |
| autoscale_refresh_seconds |        | int   | 1 | How often the autoscaler should attempt to scale this Webservice. | 
| autoscale_target_utilization|      | int   | 70 | The target utilization (in percent out of 100) the autoscaler should attempt to maintain for this Webservice. |
| scoring_timeout_ms      |          | int   | 60000 | A timeout in ms to enforce for scoring calls to this Webservice. |
| replica_max_concurrent_requests|   | float | 1 | The number of maximum concurrent requests per replica to allow for this Webservice. **Do not change this setting from the default value of 1 unless instructed by Microsoft Technical Support or a member of Azure Machine Learning team.** |
| max_request_wait_time   |          | int   | 500 | The maximum amount of time a request will stay in the queue (in milliseconds) before returning a 503 error. |
| num_replicas            |          | int   | null | The number of containers to allocate for this Webservice. **No default, if this parameter is not set then the autoscaler is enabled by default.** |
| period_seconds          |          | int: [1, inf[ | 10 | How often (in seconds) to perform the liveness probe. |
| initial_delay_seconds   |          | int   | 310 | The number of seconds after the container has started before liveness probes are initiated. |
| timeout_seconds         |          | int: [1, inf[ | 1  | The number of seconds after which the liveness probe times out. |
| success_threshold       |          | int: [1, inf[ | 1 | The minimum consecutive successes for the liveness probe to be considered successful after having failed. |
| failure_threshold       |          | int: [1, inf[ | 3  | When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold times before giving up. |
| namespace               |          | str   | null | The Kubernetes namespace in which to deploy this Webservice: up to 63 lowercase alphanumeric ('a'-'z', '0'-'9') and hyphen ('-') characters. The first and last characters cannot be hyphens. |
| token_auth_enabled      |          | bool  | false | Whether or not to enable Token auth for this Webservice. If this is enabled, users can access this Webservice by fetching an access token using their Azure Active Directory credentials. |

Please visit [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.akswebservice?view=azure-ml-py#deploy-configuration-autoscale-enabled-none--autoscale-min-replicas-none--autoscale-max-replicas-none--autoscale-refresh-seconds-none--autoscale-target-utilization-none--collect-model-data-none--auth-enabled-none--cpu-cores-none--memory-gb-none--enable-app-insights-none--scoring-timeout-ms-none--replica-max-concurrent-requests-none--max-request-wait-time-none--num-replicas-none--primary-key-none--secondary-key-none--tags-none--properties-none--description-none--gpu-cores-none--period-seconds-none--initial-delay-seconds-none--timeout-seconds-none--success-threshold-none--failure-threshold-none--namespace-none--token-auth-enabled-none--compute-target-name-none-) for more details. More Information on autoscaling parameters can be found [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.autoscaler?view=azure-ml-py) and for liveness probe [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.livenessproberequirements?view=azure-ml-py).

### Outputs

| Output              | Description                     |
| ------------------- | ------------------------------- |
| service_scoring_uri | Scoring URI of the webservice that was created (only provided if delete_service_after_test is set to False). |
| service_swagger_uri | Swagger Uri of the webservice that was created (only provided if delete_service_after_test is set to False). |

### Environment variables

Certain parameters are considered secrets and should therefore be passed as environment variables from your secrets, if you want to use custom values.

| Environment variable        | Required | Allowed Values | Default | Description |
| --------------------------- | -------- | -------------- | ------- | ----------- |
| CONTAINER_REGISTRY_ADRESS   |          | str            | null    | The DNS name or IP address of the Azure Container Registry (ACR). Required, if you specified a `custom_base_image` that is only available in your ACR. |
| CONTAINER_REGISTRY_USERNAME |          | str            | null    | The username for ACR. Required, if you specified a `custom_base_image` that is only available in your ACR. |
| CONTAINER_REGISTRY_PASSWORD |          | str            | null    | The password for ACR. Required, if you specified a `custom_base_image` that is only available in your ACR. |
| PRIMARY_KEY                 |          | str            | null    | A primary auth key to use for this Webservice. If not specified, Azure will automatically assign a key. |
| SECONDARY_KEY               |          | str            | null    | A secondary auth key to use for this Webservice. If not specified, Azure will automatically assign a key. |
| CMK_VAULT_BASE_URL          |           | str   | null | Customer managed Key Vault base url. This value is ACI specific. |
| CMK_KEY_NAME                |           | str   | null | Customer managed key name.  This value is ACI specific. |
| CMK_KEY_VERSION             |           | str   | null | Customer managed key version.  This value is ACI specific. |

### Other Azure Machine Learning Actions

- [aml-workspace](https://github.com/Azure/aml-workspace) - Connects to or creates a new workspace
- [aml-compute](https://github.com/Azure/aml-compute) - Connects to or creates a new compute target in Azure Machine Learning
- [aml-run](https://github.com/Azure/aml-run) - Submits a ScriptRun, an Estimator or a Pipeline to Azure Machine Learning
- [aml-registermodel](https://github.com/Azure/aml-registermodel) - Registers a model to Azure Machine Learning
- [aml-deploy](https://github.com/Azure/aml-deploy) - Deploys a model and creates an endpoint for the model

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

