"""
Entrypoint for job worker
"""

import logging
import os
import time

from dotenv import load_dotenv

from service.animal_api_service import AnimalService
from service.camunda_service import CamundaService

# Name of service task to retrieve image
SERVICE_TASK_JOB_TYPE = "retrieve-animal-image"

# Name of output variable that holds the animal image url
OUTPUT_ANIMAL_URL_VAR = "animal_url"

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

def main(camunda_service: CamundaService):

    logger.debug("Token -> %s", access_token)

    # Activate the jobs for the service task type
    # NOTE: Set the timeout period to a relatively high 60 seconds as the call that handles the job completion can take around
    #       45 seconds to complete depending on which animal is picked. The duck and fox REST services are slow
    jobs = camunda_service.activate_jobs(service_task_job_type=SERVICE_TASK_JOB_TYPE, timeout=60000, max_jobs_to_activate=5)

    for job in jobs:
        animal = job.get("variables").get("animal")
        job_key = job.get("jobKey")

        logger.debug("animal_var -> %s", animal)
        logger.debug("job_key -> %s", job_key)

        # get an image url based for the animal
        animal_service = AnimalService()
        animal_image_url = animal_service.get_animal_url(animal=animal)
        logger.info("%s -> Retrieved URL for animal image %s: %s.", logger.name, animal, animal_image_url)

        # handle the job failure or completion
        if not animal_image_url:
            camunda_service.fail_job(job_key=job_key, error_message=f"Failed to get animal image for {animal}.")
        else:
            animal_image_url = camunda_service.complete_job(job_key, variables={ OUTPUT_ANIMAL_URL_VAR: animal_image_url })


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

    return CamundaService(
        base_url = os.getenv('ZEEBE_REST_ADDRESS'),
        token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE'),
        client_id = os.getenv('CAMUNDA_CLIENT_ID'),
        client_secret = os.getenv('CAMUNDA_CLIENT_SECRET'),
        auth_url = os.getenv('CAMUNDA_OAUTH_URL')
    )


if __name__ == "__main__":

    camunda_service_init = initialise_camunda_service()

    # get the access_token and set the value to the global variable
    camunda_service_init.get_token()
    access_token = camunda_service_init.access_token

    while True:
        main(camunda_service_init)
        time.sleep(60)
