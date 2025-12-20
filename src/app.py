import logging
import os
import time
import sys
import yaml

from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from pathlib import Path

from service.camunda_service import CamundaService

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
        logger.info(f"{logger.name} -> Animal selected: {animal_selected}")

        camunda_service = initialise_camunda_service()
        logger.debug(f"{logger.name} -> Retrieved base url: {camunda_service.base_url}")
        
        # Check if a token exists in the session and, if it does, check if it is still valid
        # TODO: Implement token refresh functionality using jwt package to check for expiry.
        #       At the moment, a rudimentary method that makes a request to get the cluster topology is used to see if the token is still valid
        token_refresh_results = get_or_refresh_token(camunda_service=camunda_service)

        if not token_refresh_results["valid"]:
            return render_template('index.html', show_error_message=True, error_message=token_refresh_results["error_message"])


        # Retrieve the deployment resources from the assets directory
        resource_files = os.listdir("assets")
        resource_paths = ['./' + ASSET_DIR + "/" + file for file in resource_files]

        logger.info(f"{logger.name} -> Retrieved deployment resources resource: {resource_paths}")

        # Deploy the resources
        deployment_key = camunda_service.deploy_resources(resource_paths)

        if not deployment_key:
            # Log the error message to the logger's handler(s) and output it to the html form
            error_message = "Failed to deploy resources"
            logger.error(f"{logger.name} -> {error_message}")
            return render_template('index.html', show_error_message=True, error_message=error_message)
        
        logger.info(f"{logger.name} -> successfully deployed resources. Deployment Key: {deployment_key}")


        # Create and start a process instance
        process_instance_key = camunda_service.create_process_instance(process_model=PROCESS_MODEL, variables={INPUT_ANIMAL_VAR: animal_selected}) # "4503599627452451"

        if not process_instance_key:
            error_message = "Failed to create process instance"
            logger.error(f"{logger.name} -> {error_message}")
            return render_template('index.html', show_error_message=True, error_message=error_message)
        
        logger.info(f"{logger.name} -> Successfully created process instance. Process Instance Key: {process_instance_key}")
        
        # Search for the jobs for the service task in the process instance and get its job key
        # HACK: Sleep for 10 seconds before retrieving the job as the search job method is 'Eventually Consistent'
        time.sleep(10)
        job_key = camunda_service.search_jobs(process_instance_key=process_instance_key, service_task_job_type=SERVICE_TASK_JOB_TYPE)

        if not job_key:
            error_message = "Failed to retrieve the job key for the service task"
            logger.error(f"{logger.name} -> {error_message}")
            return render_template('index.html', show_error_message=True, error_message=error_message)
        
        logger.info(f"{logger.name} -> Successfully retrieved the job key for service task of type {SERVICE_TASK_JOB_TYPE}. Job Key: {job_key}")

        # Get the 'animal' variable from the process instance
        # NOTE: Within the scope of this application, we already have the value of the animal selected but this demonstrates getting the variable from the process instance
        animal_var = camunda_service.get_variable(process_instance_key=process_instance_key, variable_name=INPUT_ANIMAL_VAR)

        logger.info(f"{logger.name} -> Retrieved variable {INPUT_ANIMAL_VAR} from process instance: {animal_var}")
        
        # Activate the jobs for the service task type
        # NOTE: Set the timeout period to a relatively high 60 seconds as the call that handles the job completion can take around 45 seconds to complete depending on which animal is picked
        #       The duck and fox REST services are slow
        camunda_service.activate_jobs(service_task_job_type=SERVICE_TASK_JOB_TYPE, timeout=60000, max_jobs_to_activate=5)
        
        # handle the job and return the animal image url
        animal_image_url = camunda_service.complete_job(job_key, animal=animal_var)

        return render_template('index.html', complete=True, animal_image_url=animal_image_url)
    else:
        return render_template('index.html')


def initialise_camunda_service() -> CamundaService:
    """
    Initialises an instance of the camunda service and sets its properties from environment variables

    The following environment variables are required:
        - ZEEBE_REST_ADDRESS: The address of the REST API of the SaaS cluster to connect to.
        - CAMUNDA_TOKEN_AUDIENCE: The audience for which the token should be valid.
        - CAMUNDA_CLIENT_ID: The client ID used to request an access token from the authorization server.
        - CAMUNDA_CLIENT_SECRET: The client secret used to request an access token from the authorization server.
        - CAMUNDA_OAUTH_URL: The URL of the authorization server from which the access token can be requested.

    Returns:
        CamundaService: Instance of camunda service
    """

    load_dotenv()

    camunda_service = CamundaService()

    camunda_service.base_url = os.getenv('ZEEBE_REST_ADDRESS')
    camunda_service.token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE')
    camunda_service.client_id = os.getenv('CAMUNDA_CLIENT_ID')
    camunda_service.client_secret = os.getenv('CAMUNDA_CLIENT_SECRET')
    camunda_service.auth_url = os.getenv('CAMUNDA_OAUTH_URL')

    return camunda_service


def get_or_refresh_token(camunda_service: CamundaService) -> dict[bool, str]:
    """
    Checks if a valid access token exists in the session. If not, refreshes the token and stores it in the session.
    Uses a request to get the cluster topology to check if the token is valid.

    Args:
        camunda_service (CamundaService): CamundaService object

    Returns:
        dict: dict[bool, str] Returns a dictionary indicating success or failure with error message, e.g. { "valid": False, "error_message": "Token invalid." }
    """

    token_valid = False

    if session['token']:
        logger.info(f"{logger.name} -> Found token in session")
        camunda_service.access_token = session['token']        
        token_valid = camunda_service.get_cluster_topology()

        if token_valid is None: # None: Could not connect to check cluster topology to check token validity
            return { "valid": False, "error_message": "Failed to check for token validity or token invalid." }
        elif not token_valid: # False: Unauthorised to retrieve cluster topology
            logger.info(f"{logger.name} -> Token invalid")
        else:
            token_valid = True
            logger.info(f"{logger.name} -> Token still valid")
            return { "valid": True, "error_message": None }

    # if the token is not in the session or the validity check failed, get a new token
    if not session['token'] or not token_valid:
        logger.info(f"{logger.name} -> Token expired. Refreshing token")
        camunda_service.get_token()

        if camunda_service.access_token:
            session['token'] = camunda_service.access_token
            return { "valid": True, "error_message": None }
        else:
            return { "valid": False, "error_message": "Failed to get token." }


def get_config_values() -> dict[str, str]:
    """
    Reads a yaml config file for the current file and returns its values

    Raises:
        Exception: When yaml file is not present.

    Returns:
        dict: dict[str, str]: Key-value pairs of config items
    """

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
    """
    Overrides the root log level

    Args:
        log_level (str): Log level
    """

    logging.getLogger().setLevel(logging._nameToLevel[log_level])

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

