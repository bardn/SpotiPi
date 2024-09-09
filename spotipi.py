import time
import requests
from io import BytesIO
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import json
from threading import Lock  # Import Lock for synchronization

# Configuration file path
config_file_path = 'spotify_config.json'

# Create a lock for the matrix (shared with the other service)
matrix_lock = Lock()

def load_config():
    with open(config_file_path) as config_file:
        return json.load(config_file)

def setup_matrix():
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'
    options.brightness = 80
    return RGBMatrix(options=options)

def fetch_current_track(access_token):
    url = 'https://api.spotify.com/v1/me/player/currently-playing'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_album_artwork(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.RequestException:
        return None

def resize_image(image, target_size):
    img_width, img_height = image.size
    target_width, target_height = target_size

    img_aspect = img_width / img_height
    target_aspect = target_width / target_height

    if img_aspect > target_aspect:
        new_width = target_width
        new_height = int(new_width / img_aspect)
    else:
        new_height = target_height
        new_width = int(new_height * img_aspect)

    img = image.resize((new_width, new_height), Image.LANCZOS)

    background = Image.new('RGB', target_size, (0, 0, 0))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    background.paste(img, (paste_x, paste_y))
    return background

def display_image_on_matrix(image, matrix):
    image = resize_image(image, (matrix.width, matrix.height))
    image = image.convert('RGB')

    # Lock the matrix for display
    with matrix_lock:
        matrix.SetImage(image)

def main():
    config = load_config()
    access_token = config['access_token']
    
    matrix = setup_matrix()
    
    prev_track_url = ""

    while True:
        track_data = fetch_current_track(access_token)
        if track_data and 'item' in track_data:
            album_art_url = track_data['item']['album']['images'][0]['url']
            
            if album_art_url != prev_track_url:
                image = fetch_album_artwork(album_art_url)
                if image:
                    display_image_on_matrix(image, matrix)
                    prev_track_url = album_art_url
        
        time.sleep(5)  # Check every 5 seconds

if __name__ == '__main__':
    main()
