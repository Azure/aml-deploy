![Integration Test](https://github.com/Azure/aml-deploy/workflows/Integration%20Test/badge.svg?branch=master&event=push)
![Lint and Test](https://github.com/Azure/aml-deploy/workflows/Lint%20and%20Test/badge.svg?branch=master&event=push)

# GitHub Action for deploying Machine Learning Models to Azure

## Deprecation notice

This Action is deprecated. Instead, consider using the [CLI (v2)](https://docs.microsoft.com/azure/machine-learning/how-to-configure-cli) to manage and interact with Azure Machine Learning endpoints and deployments in GitHub Actions.

**Important:** The CLI (v2) is not recommended for production use while in preview.

## Usage

The Deploy Machine Learning Models to Azure action will deploy your model on [Azure Machine Learning](https://azure.microsoft.com/en-us/services/machine-learning/) using GitHub Actions.

Get started today with a [free Azure account](https://azure.com/free/open-source)!

This repository contains GitHub Action for deploying Machine Learning Models to Azure Machine Learning and creates a real-time endpoint on the model to integrate models in other systems. The endpoint can be hosted either on an Azure Container Instance or on an Azure Kubernetes Service. 


This GitHub Action also allows you to provide a python script that executes tests against the Webservice endpoint after the model deployment has completed successfully. You can enable tests by setting the parameter `test_enabled` to true. In addition to that, you have to provide a python script (default `code/test/test.py`) which includes a function (default ` def main(webservice):`) that describes your tests that you want to execute against the service object. The python script gets the [webservice object](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice(class)?view=azure-ml-py) injected. The action fails, if the test script fails.


## Dependencies on other GitHub Actions
* [Checkout](https://github.com/actions/checkout) Checkout your Git repository content into GitHub Actions agent.
* [aml-workspace](https://github.com/Azure/aml-workspace) This action requires an Azure Machine Learning workspace to be present. You can either create a new one or re-use an existing one using the action. 
* [aml-registermodel](https://github.com/Azure/aml-registermodel) Before deploying the model, you need to register the model with Azure Machine Learning. If not already registered, you can use this action and use its output in deploy action. 
* [aml-compute](https://github.com/Azure/aml-compute) You don't need this if you want to host your endpoint on an ACI instance. But, if you want to host your endpoint on an AKS cluster, you can  manage the AKS Cluster via the action. 



## Create Azure Machine Learning and deploy an machine learning model using GitHub Actions

This action is one in a series of actions that can be used to setup an ML Ops process. **We suggest getting started with one of our template repositories**, which will allow you to create an ML Ops process in less than 5 minutes.

1. **Simple template repository: [ml-template-azure](https://github.com/machine-learning-apps/ml-template-azure)**

    Go to this template and follow the getting started guide to setup an ML Ops process within minutes and learn how to use the Azure       Machine Learning GitHub Actions in combination. This template demonstrates a very simple process for training and deploying machine     learning models.

2. **Advanced template repository: [mlops-enterprise-template](https://github.com/Azure-Samples/mlops-enterprise-template)**

    This template demonstrates how approval processes can be included in the process and how training and deployment workflows can be       splitted. It also shows how workflows (e.g. deployment) can be triggered from pull requests. More enhancements will be added to this     template in the future to make it more enterprise ready.

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
    - uses: Azure/aml-workspace@v1
      id: aml_workspace
      with:
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
    
    # AML Register Model Action
    - uses: Azure/aml-registermodel@v1
      id: aml_registermodel
      with:
        azure_credentials: ${{ secrets.AZURE_CREDENTIALS }}
        run_id:  "<your-run-id>"
        experiment_name: "<your-experiment-name>"
    
    # Deploy model in Azure Machine Learning to ACI
    - name: Deploy model
      id: aml_deploy
      uses: Azure/aml-deploy@v1
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
| model_name | x | - | Name of the model that will be deployed. You will get it as an output of register model action as in above example workflow. |
| model_version | x | - | Version of the model that will be deployed. You will get it as an output of register model action as in above example workflow. |
| parameters_file |  | `"deploy.json"` | We expect a JSON file in the `.cloud/.azure` folder in root of your repository specifying your model deployment details. If you have want to provide these details in a file other than "deploy.json" you need to provide this input in the action. |

#### azure_credentials ( Azure Credentials ) 

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


#### parameters_file (Parameters File)

The action tries to load a JSON file in the `.cloud/.azure` folder in your repository, which specifies details for the model deployment to your Azure Machine Learning Workspace. By default, the action expects a file with the name `deploy.json`. If your JSON file has a different name, you can specify it with this parameter. Note that none of these values are required and, in the absence, defaults will be created with a combination of the repo name and branch name.

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
| enable_gpu              |          | bool | false | Indicates whether to enable GPU support in the image. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. |
| cuda_version            |          | str | `"9.1"` if `enable_gpu` is set to true | The Version of CUDA to install for images that need GPU support. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. Supported versions are 9.0, 9.1, and 10.0. |
| runtime                 |          | str: `"python"` or `"spark-py"` | `"python"` | The runtime to use for the image. |
| custom_base_image       |          | str  | null | A custom Docker image to be used as base image. If no base image is given then the base image will be used based off of given runtime parameter. |
| model_data_collection_enabled |    | bool | false | Whether or not to enable model data collection for this Webservice. |
| authentication_enabled  |          | bool | false for ACI, true for AKS | Whether or not to enable key auth for this Webservice. |
| app_insights_enabled    |          | bool | false | Whether or not to enable Application Insights logging for this Webservice. |
| cpu_cores               |          | float: ]0.0, inf[ | 0.1 | The number of CPU cores to allocate for this Webservice. Can be a decimal. |
| memory_gb               |          | float: ]0.0, inf[ | 0.5 | The amount of memory (in GB) to allocate for this Webservice. Can be a decimal. |
| delete_service_after_deployment |  | bool | false | Indicates whether the service gets deleted after the deployment completed successfully. |
| tags                    |          | dict: {"<your-run-tag-key>": "<your-run-tag-value>", ...} | null | Dictionary of key value tags to give this Webservice. |
| properties              |          | dict: {"<your-run-tag-key>": "<your-run-tag-value>", ...} | | Dictionary of key value properties to give this Webservice. These properties cannot be changed after deployment, however new key value pairs can be added. |
| description             |          | str  | null | A description to give this Webservice and image. |
| test_enabled            |          | bool | false | Whether to run tests for this model deployment and the created real-time endpoint. |
| test_file_path          |          | str  | `"code/test/test.py"` | Path to the python script in your repository in which you define your own tests that you want to run against the webservice endpoint. The GitHub Action fails, if your script fails. |
| test_file_function_name |          | str   | `"main"` | Name of the function in your python script in your repository in which you define your own tests that you want to run against the webservice endpoint. The function gets the webservice object injected and allows you to run tests against the scoring uri. The GitHub Action fails, if your script fails. |
| profiling_enabled       |          | bool | false | Whether or not to profile this model for an optimal combination of cpu and memory. To use this functionality, you also have to provide a model profile dataset (`profiling_dataset`). If the parameter is not specified, the Action will try to use the sample input dataset that the model was registered with. Please, note that profiling is a long running operation and can take up to 25 minutes depending on the size of the dataset. More details can be found [here](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/deployment/production-deploy-to-aks/production-deploy-to-aks.ipynb). |
| profiling_dataset       |          | str   | null | Name of the dataset that should be used for model profiling. |
| skip_deployment         |          | bool | false | Indicates whether the deployment to ACI or AKS should be skipped. This can be used in combination with `create_image` to only create a Docker image that can be used for further deployment. |
| create_image            |          | str: `"docker"`, `"function_blob"`, `"function_http"` or `"function_service_bus_queue"`  | null | Indicates whether a Docker image should be created which can be used for further deployment. |

Please visit [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.model.inferenceconfig?view=azure-ml-py) and [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.model(class)?view=azure-ml-py#deploy-workspace--name--models--inference-config-none--deployment-config-none--deployment-target-none--overwrite-false-) for more details.

##### ACI specific parameters

ACI is the default deployment resource. A sample file for an aci deployment can be found in the `.cloud/.azure` folder.

| Parameter              | Required | Allowed Values | Default    | Description |
| ---------------------- | -------- | -------------- | ---------- | ----------- |
| location               |           | str: [supported region](https://azure.microsoft.com/en-us/global-infrastructure/services/?products=container-instances) | workspace location | The Azure region to deploy this Webservice to. |
| ssl_enabled            |           | bool  | false | Whether or not to enable SSL for this Webservice. |
| ssl_cert_pem_file      |           | str   | null | A file path to a file containing cert information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_key_pem_file       |           | str   | null | A file path to a file containing key information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_cname              |           | str   | null | A CName to use if enabling SSL validation on the cluster. Must provide all three CName, cert file, and key file to enable SSL validation. |
| dns_name_label         |           | str   | null | The DNS name label for the scoring endpoint. If not specified a unique DNS name label will be generated for the scoring endpoint. |

Please visit [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aciwebservice?view=azure-ml-py#deploy-configuration-cpu-cores-none--memory-gb-none--tags-none--properties-none--description-none--location-none--auth-enabled-none--ssl-enabled-none--enable-app-insights-none--ssl-cert-pem-file-none--ssl-key-pem-file-none--ssl-cname-none--dns-name-label-none--primary-key-none--secondary-key-none--collect-model-data-none--cmk-vault-base-url-none--cmk-key-name-none--cmk-key-version-none-) for more details.

##### AKS Deployment

For the deployment of the model to AKS, you must configure an AKS resource and specify the name of the AKS cluster with the `deployment_compute_target` parameter. Additional parameters allow you to finetune your deployment on AKS with options like autoscaling and the liveness probe requirements. These will be set to default parameters if not provided.

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| gpu_cores              |           | int: [0, inf[ | 1 | The number of GPU cores to allocate for this Webservice. |
| autoscale_enabled       |          | bool  | true if `num_replicas` is null | Whether to enable autoscale for this Webservice. |
| autoscale_min_replicas  |          | int: [1, inf[ | 1 | The minimum number of containers to use when autoscaling this Webservice. | 
| autoscale_max_replicas  |          | int: [1, inf[ | 10 | The maximum number of containers to use when autoscaling this Webservice. |
| autoscale_refresh_seconds |        | int: [1, inf[ | 1 | How often the autoscaler should attempt to scale this Webservice (in seconds). | 
| autoscale_target_utilization|      | int: [1, 100] | 70 | The target utilization (in percent out of 100) the autoscaler should attempt to maintain for this Webservice. |
| scoring_timeout_ms      |          | int: [1, inf[ | 60000 | A timeout in ms to enforce for scoring calls to this Webservice. |
| replica_max_concurrent_requests|   | int: [1, inf[ | 1 | The number of maximum concurrent requests per replica to allow for this Webservice. **Do not change this setting from the default value of 1 unless instructed by Microsoft Technical Support or a member of Azure Machine Learning team.** |
| max_request_wait_time   |          | int: [0, inf[ | 500 | The maximum amount of time a request will stay in the queue (in milliseconds) before returning a 503 error. |
| num_replicas            |          | int   | null | The number of containers to allocate for this Webservice. **No default, if this parameter is not set then the autoscaler is enabled by default.** |
| period_seconds          |          | int: [1, inf[ | 10 | How often (in seconds) to perform the liveness probe. |
| initial_delay_seconds   |          | int: [1, inf[ | 310 | The number of seconds after the container has started before liveness probes are initiated. |
| timeout_seconds         |          | int: [1, inf[ | 1  | The number of seconds after which the liveness probe times out. |
| success_threshold       |          | int: [1, inf[ | 1 | The minimum consecutive successes for the liveness probe to be considered successful after having failed. |
| failure_threshold       |          | int: [1, inf[ | 3  | When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold times before giving up. |
| namespace               |          | str   | null | The Kubernetes namespace in which to deploy this Webservice: up to 63 lowercase alphanumeric ('a'-'z', '0'-'9') and hyphen ('-') characters. The first and last characters cannot be hyphens. |
| token_auth_enabled      |          | bool  | false | Whether to enable Token authentication for this Webservice. If this is enabled, users can access this Webservice by fetching an access token using their Azure Active Directory credentials. |

Please visit [this website](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.akswebservice?view=azure-ml-py#deploy-configuration-autoscale-enabled-none--autoscale-min-replicas-none--autoscale-max-replicas-none--autoscale-refresh-seconds-none--autoscale-target-utilization-none--collect-model-data-none--auth-enabled-none--cpu-cores-none--memory-gb-none--enable-app-insights-none--scoring-timeout-ms-none--replica-max-concurrent-requests-none--max-request-wait-time-none--num-replicas-none--primary-key-none--secondary-key-none--tags-none--properties-none--description-none--gpu-cores-none--period-seconds-none--initial-delay-seconds-none--timeout-seconds-none--success-threshold-none--failure-threshold-none--namespace-none--token-auth-enabled-none--compute-target-name-none-) for more details. More Information on autoscaling parameters can be found [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.autoscaler?view=azure-ml-py) and for liveness probe [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.webservice.aks.livenessproberequirements?view=azure-ml-py).

### Outputs

| Output              | Description                     |
| ------------------- | ------------------------------- |
| service_scoring_uri | Scoring URI of the webservice that was created (only provided if `delete_service_after_deployment` is set to False). |
| service_swagger_uri | Swagger Uri of the webservice that was created (only provided if `delete_service_after_deployment` is set to False). |
| acr_address         | The DNS name or IP address (e.g. myacr.azurecr.io) of the Azure Container Registry (ACR) (only provided if `create_image` is not None).  |
| acr_username        | The username for ACR (only provided if `create_image` is not None). |
| acr_password        | The password for ACR (only provided if `create_image` is not None). |
| package_location    | Full URI of the docker image (e.g. myacr.azurecr.io/azureml/azureml_*) (only provided if `create_image` is not None). |
| profiling_details   | Dictionary of details of the model profiling result. This will only be provided, if the model profiling method is used and successfully executed. |

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

