import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

def test_get_pokemon(client):
    response = client.get('/pokemon/pikachu')
    assert response.status_code == 200
    assert "name" in response.json