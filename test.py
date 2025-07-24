import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_spotify_token():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    auth_url = "https://accounts.spotify.com/api/token"

    response = requests.post(auth_url, data={
        'grant_type': 'client_credentials'
    }, auth=(client_id, client_secret))

    if response.status_code == 200:
        token_info = response.json()
        return token_info['access_token']
    else:
        print(f"Failed to get Spotify token. Status code: {response.status_code}")
        print(f"Response body: {response.text}")
        return None

def search_song(token, song_title, artist_name):
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    query = f"{song_title} {artist_name}"
    params = {
        'q': query,
        'type': 'track',
        'limit': 1
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()
        tracks = results.get('tracks', {}).get('items', [])
        if tracks:
            return tracks[0]['external_urls']['spotify']
        else:
            print("No tracks found.")
            return None
    else:
        print(f"Failed to search song. Status code: {response.status_code}")
        print(f"Response body: {response.text}")
        return None

if __name__ == '__main__':
    token = get_spotify_token()
    if token is None:
        print("Spotify token could not be retrieved.")
    else:
        song_title = "チェリー"
        artist_name = "スピッツ"
        link = search_song(token, song_title, artist_name)
        if link:
            print(f"Spotify link for '{song_title}' by '{artist_name}': {link}")
        else:
            print("Could not find Spotify link.")

import os
print("Client ID:", os.getenv("SPOTIFY_CLIENT_ID"))
print("Client Secret:", os.getenv("SPOTIFY_CLIENT_SECRET"))
