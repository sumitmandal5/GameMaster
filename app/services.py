import os
import requests
import random
from PIL import Image
from io import BytesIO

BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
pokemon_cache = {}

def get_pokemon_data(id):
    """Fetches Pokemon data."""
    try:
        response = requests.get(f"{BASE_URL}{id}")
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        return {"error": f"Pokemon with ID {id} not found"}


'''
Grayscale conversion (img.convert("L"))
Converts the image to black & white shades.
Thresholding (img.point(lambda p: 0 if p < threshold else 255))
Makes dark areas black and light areas white.
threshold = 50 (adjust if needed).
Transparency Fix
Any white pixels are turned transparent ((255, 255, 255, 0)).
'''
def get_pokemon_silhouette_and_save_images(sprite_url, pokemon_id):
    """Converts a Pokémon image into a silhouette and returns its stored URL."""
    silhouette_dir = "static/silhouettes"
    real_image_dir = "static/realImages"
    os.makedirs(silhouette_dir, exist_ok=True)  # Ensure directory exists
    os.makedirs(real_image_dir, exist_ok=True)

    silhouette_path = f"{silhouette_dir}/{pokemon_id}.png"
    real_image_path = f"{real_image_dir}/{pokemon_id}.png"

    # If silhouette already exists, return the existing file path
    if os.path.exists(silhouette_path):
        return f"http://127.0.0.1:5000/{silhouette_path}"

    response = requests.get(sprite_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGBA")  # Ensure transparency
        img.save(real_image_path, format="PNG")  # Save real image

        # Convert image to grayscale
        img = img.convert("L")

        # Apply threshold to create a silhouette effect
        threshold = 150  # Adjust this to get a better silhouette effect
        img = img.point(lambda p: 0 if p < threshold else 255)

        # Convert to black-and-transparent silhouette
        img = img.convert("RGBA")
        pixels = img.load()

        for y in range(img.height):
            for x in range(img.width):
                if pixels[x, y][0] == 0:  # Black areas remain black
                    pixels[x, y] = (0, 0, 0, 255)  # Fully black
                else:
                    pixels[x, y] = (255, 255, 255, 0)  # Transparent background

        img.save(silhouette_path, format="PNG")  # Save with transparency

        return f"http://127.0.0.1:5000/{silhouette_path}"  # Return URL
    return None

def get_random_pokemon_data():
    """Generates a random Pokemon id and fetches data"""
    random_id = random.randint(1, 50)
    if random_id in pokemon_cache:
        return pokemon_cache[random_id]
    else:
        pokemon = get_pokemon_data(random_id)

    if "error" in pokemon:
        return pokemon  # Return error if Pokemon not found

    data_to_return = {"id": pokemon["id"],
                      "name": pokemon["name"],
                      "silhouette": get_pokemon_silhouette_and_save_images(pokemon["sprites"]["other"]["official-artwork"]["front_shiny"], pokemon["id"])
                      }
    pokemon_cache[random_id] = data_to_return

    return data_to_return
