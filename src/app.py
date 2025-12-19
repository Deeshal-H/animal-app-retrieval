from flask import Flask, render_template, request
import logging
from service.camunda_service import CamundaService
from dotenv import load_dotenv, find_dotenv
import os
import time
import json
import sys
# import yaml
# from pathlib import Path

PROCESS_MODEL = "Process_AnimalImageRetrieval"
SERVICE_TASK_JOB_TYPE = "retrieve-animal-imag"
INPUT_ANIMAL_VAR = "animal"
OUTPUT_ANIMAL_URL_VAR = "animal_url"

 # Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()
        # ,logging.FileHandler(f"./src/logs/logs_{time.strftime('%Y%m%d_%H-00-00', time.localtime(time.time()))}.txt", mode='a')
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        logger.info(get_source_path("assets/Animal Image Retrieval.bpmn"))
        logger.info(get_source_path("app.yaml"))

        selected_animal = request.form.get('animal')

        logger.info(selected_animal)

        camunda_service = initialise_camunda_service()

        logger.info(f"{camunda_service.base_url}")
        
        # camunda_service.get_token()

        camunda_service.access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFVVXdPVFpDUTBVM01qZEVRME0wTkRFelJrUkJORFk0T0RZeE1FRTBSa1pFUlVWRVF6bERNZyJ9.eyJodHRwczovL2NhbXVuZGEuY29tL2NsdXN0ZXJJZCI6IjdhMTJkMzgxLTgwYTMtNGEwZC1hODZjLTMxY2JhNzMwZjViYiIsImh0dHBzOi8vY2FtdW5kYS5jb20vb3JnSWQiOiJlYjQyZjEwZS1lNTQ2LTQ1NWUtOGM4MS1hY2IzNmY4MjNmMGUiLCJodHRwczovL2NhbXVuZGEuY29tL2NsaWVudElkIjoiRi03LThzMC5CdzNWamk3T2xKaVh6THh2S2d4RkdMR04iLCJpc3MiOiJodHRwczovL3dlYmxvZ2luLmNsb3VkLmNhbXVuZGEuaW8vIiwic3ViIjoibXdvOTB0MnIzMTYwN3ozNkJOSDY5dFdGS0JYNTVqMVdAY2xpZW50cyIsImF1ZCI6InplZWJlLmNhbXVuZGEuaW8iLCJpYXQiOjE3NjYwNzMzNDksImV4cCI6MTc2NjE1OTc0OSwic2NvcGUiOiI3YTEyZDM4MS04MGEzLTRhMGQtYTg2Yy0zMWNiYTczMGY1YmIiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJtd285MHQycjMxNjA3ejM2Qk5INjl0V0ZLQlg1NWoxVyJ9.Uzfcho5SWsedphhVaDxm6TCBws2gTZueaKLCOo3zSl8w_pAvi1XTRnsidahsc_6fynsaI5jgksQDz4V60UOuqU87bjbbmamrBKBLFUMOHkzjkqTEJcyvabW1OCZ09cWcS36-G4cWQxmh1k63sehEHFykoeWAEfrFXVGCEWUGQ5sQrOid0Zy-cCVEzlqoINDznOXOBjSlpE__9o2VLvdFaf6xzFTp27eVDoByEMN_JQj3pUuZt-SjMDSgkRno_mPE2ZkNoSWZn67O3qFWyQkRVf76EkiE5Gt2JPaq8da3M3I9kPWnqvutDvq5FfscEWq7bam8mex29lF1UgL9z1R9YQ"

        resource_files = os.listdir("assets")
        resource_paths = ['assets/' + file for file in resource_files]

        logger.info(f"resource_paths: {resource_paths}")

        # camunda_service.deploy_resources(resource_paths)
        
        # process_instance_key = camunda_service.create_process_instance(process_model=PROCESS_MODEL, variables={INPUT_ANIMAL_VAR: selected_animal})
        
        # time.sleep(10)
        
        # camunda_service.get_process_instance(process_instance_key)
        
        # job_key = camunda_service.search_jobs(process_instance_key=process_instance_key, service_task_job_type=SERVICE_TASK_JOB_TYPE)

        # animal_var = camunda_service.get_variable(process_instance_key=process_instance_key, variable_name=INPUT_ANIMAL_VAR)

        # logger.info(f"Retrieved variable {INPUT_ANIMAL_VAR} -> [{animal_var}]")
        
        # camunda_service.activate_jobs(service_task_job_type=SERVICE_TASK_JOB_TYPE, timeout=60000, max_jobs_to_activate=5)
        
        # camunda_service.complete_job(job_key)

        return render_template('index.html', complete=True, animal_url="https://randomfox.ca/images/114.jpg")
    else:
        return render_template('index.html')


def initialise_camunda_service() -> CamundaService:

    load_dotenv()

    camunda_service = CamundaService()

    camunda_service.base_url = os.getenv('ZEEBE_REST_ADDRESS')
    camunda_service.token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE')
    camunda_service.client_id = os.getenv('CAMUNDA_CLIENT_ID')
    camunda_service.client_secret = os.getenv('CAMUNDA_CLIENT_SECRET')
    camunda_service.auth_url = os.getenv('CAMUNDA_OAUTH_URL')

    return camunda_service

# def get_config():

#     # retrieve config values from yaml file
#     yaml_file_path = __file__.replace(".py", ".yaml")

#     if Path(yaml_file_path).exists:
#         with open(yaml_file_path, encoding='utf-8') as yaml_file:
#             yaml_config = yaml.safe_load(yaml_file)
#     else:
#         raise Exception(f"Missing {yaml_file_path} file.")

def get_source_path(relative_path):
    if hasattr(sys,'_MEIPASS'):
        # Program is running in packaged mode
        base_path = sys._MEIPASS
    else:
        # Program is running in development mode
        base_path = os.path.abspath(".")

    return os.path.join(base_path,relative_path)

# Get the correct file path
# data_file_path = get_source_path('mydata.txt')

# with open(data_file_path, 'r') as f:
#     print(f.read())

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

