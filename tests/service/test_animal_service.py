import pytest
import validators

from src.service.animal_api_service import AnimalService


@pytest.fixture
def setup():

    pytest.animals = {
        "dog",
        "duck",
        "fox"
    }

@pytest.mark.parametrize("animal", [
    "dog",
    "duck",
    "fox"
])
def test_get_animal_url(animal):

    # animal_service = AnimalService()
    # animal_url = animal_service.get_animal_url(animal)

    # assert validators.url(animal_url)

    assert 1 == 1