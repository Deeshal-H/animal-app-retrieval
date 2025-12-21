import pytest
import requests
from src.service.animal_api_service import AnimalService

def test_get_animal_url():

    url = "https://random.dog/woof.json"

    response = requests.get(url)

    assert response.status_code == 200
    assert "https://random.dog/" in response.json()["url"]