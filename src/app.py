from flask import Flask, render_template, request, session
import logging
from service.camunda_service import CamundaService
from dotenv import load_dotenv, find_dotenv
import os
import time
import json
import sys
import yaml
from pathlib import Path
from service.animal_api_service import AnimalService

# PROCESS NAME
PROCESS_MODEL = "Process_AnimalImageRetrieval"

# NAME OF SERVICE TASK TO RETRIEVE IMAGE
SERVICE_TASK_JOB_TYPE = "retrieve-animal-image"

# NAME OF INPUT VARIABLE TO SERVICE TASK TO RETRIEVE IMAGE
INPUT_ANIMAL_VAR = "animal"

# NAME OF OUTPUT VARIABLE THAT HOLDS THE ANIMAL IMAGE URL
OUTPUT_ANIMAL_URL_VAR = "animal_url"

# Directories where the Camunda resources to be deployed are placed
ASSET_DIR = "assets"


 # Configure root-level logging.
 # For debugging purposes, this is currently set to DEBUG
 # TODO: Complete mechanism to overwrite log level based on a yaml config file
 # TODO: Add option to output to either StreamHandler or FileHandler or both
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Set the secret key to use flask session data. This is used to store the access token in a session
# TODO: Load the secret_key in an environment variable
app.secret_key = 'scorm/3o9btmgnh45l1'

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        """
        TODO: Future functionality - This section is to load config values from a file
        
        # Retrieves config values from a file named (implemented but not in use)
        config_values = get_config_values()

        # Use the log_level from the config file to override the root level logging (implemented but not in use)
        # if config_values["log_level"] is not None:
        #     override_root_level_log_level(config_values['log_level'])
        """

        animal_selected = request.form.get('animal')
        logger.info(f"Animal selected: {animal_selected}")

        camunda_service = initialise_camunda_service()
        logger.debug(f"Retrieved base url: {camunda_service.base_url}")

        logger.info(f"{session['token']}")
        
        # check if a token exists in the session and, if it does, check if it is still valid
        # TODO: Implement token refresh functionality. At the moment, a request to get the cluster topology is used to see if the token is still valid
        token_valid = False

        if session['token'] is not None:
            logger.info(f"Found token in session")
            camunda_service.access_token = session['token']        
            token_valid = camunda_service.get_cluster_topology()

            if token_valid is None: # Could not get cluster topology to check token validity
                error_message = "Failed to check for token validity or token invalid."
                logger.error(error_message)
                return render_template('index.html', show_error_message=True, error_message=error_message)
            elif not token_valid:
                 logger.info(f"Token invalid")
            else:
                 token_valid = True
                 logger.info(f"Token still valid")

        #if the token is not in the session or the validity check failed, get a new token
        if session['token'] is None or not token_valid:
            logger.info(f"Token expired. Refreshing token")
            camunda_service.get_token()

            if camunda_service.access_token is not None:
                session['token'] = camunda_service.access_token
            else:
                error_message = "Failed to get token."
                logger.error(error_message)
                return render_template('index.html', show_error_message=True, error_message=error_message)

        # animal_service = AnimalService()
        # animal_url = animal_service.get_animal_url(animal=animal_selected)

        # logger.info(f"animal_urls: {animal_url}")

        # retrieve the deployment resources from the assets directory
        resource_files = os.listdir("assets")
        resource_paths = ['./' + ASSET_DIR + "/" + file for file in resource_files]

        logger.info(f"Retrieved deployment resources resource: {resource_paths}")

        # deploy the resources
        deploymentKey = camunda_service.deploy_resources(resource_paths)

        if deploymentKey is None:
            error_message = "Failed to deploy resources"
            logger.error(error_message)
            return render_template('index.html', show_error_message=True, error_message=error_message)
        
        logger.info(f"Resources successfully deployed. Deployment key: {deploymentKey}")
        
        # process_instance_key = camunda_service.create_process_instance(process_model=PROCESS_MODEL, variables={INPUT_ANIMAL_VAR: selected_animal})
        
        # time.sleep(10)
        
        # camunda_service.get_process_instance(process_instance_key)
        
        # job_key = camunda_service.search_jobs(process_instance_key=process_instance_key, service_task_job_type=SERVICE_TASK_JOB_TYPE)

        # animal_var = camunda_service.get_variable(process_instance_key=process_instance_key, variable_name=INPUT_ANIMAL_VAR)

        # logger.info(f"Retrieved variable {INPUT_ANIMAL_VAR} -> [{animal_var}]")
        
        # camunda_service.activate_jobs(service_task_job_type=SERVICE_TASK_JOB_TYPE, timeout=60000, max_jobs_to_activate=5)
        
        # camunda_service.complete_job(job_key)

        return render_template('index.html', complete=True)
    else:
        return render_template('index.html')

def get_animal_url(animal: str) -> str:

    animal_service = AnimalService(animal=animal)

    animal_service.handleAnimal()

def initialise_camunda_service() -> CamundaService:

    load_dotenv()

    camunda_service = CamundaService()

    camunda_service.base_url = os.getenv('ZEEBE_REST_ADDRESS')
    camunda_service.token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE')
    camunda_service.client_id = os.getenv('CAMUNDA_CLIENT_ID')
    camunda_service.client_secret = os.getenv('CAMUNDA_CLIENT_SECRET')
    camunda_service.auth_url = os.getenv('CAMUNDA_OAUTH_URL')

    return camunda_service

def get_config_values() -> dict[str, str]:

    # retrieve config values from yaml file
    yaml_file_path = __file__.replace(".py", ".yaml")

    if Path(yaml_file_path).exists:
        with open(yaml_file_path, encoding='utf-8') as yaml_file:
            yaml_config = yaml.safe_load(yaml_file)
    else:
        raise Exception(f"Missing {yaml_file_path} file.")
    
    config_values = {}

    log_level = yaml_config.get("config").get("log_level")
    base_url = yaml_config.get("base_url")

    config_values = config_values | { "log_level": log_level } | { "base_url": base_url }

    return config_values


def override_root_level_log_level(log_level: str):

    logging.getLogger().setLevel(logging._nameToLevel[log_level])


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

