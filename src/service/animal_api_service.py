"""
Service to retrieve animal image
"""

import json
import logging
import requests

# Stores the REST API URL for each animal type
API_URLS = {
    "dog": "https://random.dog/woof.json",
    "duck": "https://random-d.uk/api/v2/random",
    "fox": "https://randomfox.ca/floof"
}

# Stores the property within the json response body that contains the image url
RESPONSE_BODY_PROP = {
    "dog": "url",
    "duck": "url",
    "fox": "image"
}

logger = logging.getLogger(__name__)

class AnimalService:

    def __init__(self):
        pass

    def get_animal_url(self, animal: str) -> str:
        """
        Gets the animal image url

        Args:
            animal (str): Animal type

        Returns:
            str: Animal image url
        """

        logger.debug(f"{logger.name} -> Animal: {animal}")

        url = API_URLS[animal]

        logger.debug(f"{logger.name} -> Animal image url: {url}")

        try:

            session = requests.Session()

            response = session.get(
                url=url
            )

            if response.ok:
                logger.debug(f"{logger.name} -> {url} - {json.dumps(response.json(), indent=4)}")

                return response.json().get(RESPONSE_BODY_PROP[animal])
            else:
                logger.error(f"{logger.name} -> Failed to get animal '{animal}''. Status Code: {response.status_code}. Response: {response.text}")

        except requests.exceptions.RequestException as exception:
            logger.error(f"{logger.name} -> Failed to connect to '{url}] -> {str(exception)}")