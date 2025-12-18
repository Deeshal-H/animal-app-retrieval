from urllib.parse import urlencode
import json
import logging
import requests

REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "Accept":"application/json"
}

class CamundaService:

    def __init__(self):
        self.base_url = None
        self.token_audience = None
        self.client_id = None
        self.client_secret = None
        self.auth_url = None

    def get_token(self):
        
        payload = {
            "grant_type": "client_credentials",
            "audience": self.token_audience,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

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
                logging.warning(f'Failed to authenticate. Status Code: {response.status_code}. Response: {response.text}')
    
        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{self.auth_url}] -> {str(exception)}")


    def search_process_definitions(self):

        request_url = f"{self.base_url}/v2/process-definitions/search"

        request_headers = REQUEST_HEADERS | {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.post(
                url=request_url,
                headers=request_headers
            )

            if response.ok:
                logging.info(f"{request_url} - {json.dumps(response.json(), indent=4)}")
            else:
                logging.warning(f'Failed to retrieve process definitions. Status Code: {response.status_code}. Response: {response.text}')
        
        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{request_url}] -> {str(exception)}")


    def create_process_instance(self, process_model: str, variables: str) -> str:

        request_url = f"{self.base_url}/v2/process-instances"

        request_headers = REQUEST_HEADERS | {"Authorization": f"Bearer {self.access_token}"}

        payload = json.dumps({
            "processDefinitionId": process_model,
            "variables": variables
        })

        try:
            response = requests.post(
                url=request_url,
                headers=request_headers,
                data=payload
            )

            if response.ok:
                logging.info(f"{request_url} - {json.dumps(response.json(), indent=4)}")
        
                return response.json().get("processInstanceKey")
            else:
                raise Exception(f'Failed to create process instance. Status Code: {response.status_code}. Response: {response.text}')
        
        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{request_url}] -> {str(exception)}")


    def get_process_instance(self, process_instance_key: str):

        request_url = f"{self.base_url}/v2/process-instances/{process_instance_key}"

        request_headers = REQUEST_HEADERS | {"Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.get(
                url=request_url,
                headers=request_headers
            )

            if response.ok:
                logging.info(f"{request_url} - {json.dumps(response.json(), indent=4)}")
            else:
                raise Exception(f'Failed to get process instance [{process_instance_key}]. Status Code: {response.status_code}. Response: {response.text}')

        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{request_url}] -> {str(exception)}")


    def search_jobs(self, process_instance_key: str, service_task_job_type: str) -> str:

        request_url = f"{self.base_url}/v2/jobs/search"

        request_headers = REQUEST_HEADERS | {"Authorization": f"Bearer {self.access_token}"}

        payload = json.dumps({
            "filter": {
                "processInstanceKey": f"{process_instance_key}",
                "type": f"{service_task_job_type}"
            }
        })

        try:
            response = requests.post(
                url=request_url,
                headers=request_headers,
                data=payload
            )

            if response.ok:
                jobs = response.json().get("items")
                
                logging.info(f"{request_url} - {json.dumps(jobs, indent=4)}")

                if len(jobs) > 0:
                    return jobs[0].get("jobKey")
            else:
                raise Exception(f'Failed to search for job [{service_task_job_type}] for process instance [{process_instance_key}]. \
                                Status Code: {response.status_code}. Response: {response.text}')
        
        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{request_url}] -> {str(exception)}")


    def activate_jobs(self, service_task_job_type: str, timeout: int, max_jobs_to_activate: int):

        request_url = f"{self.base_url}/v2/jobs/activation"

        request_headers = REQUEST_HEADERS | {"Authorization": f"Bearer {self.access_token}"}

        payload = json.dumps({
            "type": service_task_job_type,
            "timeout": timeout,
            "maxJobsToActivate": max_jobs_to_activate
        })

        try:
            response = requests.post(
                url=request_url,
                headers=request_headers,
                data=payload
            )
            
            if response.ok:
                logging.info(f"{request_url} - {json.dumps(response.json(), indent=4)}")
            else:
                raise Exception(f'Failed to activate [{service_task_job_type}] jobs. Status Code: {response.status_code}. Response: {response.text}')

        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{request_url}] -> {str(exception)}")


    def complete_job(self, job_key: str):

        request_url = f"{self.base_url}/v2/jobs/{job_key}/completion"

        request_headers = REQUEST_HEADERS | {"Authorization": f"Bearer {self.access_token}"}

        payload = json.dumps({
            "variables": {"animal_url": "https:\/\/randomfox.ca\/images\/114.jpg"}
        })

        try:
            response = requests.post(
                url=request_url,
                headers=request_headers,
                data=payload
            )

            if response.ok:
                logging.info(f"{request_url} - {response.text}")
            else:
                raise Exception(f'Failed to complete job [{job_key}]. Status Code: {response.status_code}. Response: {response.text}')
        
        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{request_url}] -> {str(exception)}")


    def get_variable(self, process_instance_key: str, variable_name: str) -> str:

        request_url = f"{self.base_url}/v2/variables/search"

        request_headers = REQUEST_HEADERS | {"Authorization": f"Bearer {self.access_token}"}

        payload = json.dumps({
            "filter": {
                "processInstanceKey": f"{process_instance_key}"
            }
        })

        try:
            response = requests.post(
                url=request_url,
                headers=request_headers,
                data=payload
            )

            if response.ok:
                variables = response.json().get("items")
                
                logging.info(f"{request_url} - {json.dumps(variables, indent=4)}")

                filtered_variables = [var for var in variables if var["name"] == variable_name ]

                if len(filtered_variables) > 0:
                    return filtered_variables[0]["value"]
            else:
                raise Exception(f'Failed to get variables for process instance [{process_instance_key}]. Status Code: {response.status_code}. Response: {response.text}')
        
        except requests.exceptions.RequestException as exception:
            logging.error(f"Failed to connect to [{request_url}] -> {str(exception)}")