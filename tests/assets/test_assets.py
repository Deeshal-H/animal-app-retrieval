import pytest
from pathlib import Path

@pytest.fixture
def setup():

    assets_relative_dir = "src/assets"
    pytest.assets_relative_dir = assets_relative_dir

def test_assets_exists(setup):
    """
    Test that the assets exist
    """

    assert len(list(Path(pytest.assets_relative_dir).glob(pattern="*.bpmn"))) > 0
    assert len(list(Path(pytest.assets_relative_dir).glob(pattern="*.form"))) > 0