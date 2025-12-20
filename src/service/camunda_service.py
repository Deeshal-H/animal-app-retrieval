from urllib.parse import urlencode
import json
import logging
import requests
import os
import time
from service.animal_api_service import AnimalService
import ast

REQUEST_JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

logger = logging.getLogger(__name__)

class CamundaService:

    def __init__(self):
        self.base_url = None
        self.token_audience = None
        self.client_id = None
        self.client_secret = None
        self.auth_url = None


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
                logger.error(f"{logger.name} -> Failed to authenticate. Status Code: {response.status_code}. Response: {response.text}")
    
        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{self.auth_url}' -> {str(exception)}")


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
                logger.error(f"{logger.name} -> Failed to get cluster topology'. Status Code: {response.status_code}. Response: {response.text}")

                return False
        
        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}' -> {str(exception)}")


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

        logger.debug(f"{logger.name} -> Files being deployed: {files}")

        payload = {}

        try:
            response = requests.post(url=request_url, headers=headers, data=payload, files=files)

            if response.ok:
                logger.debug(f"{logger.name} -> {request_url} - {json.dumps(response.json(), indent=4)}")

                return response.json().get("deploymentKey")
            else:
                logger.error(f"{logger.name} -> Failed to deploy resources '{resource_paths}'. Status Code: {response.status_code}. Response: {response.text}")
        
        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}' -> {str(exception)}")


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
                logger.debug(f"{logger.name} -> {request_url} - {json.dumps(response.json(), indent=4)}")
        
                return response.json().get("processInstanceKey")
            else:
                logger.error(f"{logger.name} -> Failed to create process instance. Status Code: {response.status_code}. Response: {response.text}")
        
        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}' -> {str(exception)}")


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
                logger.debug(f"{logger.name} -> {request_url} - {json.dumps(response.json(), indent=4)}")
            else:
                logger.error(f"{logger.name} -> Failed to get process instance '{process_instance_key}''. Status Code: {response.status_code}. Response: {response.text}")

        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}] -> {str(exception)}")


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

        logger.info(f"{logger.name} -> payload for job search: {payload}")

        try:
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            if response.ok:
                logger.debug(f"{logger.name} -> {request_url} - {json.dumps(response.json(), indent=4)}")
                jobs = response.json().get("items")

                # TODO: move the jobs array length check logic to the application layer. This method should return the matching jobs array.
                #       return the key for the first job retrieved as there will be one job of this type associated with the process instance 
                if len(jobs) > 0:
                    return jobs[0].get("jobKey")
            else:
                logger.error(f"{logger.name} -> Failed to search for job of type '{service_task_job_type}' for process instance '{process_instance_key}'. \
                                Status Code: {response.status_code}. Response: {response.text}")
        
        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}' -> {str(exception)}")
        except exception:
            logger.error(f"{logger.name} -> Error '{request_url}' -> {str(exception)}")


    def activate_jobs(self, service_task_job_type: str, timeout: int, max_jobs_to_activate: int):
        """
        Activate jobs based on the job type.

        Args:
            service_task_job_type (str): Job type, as defined in the BPMN process.
            timeout (int): Timeout period for which the activated jobs will not be activated by another activation call.
            max_jobs_to_activate (int): Maximum jobs to activate by this request.
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
                logger.info(f"{logger.name} -> {request_url} - {json.dumps(response.json(), indent=4)}")
            else:
                logger.error(f"{logger.name} -> Failed to activate '{service_task_job_type}' jobs. Status Code: {response.status_code}. Response: {response.text}")

        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}' -> {str(exception)}")


    def complete_job(self, job_key: str, animal: str) -> str:
        """
        Complete the job for the service task after retrieving the animal image url

        Args:
            job_key (str): Key of the job handling the service task.
            animal (str): Animal for which to retrieve image url.

        Returns:
            str: Image url for the animal selected.
        """

        # get an image url based for the animal
        animal_service = AnimalService()
        animal_image_url = animal_service.get_animal_url(animal=animal)
        logger.info(f"{logger.name} -> Retrieved URL for animal image {animal}: {animal_image_url}")

        request_url = f"{self.base_url}/v2/jobs/{job_key}/completion"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = json.dumps({
            "variables": { "animal_url": animal_image_url }
        })

        try:
            # complete the job
            response = requests.post(
                url=request_url,
                headers=headers,
                data=payload
            )

            # if the job is successfully completed, return the animal image url
            if response.ok:
                logger.info(f"{logger.name} -> Job completed: {job_key}")

                return animal_image_url
            else:
                logger.error(f"{logger.name} -> Failed to complete job '{job_key}'. Status Code: {response.status_code}. Response: {response.text}")
        
        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}' -> {str(exception)}")


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
                
                logger.debug(f"{logger.name} -> {request_url} - {json.dumps(variables, indent=4)}")

                # filtered_variables = [var for var in variables if var["name"] == variable_name ]

                if len(variables) > 0:

                    variable_value = variables[0].get("value")
 
                    # if the variable value is returned as a variable in quotes, strip them out so that a literal is returned 
                    if variable_value.startswith("\"") and variable_value.endswith("\""):
                        variable_value = ast.literal_eval(variable_value)

                    return variable_value
            else:
                logger.error(f"{logger.name} -> Failed to get variables for process instance '{process_instance_key}'. Status Code: {response.status_code}. Response: {response.text}")
        
        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{request_url}' -> {str(exception)}")