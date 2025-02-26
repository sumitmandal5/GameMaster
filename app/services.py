import requests
import random

BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

def get_pokemon_data(id):
    """Fetches Pokemon data."""
    try:
        response = requests.get(f"{BASE_URL}{id}")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        return {"error": f"Pokemon with ID {id} not found"}

def get_random_pokemon_data():
    """Generates a random Pokemon id and fetches data"""
    random_id = random.randint(1, 50)
    return get_pokemon_data(random_id)
