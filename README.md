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
    
##### Both Deplployments

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| name                    |          |      | |  |
| deployment_compute_target | x      | str  | |  | 
| inference_source_directory |       | str  | | The path to the folder that contains all files to create the image. |
| inference_entry_script  |          | str  | | The path to a local file that contains the code to run for the image. | 
| test_enabled            |          | bool | |  |
| test_source_directory   |          | str  | |  |
| test_script_name        |          | str  | |  |
| test_function_name      |          | str   | | |
| conda_file              |          | bool  | | The path to a local file containing a conda environment definition to use for the image. |
| extra_docker_file_steps |          | str   | | The path to a local file containing additional Docker steps to run when setting up image. |
| enable_gpu              |          | str   | False | Indicates whether to enable GPU support in the image. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. Defaults to False. |
| cuda_version            |          | str | | The Version of CUDA to install for images that need GPU support. The GPU image must be used on Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute, Azure Virtual Machines, and Azure Kubernetes Service. Supported versions are 9.0, 9.1, and 10.0. If enable_gpu is set, this defaults to '9.1'. |
| model_data_collection_enabled |    | bool | |  |
| authentication_enabled  |          | bool   | |  |
| app_insights_enabled    |          | bool  | |  |
| runtime                 |          | str  | `'python'` or `'spark-py'` | The runtime to use for the image. Current supported runtimes are 'spark-py' and 'python'. |
| custom_base_image       |          | str  | | A custom image to be used as base image. If no base image is given then the base image will be used based off of given runtime parameter. |
| cpu_cores               |          | float  | |  |
| memory_gb               |          | float  | |  |
| delete_service_after_test |          | bool  | |  |
| no_code_deployment_enabled |          | bool  | |  |
| tags                    |          | str  | |  |
| properties              |          | str  | |  |
| description             |          | str  | | A description to give this image. |

##### ACI Deployment

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| location               |           | str   |     | The location to provision cluster in. If not specified, will default to workspace location. Available regions for this compute can be found here: https://azure.microsoft.com/global-infrastructure/services/?regions=all&products=kubernetes-service |
| gpu_cores              |           | float |            | | 
| ssl_enabled            |           | bool  |  |
| ssl_cert_pem_file      |           | str   |  | A file path to a file containing cert information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. | 
| ssl_key_pem_file       |          | str      |      | A file path to a file containing key information for SSL validation. Must provide all three CName, cert file, and key file to enable SSL validation. |
| ssl_cname              |          | str  | | A CName to use if enabling SSL validation on the cluster. Must provide all three CName, cert file, and key file to enable SSL validation. |
| dns_name_label         |          | str  | | |
| cmk_vault_base_url     |          | str   | | |
| cmk_key_name           |          | str  | |  |
| cmk_key_value          |          | str   | |  |

##### AKS Deployment

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| autoscale_enabled       |          | bool           |            |             |
| autoscale_min_replicas  | x        | int            |            | | 
| autoscale_max_replicas  |          | int            |  |
| autoscale_refresh_seconds |          | float | |  | 
| autoscale_target_utilization|          | float      |      |  |
| scoring_timeout_ms      |          | float  | |  |
| replica_max_concurrent_requests|          | float  | | |
| max_request_wait_time   |          | float   | | |
| num_replicas            |          | int     | |  |
| period_seconds          |          | float   | |  |
| initial_delay_seconds   |          | float   | |  |
| timeout_seconds         |          | float | |  |
| success_threshold       |          | float | |  |
| failure_threshold       |          | float   | |  |
| namespace               |          | str  | |  |
| token_auth_enabled      |          | bool  | |  |

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

