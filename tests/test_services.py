import pytest
import json
import requests
from unittest.mock import patch
from app.services import get_pokemon_data, get_random_pokemon_data, check_pokemon_guess, pokemon_cache

pokemon_mock = {
    "id": 25,
    "name": "pikachu",
    "sprites": {
        "other": {
            "official-artwork": {
                "front_shiny": "https://pokeapi.com/pikachu.png"
            }
        }
    }
}


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the Pokemon cache before each test to ensure fresh API calls."""
    pokemon_cache.clear()


@pytest.fixture
def mock_requests_get():
    """Mock requests.get to return pokemon json object"""
    with patch("app.services.requests.get") as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        mock_response._content = json.dumps(pokemon_mock).encode("utf-8")
        mock_get.return_value = mock_response
        yield mock_get


def test_get_pokemon_data_when_invoked_returnsPokemonJsonData(mock_requests_get):
    pokemon = get_pokemon_data(25)
    assert pokemon["id"] == 25
    assert pokemon["name"] == "pikachu"
    assert "sprite" in pokemon
    assert pokemon["sprite"] == "https://pokeapi.com/pikachu.png"


def test_get_pokemon_data_when_givenIdIsLessThanOne_ThenThrowError():
    pokemon = get_pokemon_data(0)
    assert pokemon["error"] == "Pokemon with ID <1 or ID > 50 not allowed"


def test_get_pokemon_data_when_givenIdIsNone_ThenThrowError():
    pokemon = get_pokemon_data(None)
    assert pokemon["error"] == "Pokemon ID not provided"


@patch("app.services.get_pokemon_silhouette_and_save_images",
       return_value="http://127.0.0.1:5000/static/silhouettes/22.png")
def test_get_random_pokemon_data_when_called_then_returnsAJsonObject(mock_silhouette, mock_requests_get):
    pokemon = get_random_pokemon_data()

    assert "id" in pokemon
    assert pokemon["silhouetteImage"] == "http://127.0.0.1:5000/static/silhouettes/22.png"
    assert len(pokemon["options"]) == 4


@patch("app.services.get_pokemon_data",
       return_value={"id": 25, "name": "pikachu", "sprite": "https://example.com/pikachu.png"})
def test_check_pokemon_guess_when_givenTherightAnswer_thenMatchesAndReturnsTrue(mock_get_pokemon_data):
    result = check_pokemon_guess(25, "pikachu")
    assert result["correctName"] == "pikachu"
    assert result["guessCorrect"] is True


@patch("app.services.get_pokemon_data",
       return_value={"id": 25, "name": "pikachu", "sprite": "https://example.com/pikachu.png"})
def test_check_pokemon_guess_when_givenTheWrongAnswer_thenMatchesAndReturnsFalse(mock_get_pokemon_data):
    result = check_pokemon_guess(25, "fearow")
    assert result["correctName"] == "pikachu"
    assert result["guessCorrect"] is False


def test_check_pokemon_guess_when_givenTheInvalidAnswer_then():
    """Test guess with missing ID or name."""
    result = check_pokemon_guess(None, "pikachu")
    assert "error" in result

    result = check_pokemon_guess(25, None)
    assert "error" in result
