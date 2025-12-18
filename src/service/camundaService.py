"""
Docstring for AnimalImageApp.src.service.camunda_service
"""

import requests
from urllib.parse import urlencode
import json
import os
from dotenv import load_dotenv, find_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, # Set the desired log level
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()] # Output logs to console
)

class CamundaService:

    TOKEN_TIMEOUT = 3600
    PROCESS_MODEL = "Process_AnimalImageRetrieval"

    def __init__(self, animal: str):
        self.base_url = None
        self.token_audience = None
        self.client_id = None
        self.client_secret = None
        self.auth_url = None
        self.animal = animal

    def setup(self):

        load_dotenv()

        self.base_url = os.getenv('ZEEBE_REST_ADDRESS')
        self.token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE')
        self.client_id = os.getenv('CAMUNDA_CLIENT_ID')
        self.client_secret = os.getenv('CAMUNDA_CLIENT_SECRET')
        self.auth_url = os.getenv('CAMUNDA_OAUTH_URL')
        self.access_token = None
        self.process_instance_key = None

    def get_token(self):
        
        payload = {
            "grant_type": "client_credentials",
            "audience": self.token_audience,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        logging.info(payload)

        response = requests.post(
            url=self.auth_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=payload
        )

        if response is None:
            raise Exception(f"Failed to get a response.")

        if response.status_code != 200:
            raise Exception(f'Failed to successfully complete. Status Code: {response.status_code}. Response: {response.text}')
        
        access_token = response.json().get("access_token")
        self.access_token = access_token

    def search_process_definitions(self):

        process_definition_search_url = f"{self.base_url}/v2/process-definitions/search"

        headers = {
            "Content-Type": "application/json",
            "Accept":"application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        logging.info(headers)

        # payload = json.dumps({
        #     "processDefinitionId": CamundaService.PROCESS_MODEL,
        #     "variables": { "animal" : f"{self.animal}" }
        # })

        response = requests.post(
            url=process_definition_search_url,
            headers=headers
        )

        if response is None:
            raise Exception(f"Failed to get a response.")

        if response.status_code != 200:
            raise Exception(f'Failed to successfully complete. Status Code: {response.status_code}. Response: {response.text}')
        
        logging.info(response.json())
        # self.process_instance_key = process_instance_key

    def create_process_instance(self):

        processCreationUrl = f"{self.base_url}/v2/process-instances"

        headers = {
            "Content-Type": "application/json",
            "Accept":"application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        logging.info(headers)

        payload = json.dumps({
            "processDefinitionId": CamundaService.PROCESS_MODEL,
            "variables": { "animal" : f"{self.animal}" }
        })

        response = requests.post(
            url=processCreationUrl,
            headers=headers,
            data=payload
        )

        if response is None:
            raise Exception(f"Failed to get a response.")

        if response.status_code != 200:
            raise Exception(f'Failed to successfully complete. Status Code: {response.status_code}. Response: {response.text}')
        
        process_instance_key = response.json().get("processInstanceKey")
        self.process_instance_key = process_instance_key

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