import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import requests

# 環境変数読み込み
load_dotenv()

# Spotifyアクセストークンをグローバル変数管理（有効期限は簡易管理でOKならこれで）
spotify_token = None

def get_spotify_token():
    global spotify_token
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    auth_url = "https://accounts.spotify.com/api/token"
    
    response = requests.post(auth_url, data={
        'grant_type': 'client_credentials'
    }, auth=(client_id, client_secret))
    
    if response.status_code == 200:
        token_info = response.json()
        spotify_token = token_info['access_token']
        return spotify_token
    else:
        raise Exception("Failed to get Spotify token")

def get_spotify_link(song_title, artist_name):
    global spotify_token
    if not spotify_token:
        get_spotify_token()  # トークンがなければ取得
    
    search_url = "https://api.spotify.com/v1/search"
    
    headers = {
        'Authorization': f'Bearer {spotify_token}'
    }
    
    # 曲名とアーティスト名で検索（ゆるめのクエリにしてもOK）
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
            return None
    else:
        # トークン期限切れなどで401の場合は再取得して再試行してもいい
        if response.status_code == 401:
            spotify_token = None  # トークン破棄
            return get_spotify_link(song_title, artist_name)
        raise Exception(f"Failed to search for song on Spotify: {response.status_code}")

# Flask初期化
app = Flask(__name__, static_folder='static')

# Gemini初期化
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/about')
def about():
    return app.send_static_file('about.html')

@app.route('/recommend', methods=['POST'])
def recommend_music():
    user_text = request.json.get('text')
    if not user_text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        prompt_combined = f"""
以下のユーザーの発言から、感情・ジャンル・歌詞の雰囲気を推測し、
それに基づいて楽曲を3つ提案してください。

出力は以下の形式のJSONでお願いします：

{{
  "emotion": "...",
  "genre": "...",
  "lyric_vibe": "...",
  "recommendations": [
    {{
      "title": "曲名A",
      "artist": "アーティストX",
      "reason": "理由A"
    }},
    {{
      "title": "曲名B",
      "artist": "アーティストY",
      "reason": "理由B"
    }},
    {{
      "title": "曲名C",
      "artist": "アーティストZ",
      "reason": "理由C"
    }}
  ]
}}

ユーザーの発言: "{user_text}"
"""

        response = model.generate_content(prompt_combined)
        response_text = response.text.strip().replace('```json\n', '').replace('\n```', '')
        result = json.loads(response_text)

        recommended_songs = result.get("recommendations", [])

        # Spotifyリンクを取得して付加
        for song in recommended_songs:
            title = song.get("title", "").strip()
            artist = song.get("artist", "").strip()
            if title and artist:
                try:
                    spotify_link = get_spotify_link(title, artist)
                    song['spotify_link'] = spotify_link
                except Exception as e:
                    song['spotify_link'] = None
                    print(f"Error getting Spotify link for '{title}' by '{artist}': {e}")
            else:
                song['spotify_link'] = None

        return jsonify({'recommendations': recommended_songs})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
