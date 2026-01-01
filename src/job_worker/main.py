import logging
import os
import time

from dotenv import load_dotenv

from service.camunda_service import CamundaService

# NAME OF SERVICE TASK TO RETRIEVE IMAGE
SERVICE_TASK_JOB_TYPE = "retrieve-animal-image"

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

# Load the environment variables
load_dotenv()

# global variable to store the access token
access_token = ""

def main():
    
    logger.debug(f"Token -> {access_token}")

    # Activate the jobs for the service task type
    # NOTE: Set the timeout period to a relatively high 60 seconds as the call that handles the job completion can take around 45 seconds to complete depending on which animal is picked
    #       The duck and fox REST services are slow
    jobs = camunda_service.activate_jobs(service_task_job_type=SERVICE_TASK_JOB_TYPE, timeout=60000, max_jobs_to_activate=5)

    for job in jobs:
        # logger.debug(json.dumps(job, indent=4))
        animal_var = job.get("variables").get("animal")
        job_key = job.get("jobKey")
        
        logger.debug(f"animal_var -> {animal_var}")
        logger.debug(f"job_key -> {job_key}")

        # handle the job and return the animal image url
        animal_image_url = camunda_service.complete_job(job_key, animal=animal_var)


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


if __name__ == "__main__":

    camunda_service = initialise_camunda_service()

    # get the access_token and set the value to the global variable
    camunda_service.get_token()
    access_token = camunda_service.access_token

    while True:
        main()
        time.sleep(60)