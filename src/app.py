from flask import Flask, render_template, request
import logging
from service.camunda_service import CamundaService
from dotenv import load_dotenv, find_dotenv
import os
import time
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

PROCESS_MODEL = "Process_AnimalImageRetrieval"
SERVICE_TASK_JOB_TYPE = "retrieve-animal-imag"
INPUT_ANIMAL_VAR = "animal"
OUTPUT_ANIMAL_URL_VAR = "animal_url"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        selected_animal = request.form.get('animal')

        app.logger.info(selected_animal)

        camunda_service = initialise_camunda_service()

        app.logger.info(f"{camunda_service.base_url}")
        
        camunda_service.get_token()
        
        process_instance_key = camunda_service.create_process_instance(process_model=PROCESS_MODEL, variables={INPUT_ANIMAL_VAR: selected_animal})
        
        # time.sleep(10)
        
        # # camunda_service.get_process_instance(process_instance_key)
        
        # job_key = camunda_service.search_jobs(process_instance_key=process_instance_key, service_task_job_type=SERVICE_TASK_JOB_TYPE)
        
        # camunda_service.activate_jobs(service_task_job_type=SERVICE_TASK_JOB_TYPE, timeout=60000, max_jobs_to_activate=5)

        # camunda_service.get_variable(process_instance_key=process_instance_key)
        
        # camunda_service.complete_job(job_key)

        camunda_service.get_variable(process_instance_key=process_instance_key, variable_name=INPUT_ANIMAL_VAR)

        # variables = {
        #     "jobs": [
        #         {
        #             "type": "mammal",
        #             "processDefinitionId": "Process_AnimalImageRetrieval",
        #             "processDefinitionVersion": 2,
        #             "elementId": "ServiceTask_RetrieveAnimalImage",
        #             "customHeaders": {},
        #             "worker": "",
        #             "retries": 3,
        #             "deadline": 1766073423010,
        #             "animal": "fox",
        #             "tenantId": "<default>",
        #             "jobKey": "4503599627485109",
        #             "processInstanceKey": "4503599627485102",
        #             "processDefinitionKey": "2251799813781705",
        #             "elementInstanceKey": "4503599627485107",
        #             "kind": "BPMN_ELEMENT",
        #             "listenerEventType": "UNSPECIFIED"
        #         },
        #         {
        #             "type": "bird",
        #             "processDefinitionId": "Process_AnimalImageRetrieval",
        #             "processDefinitionVersion": 2,
        #             "elementId": "ServiceTask_RetrieveAnimalImage",
        #             "customHeaders": {},
        #             "worker": "",
        #             "retries": 3,
        #             "deadline": 1766073423010,
        #             "animal": "duck",
        #             "tenantId": "<default>",
        #             "jobKey": "4503599627485109",
        #             "processInstanceKey": "4503599627485102",
        #             "processDefinitionKey": "2251799813781705",
        #             "elementInstanceKey": "4503599627485107",
        #             "kind": "BPMN_ELEMENT",
        #             "listenerEventType": "UNSPECIFIED"
        #         }
        #     ]
        # }

        # filtered_data = [job for job in variables["jobs"] if job["type"] == "mammal" ]
        # logging.info(json.dumps(filtered_data, indent=4))
        # logging.info(filtered_data[0]["animal"])

        return render_template('index.html', complete=True, animal_url="https:\/\/randomfox.ca\/images\/114.jpg")
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

