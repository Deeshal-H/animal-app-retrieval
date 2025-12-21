import pytest
from flask import Flask
import src.app as web_app

app = Flask(__name__)

@pytest.fixture
def setup():
    app_test_client = web_app.app.test_client()
    pytest.app_test_client = app_test_client

def test_home_route(setup):
    response = pytest.app_test_client.get("/")
    html_content = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "<h2>Animal Image Retrieval</h2>" in html_content