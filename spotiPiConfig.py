import json
import requests
import time
from urllib.parse import urlparse, parse_qs

# Configuration file path
config_file_path = 'spotify_config.json'

def prompt_for_input(prompt):
    return input(prompt).strip()

def create_config_file(client_id, client_secret, redirect_uri):
    config = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
    }
    
    with open(config_file_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)
    
    print(f"Configuration file '{config_file_path}' has been created successfully.")

def get_authorization_code(client_id, redirect_uri):
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=user-read-currently-playing"
    )
    print(f"Please go to this URL and authorize the app: {auth_url}")
    
    full_redirect_url = input("Enter the full redirected URL: ")
    
    parsed_url = urlparse(full_redirect_url)
    authorization_code = parse_qs(parsed_url.query).get('code', [None])[0]
    
    if not authorization_code:
        raise ValueError("Authorization code not found in the URL")
    
    return authorization_code

def exchange_code_for_token(client_id, client_secret, redirect_uri, code):
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    headers = {
        'Authorization': f'Basic {requests.auth._basic_auth_str(client_id, client_secret)}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=data, headers=headers)
    token_data = response.json()
    
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    
    return access_token, refresh_token

def save_tokens(access_token, refresh_token):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    
    config['access_token'] = access_token
    config['refresh_token'] = refresh_token
    
    with open(config_file_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)
    
    print("Config file updated with new access token and refresh token.")

def refresh_access_token(client_id, client_secret, refresh_token):
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Authorization': f'Basic {requests.auth._basic_auth_str(client_id, client_secret)}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=data, headers=headers)
    token_data = response.json()
    
    new_access_token = token_data.get('access_token')
    new_refresh_token = token_data.get('refresh_token', refresh_token)

    return new_access_token, new_refresh_token

def main():
    print("Welcome to the Spotify API configuration setup script.")

    client_id = prompt_for_input("Enter your Spotify API client ID: ")
    client_secret = prompt_for_input("Enter your Spotify API client secret: ")
    redirect_uri = prompt_for_input("Enter your redirect URI: ")

    create_config_file(client_id, client_secret, redirect_uri)

    authorization_code = get_authorization_code(client_id, redirect_uri)

    access_token, refresh_token = exchange_code_for_token(client_id, client_secret, redirect_uri, authorization_code)

    save_tokens(access_token, refresh_token)

    print("Waiting for 5 seconds before refreshing token...")
    time.sleep(5)

    new_access_token, new_refresh_token = refresh_access_token(client_id, client_secret, refresh_token)
    save_tokens(new_access_token, new_refresh_token)

if __name__ == '__main__':
    main()
