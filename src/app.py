from flask import Flask, render_template, request
import logging
from service.camunda_service import CamundaService
from dotenv import load_dotenv, find_dotenv
import os
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

PROCESS_MODEL = "Process_AnimalImageRetrieval"
SERVICE_TASK_JOB_TYPE = "retrieve-animal-imag"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        camunda_service = initialise_camunda_service()

        app.logger.info(f"{camunda_service.base_url}")
        
        camunda_service.get_token()
        
        process_instance_key = camunda_service.create_process_instance(process_model=PROCESS_MODEL, variables={"animal": "fox"})
        
        time.sleep(10)
        
        camunda_service.get_process_instance(process_instance_key)
        
        job_key = camunda_service.search_jobs(process_instance_key=process_instance_key, service_task_job_type=SERVICE_TASK_JOB_TYPE)
        
        camunda_service.activate_jobs(service_task_job_type=SERVICE_TASK_JOB_TYPE, timeout=60000, max_jobs_to_activate=5)
        
        camunda_service.complete_job(job_key)

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

