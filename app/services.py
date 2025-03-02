import os
import requests
import random
from PIL import Image
from io import BytesIO
import logging
from app.config import POKEAPI_URL, BASE_APPLICATION_URL, REAL_IMAGE_DIR, SILHOUETTE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pokemon_cache = {}


def get_pokemon_data(id):
    """Fetches Pokemon data and caches in-memory"""
    if id is None:
        logger.error("Pokemon ID not provided")
        return {"error": f"Pokemon ID not provided"}

    if id < 1 or id > 50:
        logger.warning(f"Pokemon ID {id} is out of the allowed range (1-50)")
        return {"error": f"Pokemon with ID <1 or ID > 50 not allowed"}

    if id in pokemon_cache:
        return pokemon_cache[id]
    try:
        response = requests.get(f"{POKEAPI_URL}{id}")
        response.raise_for_status()
        data = response.json()

        pokemon_info = {
            "id": data["id"],
            "name": data["name"],
            "sprite": data["sprites"]["other"]["official-artwork"]["front_shiny"]
        }

        pokemon_cache[id] = pokemon_info
        return pokemon_info

    except requests.exceptions.RequestException as ex:
        logger.error(f"Failed to fetch data for Pokemon ID {id}: {ex}")
        return {"error": f"Pokemon with ID {id} not found"}
    except Exception as ex:
        logger.error(f"Unexpected error fetching Pokemon data: {ex}")
        return {"error": "An unexpected error occurred while fetching Pokemon data"}


def get_pokemon_silhouette_and_save_images(sprite_url, pokemon_id):
    """Converts a Pokémon image into a silhouette and returns its stored URL."""
    os.makedirs(SILHOUETTE_DIR, exist_ok=True)  # Ensure directory exists
    os.makedirs(REAL_IMAGE_DIR, exist_ok=True)

    silhouette_path = f"{SILHOUETTE_DIR}/{pokemon_id}.png"
    real_image_path = f"{REAL_IMAGE_DIR}/{pokemon_id}.png"

    # If silhouette already exists, return the existing file path
    if os.path.exists(silhouette_path):
        return f"{BASE_APPLICATION_URL}{silhouette_path}"
    try:
        response = requests.get(sprite_url)
    except requests.exceptions.RequestException as ex:
        logger.error(f"Failed to fetch sprite image for Pokemon ID {pokemon_id}: {ex}")
        return {"error": "Failed to fetch sprite image"}

    if response.status_code == 200:
        try:
            img = Image.open(BytesIO(response.content)).convert("RGBA")  # Ensure transparency
            img.save(real_image_path, format="PNG")  # Save real image

            # ref: https://pillow.readthedocs.io/en/stable/
            '''
            1. Convert an image to grayscale.
            https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
            2. Apply a threshold to separate the foreground (the silhouette) from the background.
            https://www.geeksforgeeks.org/python-pil-image-point-method/
            3. Adjust pixel transparency for creating a silhouette effect.
            '''

            # 1. Convert an image to grayscale.
            img = img.convert("L")

            # 2. Apply a threshold to separate the foreground (the silhouette) from the background.
            threshold = 150  # Adjust this to get a better silhouette effect
            img = img.point(lambda p: 0 if p < threshold else 255)

            # Convert to black-and-transparent silhouette
            img = img.convert("RGBA")
            pixels = img.load()

            # iterate over pixels and transform all other colours to white
            for y in range(img.height):
                for x in range(img.width):
                    if pixels[x, y][0] == 0:  # Black areas remain black
                        pixels[x, y] = (0, 0, 0, 255)  # Fully black
                    else:
                        pixels[x, y] = (255, 255, 255, 0)
                        # RGBAlpha - Alpha set to 0 - sets the pixel to fully transparent white. Non-black areas turn transparent

            img.save(silhouette_path, format="PNG")  # Save with transparency

            return f"{BASE_APPLICATION_URL}{silhouette_path}"  # Return URL
        except Exception as ex:
            logger.error(f"Error processing silhouette for Pokemon ID {pokemon_id}: {ex}")
            return {"error": "An unexpected error occurred while processing silhouette"}
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
        "correctName": correct_name,
        "fullImage": get_pokemon_image_and_save(pokemon["sprite"], pokemon_id),
        "guessCorrect": guessed_name.lower() == correct_name.lower()
    }


def get_pokemon_image_and_save(sprite_url, pokemon_id):
    """check if the image is saved and send it"""
    real_image_path = f"{REAL_IMAGE_DIR}/{pokemon_id}.png"
    if os.path.exists(real_image_path):
        return f"{BASE_APPLICATION_URL}{real_image_path}"
    try:
        response = requests.get(sprite_url)

    except requests.exceptions.RequestException as ex:
        logger.error(f"Failed to fetch sprite image for Pokemon ID {pokemon_id}: {ex}")
        return {"error": "Failed to fetch sprite image"}
    except Exception as ex:
        logger.error(f"Unexpected error processing image for Pokemon ID {pokemon_id}: {ex}")
        return {"error": "An Error occurred while processing image"}

    if response.status_code == 200:
        try:
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            img.save(real_image_path, format="PNG")
            return f"{BASE_APPLICATION_URL}{real_image_path}"
        except IOError as ex:
            logger.error(f"Failed to process image for Pokemon ID {pokemon_id}: {ex}")
            return {"error": "Failed to process image"}

    return None
