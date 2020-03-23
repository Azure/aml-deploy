# Azure Machine Learning Deploy Action

https://docs.microsoft.com/en-us/azure/templates/Microsoft.ContainerService/2020-02-01/managedClusters?toc=%2Fen-us%2Fazure%2Fazure-resource-manager%2Ftoc.json&bc=%2Fen-us%2Fazure%2Fbread%2Ftoc.json#managedclusteragentpoolprofile-object

## Usage

Description. 

### Example workflow

```yaml
name: My Workflow
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@master
    - name: Run action

    steps:
    - uses: actions/checkout@master
    - name: Run action

      # Put your action repo here
      uses: me/myaction@master

      # Put an example of your mandatory inputs here
      with:
        myInput: world
```

### Inputs

| Input                                             | Description                                        |
|------------------------------------------------------|-----------------------------------------------|
| `myInput`  | An example mandatory input    |
| `anotherInput` _(optional)_  | An example optional input    |

#### Parameter File

A sample file can be found in this repository in the folder `.aml`. The action expects a similar parameter file in your repository in the `.aml folder`.

| Parameter Name      | Required | Allowed Values                       | Description |
| ------------------- | -------- | ------------------------------------ | ----------- |
| createWorkspace     | x        | bool: true, false                    | Create Workspace if it could not be loaded |
| name                | x        | str                                  | For more details please read [here](https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.workspace.workspace?view=azure-ml-py#create-name--auth-none--subscription-id-none--resource-group-none--location-none--create-resource-group-true--sku--basic---friendly-name-none--storage-account-none--key-vault-none--app-insights-none--container-registry-none--cmk-keyvault-none--resource-cmk-uri-none--hbi-workspace-false--default-cpu-compute-target-none--default-gpu-compute-target-none--exist-ok-false--show-output-true-) |
| friendlyName        |          | str                                  |
| createResourceGroup |          | bool: true, false                    |
| location            |          | str: [supported region](https://azure.microsoft.com/global-infrastructure/services/?products=machine-learning-service) |
| sku                 |          | str: "basic", "enterprise"           |
| storageAccount      |          | str: Azure resource ID format        |
| keyVault            |          | str: Azure resource ID format        |
| appInsights         |          | str: Azure resource ID format        |
| containerRegistry   |          | str: Azure resource ID format        |
| cmkKeyVault         |          | str: Azure resource ID format        |
| resourceCmkUri      |          | str: URI of the customer managed key |
| hbiWorkspace        |          | bool: true, false                    |


### Outputs

| Output                                             | Description                                        |
|------------------------------------------------------|-----------------------------------------------|
| `myOutput`  | An example output (returns 'Hello world')    |

## Examples



### Using the optional input

This is how to use the optional input.

```yaml
with:
  myInput: world
  anotherInput: optional
```

### Using outputs

Show people how to use your outputs in another action.

```yaml
steps:
- uses: actions/checkout@master
- name: Run action
  id: myaction

  # Put your action name here
  uses: me/myaction@master

  # Put an example of your mandatory arguments here
  with:
    myInput: world

# Put an example of using your outputs here
- name: Check outputs
    run: |
    echo "Outputs - ${{ steps.myaction.outputs.myOutput }}"
```

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


# Environment variables

- Container registry address username, password: CONTAINERREGISTRYADRESS, CONTAINERREGISTRYUSERNAME, CONTAINERREGISTRYPASSWORD
- service primary key, secondary key: PRIMARYKEY, SECONDARYKEY