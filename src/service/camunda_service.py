import ast
import json
import logging
import requests

REQUEST_JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

logger = logging.getLogger(__name__)

class CamundaService:

    def __init__(self, base_url: str, token_audience: str, client_id: str, client_secret: str, auth_url: str):

        self.base_url = base_url
        self.token_audience = token_audience
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.access_token = ""


    def get_token(self):
        """
        Gets access token.
        """

        payload = {
            "grant_type": "client_credentials",
            "audience": self.token_audience,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        # ensure that the token does not already have a value
        self.access_token = ""

        try:
            response = requests.post(
                url=self.auth_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=payload
            )

            if response.ok:
                access_token = response.json().get("access_token")
                self.access_token = access_token
            else:
                logger.error("%s -> Failed to authenticate. Status Code: %s. Response: %s", logger.name, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, self.auth_url, str(exception))


    def get_cluster_topology(self) -> bool | None:
        """
        Gets the cluster topology. This method is used to valid whether the access token is still valid.

        Returns:
            bool | None: True if access token is valid else False. None if could not connect to API service.
        """

        request_url = f"{self.base_url}/v2/topology"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url=request_url, headers=headers)

            if response.ok:
                return True
            else:
                logger.error("%s -> Failed to get cluster topology'. Status Code: %s. Response: %s", logger.name, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return False


    def deploy_resources(self, resource_paths: list[str]) -> str:
        """
        Deploys one or more resources (e.g. processes, decision models, or forms).

        Args:
            resource_paths (list[str]): List of relative paths of deployment resource files.

        Returns:
            str: Unique identifier of the deployment.
        """

        request_url = f"{self.base_url}/v2/deployments"

        headers = { "Authorization": f"Bearer {self.access_token}" }

        files = []

        # get binary data for all deployment resources
        for file_path in resource_paths:
            files.append(
                ('resources', (file_path, open(file_path, 'rb'), 'application/octet-stream'))
            )

        logger.debug("%s -> Files being deployed: %s", logger.name, files)

        payload = {}

        try:
            response = requests.post(url=request_url, headers=headers, data=payload, files=files)

            if response.ok:
                logger.debug("%s -> %s - {json.dumps(response.json(), indent=4)}", logger.name, request_url)

                return response.json().get("deploymentKey")
            else:
                logger.error("%s -> Failed to deploy resources '%s'. Status Code: %s. Response: %s", logger.name, resource_paths, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return ""


    def create_process_instance(self, process_model: str, variables: str) -> str:
        """
        Creates and starts an instance of the specified process.

        Args:
            process_model (str): BPMN process ID of the process definition
            variables (str): JSON object that will instantiate the variables for the root variable scope of the process instance.

        Returns:
            str: Unique identifier of the created process instance.
        """

        request_url = f"{self.base_url}/v2/process-instances"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "processDefinitionId": process_model,
            "variables": variables
        })

        try:
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            if response.ok:
                logger.debug("%s -> %s - %s", logger.name, request_url, json.dumps(response.json(), indent=4))

                return response.json().get("processInstanceKey")
            else:
                logger.error("%s -> Failed to create process instance. Status Code: %s. Response: %s", logger.name, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return ""


    def get_process_instance(self, process_instance_key: str):
        """
        Get the process instance by the process instance key.

        Args:
            process_instance_key (str): Process instance key.
        """

        request_url = f"{self.base_url}/v2/process-instances/{process_instance_key}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(
                url=request_url,
                headers=headers
            )

            if response.ok:
                logger.debug("%s -> %s - %s", logger.name, request_url, json.dumps(response.json(), indent=4))
            else:
                logger.error("%s -> Failed to get process instance '%s'. Status Code: %s. Response: %s",
                             logger.name, process_instance_key, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))


    def search_jobs(self, process_instance_key: str, service_task_job_type: str) -> str:
        """
        Search for jobs based on process instance key and job type.

        Args:
            process_instance_key (str): Process instance key associated with the job.
            service_task_job_type (str): Type of the job.

        Returns:
            str: Unique identifier for the job.
        """

        request_url = f"{self.base_url}/v2/jobs/search"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "filter": {
                "processInstanceKey": f"{process_instance_key}",
                "type": f"{service_task_job_type}"
            }
        })

        logger.info("%s -> payload for job search: %s", logger.name, payload)

        try:
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            if response.ok:
                logger.debug("%s -> %s - %s", logger.name, request_url, json.dumps(response.json(), indent=4))
                jobs = response.json().get("items")

                if len(jobs) > 0:
                    return jobs[0].get("jobKey")
            else:
                logger.error("%s -> Failed to search for job of type '%s' for process instance '%s'. Status Code: %s. Response: %s",
                             logger.name, service_task_job_type, process_instance_key, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return ""


    def activate_jobs(self, service_task_job_type: str, timeout: int, max_jobs_to_activate: int) -> list:
        """
        Activate jobs based on the job type.

        Args:
            service_task_job_type (str): Job type, as defined in the BPMN process.
            timeout (int): Timeout period for which the activated jobs will not be activated by another activation call.
            max_jobs_to_activate (int): Maximum jobs to activate by this request.

        Returns:
            list: List of jobs
        """

        request_url = f"{self.base_url}/v2/jobs/activation"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "type": service_task_job_type,
            "timeout": timeout,
            "maxJobsToActivate": max_jobs_to_activate
        })

        try:
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            if response.ok:
                logger.info("%s -> %s - %s", logger.name, request_url, json.dumps(response.json(), indent=4))

                return response.json().get("jobs")
            else:
                logger.error("%s -> Failed to activate '%s' jobs. Status Code: %s. Response: %s", logger.name, service_task_job_type, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))
        
        return []


    def complete_job(self, job_key: str, variables: str) -> bool:
        """
        Complete the job for the service task.

        Args:
            job_key (str): Key of the job handling the service task.
            variables (str): JSON string of variables to complete the job with.

        Returns:
            bool: True if the job was successfully marked as complete.
        """

        request_url = f"{self.base_url}/v2/jobs/{job_key}/completion"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "variables": variables
        })

        try:
            # complete the job
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            # if the job is successfully completed, return True
            if response.ok:
                logger.info("%s -> Job completed: %s", logger.name, job_key)

                return True
            else:
                logger.error("%s -> Failed to complete job '%s'. Status Code: %s. Response: %s", logger.name, job_key, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return False


    def fail_job(self, job_key:str, error_message: str) -> bool:
        """
        Fail the job for the service task.

        Args:
            job_key (str): The key of the job to fail.
            error_message (str): An optional message describing why the job failed.

        Returns:
            bool: True if the job was successfully failed.
        """

        request_url = f"{self.base_url}/v2/jobs/{job_key}/failure"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "errorMessage": f"Job {job_key} failed: {error_message}"
        })

        try:
            # fail the job
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            # if the job is successfully marked as failed, return True
            if response.ok:
                logger.info("%s -> Job failed: %s", logger.name, job_key)

                return True
            else:
                logger.error("%s -> Failed to mark the job '%s' as failed. Status Code: %s. Response: %s", logger.name, job_key, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return False


    def throw_error_job(self, job_key: str, error_code: str, error_message: str):
        """
        Throw a business error for the job.

        Args:
            job_key (str): The key of the job to throw an error for.
            error_code (str): The error code that will be matched with an error catch event.
            error_message (str): An error message that provides additional context.

        Returns:
            bool: True if the business error was successfully thrown.
        """

        request_url = f"{self.base_url}/v2/jobs/{job_key}/error"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "errorCode": error_code,
            "errorMessage": f"Job {job_key} has thrown error: {error_message}",
            "variables": {
                "errorCode": error_code,
                "errorMessage": f"Job {job_key} has thrown error: {error_message}"
            }
        })

        logger.debug("payload: %s", payload)

        try:
            # throw a business error for the job
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            # if the error is successfully thrown, return True
            if response.ok:
                logger.info("%s -> Error thrown for job: %s", logger.name, job_key)

                return True
            else:
                logger.error("%s -> Failed to throw error for the job '%s'. Status Code: %s. Response: %s", logger.name, job_key, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return False


    def get_variable(self, process_instance_key: str, variable_name: str) -> str:
        """
        Get the variable by the variable key.

        Args:
            process_instance_key (str): Key of the process instance of variable.
            variable_name (str): Name of variable.

        Returns:
            str: Variable value
        """

        request_url = f"{self.base_url}/v2/variables/search"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "filter": {
                "name": variable_name,
                "processInstanceKey": process_instance_key,
                "scopeKey": process_instance_key
            },
            "page": {
                "from": 0,
                "limit": 1
            }
        })

        try:
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            if response.ok:
                variables = response.json().get("items")

                logger.debug("%s -> %s - %s", logger.name, request_url, json.dumps(variables, indent=4))

                if len(variables) > 0:

                    variable_value = variables[0].get("value")

                    # if the variable value is returned as a variable in quotes, strip them out so that a literal is returned
                    if variable_value.startswith("\"") and variable_value.endswith("\""):
                        variable_value = ast.literal_eval(variable_value)

                    return variable_value
            else:
                logger.error("%s -> Failed to get variables for process instance '%s'. Status Code: %s. Response: %s",
                             logger.name, process_instance_key, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, request_url, str(exception))

        return ""
