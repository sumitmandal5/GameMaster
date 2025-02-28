from unittest.mock import patch

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch("app.services.get_random_pokemon_data", return_value={
    "id": 25,
    "silhouetteImage": "http://127.0.0.1:5000/static/silhouettes/25.png",
    "options": ["pikachu", "bulbasaur", "charmander", "squirtle"]
})
def test_get_random_pokemon_whenCalled_thenItShouldreturnValidOutput(mock_service, client):
    response = client.get("/pokemon/random")
    assert response.status_code == 200
    pokemon_data = response.get_json()

    assert "id" in pokemon_data
    assert "silhouetteImage" in pokemon_data
    assert len(pokemon_data["options"]) == 4


def test_serve_static_silhouettes_whenCalled_thenItshouldRespondWithExpectedstatusCode(client):
    response = client.get("/static/silhouettes/25.png")
    assert response.status_code in [200, 404]

def test_serve_static_realImages_whenCalled_thenItshouldRespondWithExpectedstatusCode(client):
    response = client.get("/static/silhouettes/25.png")
    assert response.status_code in [200, 404]

@patch("app.services.check_pokemon_guess", return_value={
    "correctName": "pikachu",
    "fullImage": "http://127.0.0.1:5000/static/realImages/25.png",
    "guessCorrect": True
})
def test_guess_pokemon_whenGuessIsCorrect_thenReturnTrue(mock_check_pokemon_guess, client):
    response = client.post("/pokemon/guess", json={"id": 25, "guessedName": "pikachu"})

    assert response.status_code == 200
    data = response.get_json()

    assert data["correctName"] == "pikachu"
    assert "fullImage" in data
    assert data["guessCorrect"] is True