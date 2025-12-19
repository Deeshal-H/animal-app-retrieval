import requests
import logging
import json

API_URLS = {
    "dog": "https://random.dog/woof.json",
    "duck": "https://random-d.uk/api/v2/random",
    "fox": "https://randomfox.ca/floof"
}

RESPONSE_BODY_PROP = {
    "dog": "url",
    "duck": "url",
    "fox": "image"
}

REQUEST_JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept":"application/json"
}

logger = logging.getLogger(__name__)

class AnimalService:

    def __init__(self):
        pass

    def get_animal_url(self, animal: str) -> str:

        logger.error(f"{logger.name} -> animal: {animal}")

        url = API_URLS[animal]

        logger.debug(f"THE animal_url: {url}")

        try:

            session = requests.Session()

            response = session.get(
                url=url
            )

            if response.ok:
                logger.debug(f"{url} - {json.dumps(response.json(), indent=4)}")

                return response.json().get(RESPONSE_BODY_PROP[animal])
            else:
                logger.error(f"Failed to get animal '{animal}''. Status Code: {response.status_code}. Response: {response.text}")

        except requests.exceptions.RequestException as exception:
            logger.error(f"Failed to connect to '{url}] -> {str(exception)}")