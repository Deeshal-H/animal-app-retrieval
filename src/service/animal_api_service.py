"""
Service to retrieve animal image
"""

import json
import logging
import requests

from helpers.utils import Utils

# Stores the property within the json response body that contains the image url
RESPONSE_BODY_PROP = {
    "dog": "url",
    "duck": "url",
    "fox": "image"
}

logger = logging.getLogger(__name__)

class AnimalService:

    def __init__(self):

        # get the api urls from teh config file
        self.animal_api_url = Utils.get_config_values().get("animal_api_url")
        logger.debug("animal_api_url -> %s", self.animal_api_url)


    def get_animal_url(self, animal: str) -> str:
        """
        Gets the animal image url

        Args:
            animal (str): Animal type

        Returns:
            str: Animal image url
        """

        logger.debug("%s -> Animal: %s", logger.name, animal)

        url = self.animal_api_url[animal]

        logger.debug("%s -> Animal image url: %s", logger.name, url)

        try:
            session = requests.Session()

            response = session.get(
                url=url
            )

            if response.ok:
                logger.debug("%s -> %s - %s", logger.name, url, json.dumps(response.json(), indent=4))

                return response.json().get(RESPONSE_BODY_PROP[animal])
            else:
                logger.error("%s -> Failed to get animal '%s'. Status Code: %s. Response: %s", logger.name, animal, response.status_code, response.text)

        except requests.exceptions.RequestException as exception:
            logger.error("%s -> Failed to connect to '%s' -> %s", logger.name, url, str(exception))

        return ""
