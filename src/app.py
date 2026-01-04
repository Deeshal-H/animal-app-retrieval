"""
Entry point of flask application
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request, session

from service.camunda_service import CamundaService

# Process name
PROCESS_MODEL = "Process_AnimalImageRetrieval"

# Name of input variable to service task that retrieves animal image
INPUT_ANIMAL_VAR = "animal"

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
    """
    Home page route
    """

    if request.method == 'POST':

        # # Retrieves config values
        # config_values = Utils.get_config_values()
        # logger.debug("config_values -> %s", config_values)

        animal_selected = request.form.get('animal')
        logger.info("%s -> Animal selected: %s", logger.name, animal_selected)

        camunda_service = initialise_camunda_service()
        logger.debug("%s -> Retrieved base url: %s", logger.name, camunda_service.base_url)

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

        logger.info("%s -> Retrieved deployment resources resource: %s", logger.name, resource_paths)


        # Deploy the resources
        deployment_key = camunda_service.deploy_resources(resource_paths)

        if not deployment_key:
            # Log the error message to the logger's handler(s) and output it to the html form
            error_message = "Failed to deploy resources"
            logger.error("%s -> %s", logger.name, error_message)
            return render_template('index.html', show_error_message=True, error_message=error_message)

        logger.info("%s -> successfully deployed resources. Deployment Key: %s", logger.name, deployment_key)


        # Create and start a process instance
        process_instance_key = camunda_service.create_process_instance(process_model=PROCESS_MODEL, variables={INPUT_ANIMAL_VAR: animal_selected})

        if not process_instance_key:
            error_message = "Failed to create process instance"
            logger.error("%s -> %s", logger.name, error_message)
            return render_template('index.html', show_error_message=True, error_message=error_message)

        logger.info("%s -> Successfully created process instance. Process Instance Key: %s", logger.name, process_instance_key)

        return render_template('index.html', complete=True, animal_image_url="")

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
        dict[bool, str]: A dictionary indicating success or failure with error message, e.g. { "valid": False, "error_message": "Token invalid." }
    """

    token_valid = False

    # if the token is not in the session
    if not session.get('token'):
        logger.info("%s -> Token not found.", logger.name)
    else:
        logger.info("%s -> Found token in session", logger.name)
        camunda_service.access_token = session['token']
        token_verified = camunda_service.get_cluster_topology()

        if token_verified is None: # None: Could not connect to check cluster topology to check token validity
            return { "valid": False, "error_message": "Failed to check for token validity or token invalid." }

        if not token_verified: # False: Unauthorised to retrieve cluster topology
            logger.info("%s -> Token invalid", logger.name)
        else:
            token_valid = True
            logger.info("%s -> Token still valid", logger.name)
            return { "valid": True, "error_message": None }

    # if the token is not in the session or the validity check failed, get a new token
    if not token_valid:
        camunda_service.get_token()

        if camunda_service.access_token:
            session['token'] = camunda_service.access_token
            return { "valid": True, "error_message": None }

    return { "valid": False, "error_message": "Failed to get token." }


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
