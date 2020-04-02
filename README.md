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

"name": "<your-webservice-name>",
    "deployment_compute_target": "<your-deployment-compute-target-name>", // do not specify deployment compute target name for deployment on Azure Container Registry
    "inference_source_directory": "<your-inference-source-directory>",
    "inference_entry_script": "<your-inference-entry-script>",
    "test_enabled": true,
    "test_source_directory": "<your-test-source-directory>",
    "test_script_name": "<your-test-script-name>",
    "test_function_name": "<your-test-function-name>",
    "conda_file": "<your-conda-environment-file-path>",
    "extra_docker_file_steps": "<your-extra-docker-steps-file-path>",
    "enable_gpu": false,
    "cuda_version": "<your-cuda-version>",
    "model_data_collection_enabled": true,
    "authentication_enabled": true,
    "app_insights_enabled": true,
    "runtime": "<'python' or 'spark-py'>",
    "custom_base_image": "<your-custom-docker-base-image>",
    "cpu_cores": 0.1,
    "memory_gb": 0.5,
    "delete_service_after_test": false,
    "no_code_deployment_enabled": false,
    "tags": {"<your-webservice-tag-key>": "<your-webservice-tag-value>"},
    "properties": {"<your-webservice-property-key>": "<your-webservice-property-value>"},
    "description": "<your-webservice-description>",

    // aci specific parameters
    "location": "<your-aci-location>",
    "gpu_cores": 0,
    "ssl_enabled": true,
    "ssl_cert_pem_file": "<your-aci-ssl-cert-pem-file>",
    "ssl_key_pem_file": "<your-aci-ssl-key-pem-file>",
    "ssl_cname": "<your-aci-ssl-cname>",
    "dns_name_label": "<your-aci-dns-name-label>",
    "cmk_vault_base_url": "<your-aci-cmk-vault-base-url>",
    "cmk_key_name": "<your-aci-cmk-key-name>",
    "cmk_key_version": "<your-aci-cmk-key-version>",

    // aks specific parameters
    "autoscale_enabled": true,
    "autoscale_min_replicas": 1,
    "autoscale_max_replicas": 10,
    "autoscale_refresh_seconds": 1,
    "autoscale_target_utilization": 70,
    "scoring_timeout_ms": 60000,
    "replica_max_concurrent_requests": 1,
    "max_request_wait_time": 1000,
    "num_replicas": null,
    "period_seconds": 10,
    "initial_delay_seconds": 310,
    "timeout_seconds": 2,
    "success_threshold": 1,
    "failure_threshold": 3,
    "namespace": "<your-aks-namespace>",
    "token_auth_enabled": true
    
##### Both Deplployments

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| name               |          |                |            |             |
| deployment_compute_target | x        | str            |            | | 
| inference_source_directory |          | str            |  |
| inference_entry_script |          | str | |  | 
| test_enabled            |          | str      |      |  |
| test_source_directory   |          | dict  | |  |
| test_script_name        |          | dict  | | |
| test_function_name      |          | str   | | |
| conda_file                |          | list  | |  |
| extra_docker_file_steps |          | str   | |  |
| enable_gpu              |          | str   | |  |
| cuda_version            |          | float | |  |
| model_data_collection_enabled |          | float | |  |
| authentication_enabled  |          | str   | |  |
| app_insights_enabled    |          | list  | |  |
| runtime                 |          | list  | |  |
| custom_base_image       |          | bool  | |  |
| cpu_cores               |          | bool  | |  |
| memory_gb               |          | bool  | |  |
| delete_service_after_test |          | bool  | |  |
| no_code_deployment_enabled |          | bool  | |  |
| tags                    |          | bool  | |  |
| properties              |          | bool  | |  |
| description             |          | bool  | |  |

##### ACI Deployment

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| location               |          |                |            |             |
| gpu_cores | x        | str            |            | | 
| ssl_enabled |          | str            |  |
| ssl_cert_pem_file |          | str | |  | 
| ssl_key_pem_file            |          | str      |      |  |
| ssl_cname   |          | dict  | |  |
| dns_name_label        |          | dict  | | |
| cmk_vault_base_url      |          | str   | | |
| cmk_key_name                |          | list  | |  |
| cmk_key_value |          | str   | |  |

##### AKS Deployment

| Parameter               | Required | Allowed Values | Default    | Description |
| ----------------------- | -------- | -------------- | ---------- | ----------- |
| autoscale_enabled       |          |                |            |             |
| autoscale_min_replicas  | x        | str            |            | | 
| autoscale_max_replicas  |          | str            |  |
| autoscale_refresh_seconds |          | str | |  | 
| autoscale_target_utilization |          | str      |      |  |
| scoring_timeout_ms      |          | dict  | |  |
| replica_max_concurrent_requests |          | dict  | | |
| max_request_wait_time   |          | str   | | |
| num_replicas            |          | list  | |  |
| period_seconds          |          | str   | |  |
| initial_delay_seconds   |          | str   | |  |
| timeout_seconds         |          | float | |  |
| success_threshold       |          | float | |  |
| failure_threshold       |          | str   | |  |
| namespace               |          | list  | |  |
| token_auth_enabled      |          | list  | |  |

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

