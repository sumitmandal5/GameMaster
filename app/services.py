import os
import requests
import random
from PIL import Image
from io import BytesIO

BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
pokemon_cache = {}


def get_pokemon_data(id):
    """Fetches Pokemon data and caches in-memory"""
    if id is None:
        return {"error": f"Pokemon ID not provided"}

    if id<1 or id > 50:
        return {"error": f"Pokemon with ID <1 or ID > 50 not allowed"}

    if id in pokemon_cache:
        return pokemon_cache[id]
    try:
        response = requests.get(f"{BASE_URL}{id}")
        response.raise_for_status()
        data = response.json()

        pokemon_info = {
            "id": data["id"],
            "name": data["name"],
            "sprite": data["sprites"]["other"]["official-artwork"]["front_shiny"]
        }

        pokemon_cache[id] = pokemon_info
        return pokemon_info

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


'''
Fetch the correct Pokemon using random_id (cached if available).
Get three random decoy Pokemon names while ensuring they are not the correct Pokemon.
Check cache for decoys and fetch their names if missing using API call.
Randomly shuffle the correct answer within the list of four options.
Return the final response with Pokemon ID, silhouette image, and shuffled names.
'''


def get_random_pokemon_data():
    """Generates a random Pokemon id and fetches data"""
    random_id = random.randint(1, 50)
    pokemon = get_pokemon_data(random_id)
    if "error" in pokemon:
        return pokemon

    name_options = list()
    while len(name_options) < 3:
        random_decoy_id = random.randint(1, 50)
        if random_decoy_id != random_id:  # Avoid duplicate correct answer
            decoy_pokemon = get_pokemon_data(random_decoy_id)
            if "error" not in decoy_pokemon:
                name_options.append(decoy_pokemon["name"])

    correct_position = random.randint(0, 3)
    name_options.insert(correct_position, pokemon["name"])

    return {
        "id": pokemon["id"],
        "silhouetteImage": get_pokemon_silhouette_and_save_images(pokemon["sprite"], pokemon["id"]),
        "options": name_options
    }


def check_pokemon_guess(pokemon_id, guessed_name):
    """Check if the player guessed correct name and return result"""

    if pokemon_id is None:
        return {"error": f"Pokemon id not provided"}

    if guessed_name is None:
        return {"error": f"guessed_name not provided"}

    pokemon = get_pokemon_data(pokemon_id)

    if "error" in pokemon:
        return {"error": f"Pokemon with ID {pokemon_id} not found"}

    correct_name = pokemon["name"]

    return {
        "correct_name": correct_name,
        "full_image": get_pokemon_image_and_save(pokemon["sprite"], pokemon_id),
        "guessCorrect": guessed_name.lower() == correct_name.lower()
    }


def get_pokemon_image_and_save(sprite_url, pokemon_id):
    """check if the image is saved and send it"""
    real_image_dir = "static/realImages"
    real_image_path = f"{real_image_dir}/{pokemon_id}.png"
    if os.path.exists(real_image_path):
        return f"http://127.0.0.1:5000/{real_image_path}"

    response = requests.get(sprite_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGBA")  # Ensure transparency
        img.save(real_image_path, format="PNG")  # Save real image
        return f"http://127.0.0.1:5000/{real_image_path}"

    return None

