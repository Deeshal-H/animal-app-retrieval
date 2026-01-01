import logging
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from pathlib import Path

from helpers.utils import Utils
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

# Load the environment variables
load_dotenv()

# Set the secret key to use flask session data.
app.secret_key = os.getenv('FLASK_SESSION_SECRET_KEY')


@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        # # Retrieves config values
        # config_values = Utils.get_config_values()
        # logger.debug(f"config_values -> {config_values}")

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
        assets_rel_dir = os.path.relpath(path=os.path.join(os.path.dirname(__file__), ASSET_DIR), start=os.path.abspath(os.curdir))

        resource_files = os.listdir(assets_rel_dir)
        resource_paths = ['./' + Path(assets_rel_dir).as_posix() + "/" + file for file in resource_files]

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
        process_instance_key = camunda_service.create_process_instance(process_model=PROCESS_MODEL, variables={INPUT_ANIMAL_VAR: animal_selected})

        if not process_instance_key:
            error_message = "Failed to create process instance"
            logger.error(f"{logger.name} -> {error_message}")
            return render_template('index.html', show_error_message=True, error_message=error_message)
        
        logger.info(f"{logger.name} -> Successfully created process instance. Process Instance Key: {process_instance_key}")

        return render_template('index.html', complete=True, animal_image_url="")
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

    camunda_service = CamundaService(
        base_url = os.getenv('ZEEBE_REST_ADDRESS'),
        token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE'),
        client_id = os.getenv('CAMUNDA_CLIENT_ID'),
        client_secret = os.getenv('CAMUNDA_CLIENT_SECRET'),
        auth_url = os.getenv('CAMUNDA_OAUTH_URL')
    )

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

    # if the token is not in the session
    if not session.get('token'):
        logger.info(f"{logger.name} -> Token not found.")
    else:
        logger.info(f"{logger.name} -> Found token in session")
        camunda_service.access_token = session['token']        
        token_verified = camunda_service.get_cluster_topology()

        if token_verified is None: # None: Could not connect to check cluster topology to check token validity
            return { "valid": False, "error_message": "Failed to check for token validity or token invalid." }
        elif not token_verified: # False: Unauthorised to retrieve cluster topology
            logger.info(f"{logger.name} -> Token invalid")
        else:
            token_valid = True
            logger.info(f"{logger.name} -> Token still valid")
            return { "valid": True, "error_message": None }

    # if the token is not in the session or the validity check failed, get a new token
    if not token_valid:
        camunda_service.get_token()

        if camunda_service.access_token:
            session['token'] = camunda_service.access_token
            return { "valid": True, "error_message": None }
        else:
            return { "valid": False, "error_message": "Failed to get token." }


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

