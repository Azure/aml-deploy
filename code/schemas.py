azure_credentials_schema = {
    "$id": "http://azure-ml.com/schemas/azure_credentials.json",
    "$schema": "http://json-schema.org/schema",
    "title": "azure_credentials",
    "description": "JSON specification for your azure credentials",
    "type": "object",
    "required": ["clientId", "clientSecret", "subscriptionId", "tenantId"],
    "properties": {
        "clientId": {
            "type": "string",
            "description": "The client ID of the service principal."
        },
        "clientSecret": {
            "type": "string",
            "description": "The client secret of the service principal."
        },
        "subscriptionId": {
            "type": "string",
            "description": "The subscription ID that should be used."
        },
        "tenantId": {
            "type": "string",
            "description": "The tenant ID of the service principal."
        }
    }
}

parameters_schema = {
    "$id": "http://azure-ml.com/schemas/deploy.json",
    "$schema": "http://json-schema.org/schema",
    "title": "aml-registermodel",
    "description": "JSON specification for your deploy details",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name to give the deployed service.",
            "minLength": 3,
            "maxLength": 32
        },
        "deployment_compute_target": {
            "type": "string",
            "description": "Name of the compute target to deploy the webservice to."
        },
        "inference_source_directory": {
            "type": "string",
            "description": "The path to the folder that contains all files to create the image."
        },
        "inference_entry_script": {
            "type": "string",
            "description": "The path to a local file in your repository that contains the code to run for the image and score the data."
        },
        "test_enabled": {
            "type": "boolean",
            "description": "Whether to run tests for this model deployment and the created real-time endpoint."
        },
        "test_file_path": {
            "type": "string",
            "description": "Path to the python script in your repository in which you define your own tests that you want to run against the webservice endpoint."
        },
        "test_file_function_name": {
            "type": "string",
            "description": "Name of the function in your python script in your repository in which you define your own tests that you want to run against the webservice endpoint."
        },
        "conda_file": {
            "type": "string",
            "description": "The path to a local file in your repository containing a conda environment definition to use for the image."
        },
        "extra_docker_file_steps": {
            "type": "string",
            "description": "The path to a local file in your repository containing additional Docker steps to run when setting up image."
        },
        "enable_gpu": {
            "type": "boolean",
            "description": "Indicates whether to enable GPU support in the image."
        },
        "cuda_version": {
            "type": "string",
            "description": "The Version of CUDA to install for images that need GPU support."
        },
        "model_data_collection_enabled": {
            "type": "boolean",
            "description": "Whether or not to enable model data collection for this Webservice."
        },
        "authentication_enabled": {
            "type": "boolean",
            "description": "Whether or not to enable key auth for this Webservice."
        },
        "app_insights_enabled": {
            "type": "boolean",
            "description": "Whether or not to enable Application Insights logging for this Webservice."
        },
        "runtime": {
            "type": "string",
            "description": "The runtime to use for the image.",
            "pattern": "python|spark-py"
        },
        "custom_base_image": {
            "type": "string",
            "description": "A custom Docker image to be used as base image."
        },
        "profiling_enabled": {
            "type": "boolean",
            "description": "Whether or not to profile this model for an optimal combination of cpu and memory."
        },
        "profiling_dataset": {
            "type": "string",
            "description": "The name of the dataset that should be used for profiling."
        },
        "cpu_cores": {
            "type": "number",
            "description": "The number of CPU cores to allocate for this Webservice.",
            "exclusiveMinimum": 0.0
        },
        "memory_gb": {
            "type": "number",
            "description": "The amount of memory (in GB) to allocate for this Webservice.",
            "exclusiveMinimum": 0.0
        },
        "delete_service_after_deployment": {
            "type": "boolean",
            "description": "Indicates whether the service gets deleted after the deployment completed successfully."
        },
        "skip_deployment": {
            "type": "boolean",
            "description": "Indicates whether the deployment to ACI or AKS should be skipped. This can be used in combination with `create_image` to only create a Docker image that can be used for further deployment."
        },
        "create_image": {
            "type": "string",
            "description": "Indicates whether a Docker image should be created which can be used for further deployment.",
            "pattern": "docker|function_blob|function_http|function_service_bus_queue"
        },
        "tags": {
            "type": "object",
            "description": "Dictionary of key value tags to give this Webservice."
        },
        "properties": {
            "type": "object",
            "description": "Dictionary of key value properties to give this Webservice."
        },
        "description": {
            "type": "string",
            "description": "A description to give this Webservice and image."
        },
        "location": {
            "type": "string",
            "description": "The Azure region to deploy this Webservice to."
        },
        "ssl_enabled": {
            "type": "boolean",
            "description": "Whether or not to enable SSL for this Webservice."
        },
        "ssl_cert_pem_file": {
            "type": "string",
            "description": "A file path to a file containing cert information for SSL validation."
        },
        "ssl_key_pem_file": {
            "type": "string",
            "description": "A file path to a file containing key information for SSL validation."
        },
        "ssl_cname": {
            "type": "string",
            "description": "A CName to use if enabling SSL validation on the cluster."
        },
        "dns_name_label": {
            "type": "string",
            "description": "The DNS name label for the scoring endpoint."
        },
        "gpu_cores": {
            "type": "integer",
            "description": "The number of GPU cores to allocate for this Webservice.",
            "minimum": 0
        },
        "autoscale_enabled": {
            "type": "boolean",
            "description": "Whether to enable autoscale for this Webservice."
        },
        "autoscale_min_replicas": {
            "type": "integer",
            "description": "The minimum number of containers to use when autoscaling this Webservice.",
            "minimum": 1
        },
        "autoscale_max_replicas": {
            "type": "integer",
            "description": "The maximum number of containers to use when autoscaling this Webservice.",
            "minimum": 1
        },
        "autoscale_refresh_seconds": {
            "type": "integer",
            "description": "How often the autoscaler should attempt to scale this Webservice (in seconds).",
            "minimum": 1
        },
        "autoscale_target_utilization": {
            "type": "integer",
            "description": "The target utilization (in percent out of 100) the autoscaler should attempt to maintain for this Webservice.",
            "minimum": 1,
            "maximum": 100
        },
        "scoring_timeout_ms": {
            "type": "integer",
            "description": "A timeout in ms to enforce for scoring calls to this Webservice.",
            "minimum": 1
        },
        "replica_max_concurrent_requests": {
            "type": "integer",
            "description": "The number of maximum concurrent requests per replica to allow for this Webservice.",
            "minimum": 1
        },
        "max_request_wait_time": {
            "type": "integer",
            "description": "The maximum amount of time a request will stay in the queue (in milliseconds) before returning a 503 error.",
            "minimum": 0
        },
        "num_replicas": {
            "type": "integer",
            "description": "The number of containers to allocate for this Webservice."
        },
        "period_seconds": {
            "type": "integer",
            "description": "How often (in seconds) to perform the liveness probe.",
            "minimum": 1
        },
        "initial_delay_seconds": {
            "type": "integer",
            "description": "The number of seconds after the container has started before liveness probes are initiated.",
            "minimum": 1
        },
        "timeout_seconds": {
            "type": "integer",
            "description": "The number of seconds after which the liveness probe times out.",
            "minimum": 1
        },
        "success_threshold": {
            "type": "integer",
            "description": "The minimum consecutive successes for the liveness probe to be considered successful after having failed.",
            "minimum": 1
        },
        "failure_threshold": {
            "type": "integer",
            "description": "When a Pod starts and the liveness probe fails, Kubernetes will try failureThreshold times before giving up.",
            "minimum": 1
        },
        "namespace": {
            "type": "string",
            "description": "The Kubernetes namespace in which to deploy this Webservice.",
            "maxLength": 63,
            "pattern": "([a-z0-9-])+"
        },
        "token_auth_enabled": {
            "type": "boolean",
            "description": "Whether to enable Token authentication for this Webservice."
        }
    }
}
