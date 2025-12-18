import requests
from urllib.parse import urlencode
import json
import os
import logging

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

def main():

    # data = {
    #     "grant_type":"client_credentials",
    #     "audience":"zeebe.camunda.io",
    #     "client_id":"F-7-8s0.Bw3Vji7OlJiXzLxvKgxFGLGN",
    #     "client_secret":"gLwyE~qJ5WErO~RXqQt0I5aQaWGw7x8k_4.6szM8lwhDJeWV~i_9pGIr20UU4REP"
    # }

    # response = requests.post(url='https://login.cloud.camunda.io/oauth/token',
    #                         headers={"Content-Type": "application/x-www-form-urlencoded"},
    #                         data=data)
    
    # if response is None:
    #     raise Exception(f"Failed to get a response.")

    # if response.status_code != 200:
    #     raise Exception(f'Failed to extract data. Status Code: {response.status_code}. Response: {response.text}')
    
    # # print(response.json())
    # access_token = response.json().get("access_token")

    # print(access_token)
    # print(os.linesep)

    # job_url = "https://syd-1.zeebe.camunda.io:443/7a12d381-80a3-4a0d-a86c-31cba730f5bb/v2/jobs/activation"
    processSearchUrl = "https://syd-1.zeebe.camunda.io:443/7a12d381-80a3-4a0d-a86c-31cba730f5bb/v2/process-instances/search"

    headers = {
        "Content-Type": "application/json",
        "Accept":"application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFVVXdPVFpDUTBVM01qZEVRME0wTkRFelJrUkJORFk0T0RZeE1FRTBSa1pFUlVWRVF6bERNZyJ9.eyJodHRwczovL2NhbXVuZGEuY29tL2NsdXN0ZXJJZCI6IjdhMTJkMzgxLTgwYTMtNGEwZC1hODZjLTMxY2JhNzMwZjViYiIsImh0dHBzOi8vY2FtdW5kYS5jb20vb3JnSWQiOiJlYjQyZjEwZS1lNTQ2LTQ1NWUtOGM4MS1hY2IzNmY4MjNmMGUiLCJodHRwczovL2NhbXVuZGEuY29tL2NsaWVudElkIjoiRi03LThzMC5CdzNWamk3T2xKaVh6THh2S2d4RkdMR04iLCJpc3MiOiJodHRwczovL3dlYmxvZ2luLmNsb3VkLmNhbXVuZGEuaW8vIiwic3ViIjoibXdvOTB0MnIzMTYwN3ozNkJOSDY5dFdGS0JYNTVqMVdAY2xpZW50cyIsImF1ZCI6InplZWJlLmNhbXVuZGEuaW8iLCJpYXQiOjE3NjU4NTY3OTAsImV4cCI6MTc2NTk0MzE5MCwic2NvcGUiOiI3YTEyZDM4MS04MGEzLTRhMGQtYTg2Yy0zMWNiYTczMGY1YmIiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJtd285MHQycjMxNjA3ejM2Qk5INjl0V0ZLQlg1NWoxVyJ9.MxQGQXuvu007MyShAJwj6xt-PMPHXSVuW6vsdnV5icBuV-sVhtU5w3dFAGvAe323rMM1NLEKr_Yp4wiT1nctwz7doTE-_GOZk9dJklMH8enicySmejUqJoTMtyURThgyNPEMc5ssoSigxVSlDjQ2Brrcv8W4L8DmCEhl7CHZQRmgbckndE_V4kWiCn8JKYYDSWq-r3OvdYS8AeYyNJQ_JhHXv0rX1DLTLpd3mMcH47muWRd5Z0s1tA5QKdRFR--xCtixTfHDnlq7qh1I_pR0SbERSKk3agRmKw0tb2CD9FD_Fr9QmFKHVpPTCtiaFvJHegLnNpIcThGumsO6uMzxIg"
    }

    data = json.dumps({
        "type": "call-api",
        "worker": "worker-324",
        "timeout": 20000,
        "maxJobsToActivate": 1,
        "fetchVariable": ["animal"]
    })

    print(headers)
    print(os.linesep)

    processSearchResponse = requests.post(url=processSearchUrl,
                  headers=headers)
    
    print(processSearchResponse)
    print(json.dumps(processSearchResponse.json(), indent=4))
    print(os.linesep)

    processInstanceUrl = "https://syd-1.zeebe.camunda.io:443/7a12d381-80a3-4a0d-a86c-31cba730f5bb/v2/process-instances/4503599627497423"

    processInstanceResponse = requests.get(url=processInstanceUrl,
                 headers=headers)

    print(processInstanceResponse)
    print(json.dumps(processInstanceResponse.json(), indent=4))
    print(os.linesep)

    jobResponse = requests.post(url="https://syd-1.zeebe.camunda.io:443/7a12d381-80a3-4a0d-a86c-31cba730f5bb/v2/jobs/search",
                  headers=headers)
    
    print(jobResponse)
    print(json.dumps(jobResponse.json(), indent=4))
    print(os.linesep)

    jobActivationResponse = requests.post(url="https://syd-1.zeebe.camunda.io:443/7a12d381-80a3-4a0d-a86c-31cba730f5bb/v2/jobs/activation",
                                          headers=headers,
                                          data=data)
    
    print(jobActivationResponse)
    print(json.dumps(jobActivationResponse.json(), indent=4))
    print(os.linesep)

    jobCompletionResponse = requests.post(url="https://syd-1.zeebe.camunda.io:443/7a12d381-80a3-4a0d-a86c-31cba730f5bb/v2/jobs/4503599627497429/completion",
                                          headers=headers,
                                          data=json.dumps({ "variables": {"animal": "cat"} }))
    
    print(jobCompletionResponse)
    # print(json.dumps(jobCompletionResponse.json(), indent=4))
    print(jobCompletionResponse.json())

class JobWorkerClient:

    def __init__(self):
        pass