import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai


# 環境変数読み込み
load_dotenv()



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

        emotion = result.get("emotion", "不明")
        genre = result.get("genre", "不明")
        lyric_vibe = result.get("lyric_vibe", "不明")
        recommended_songs = result.get("recommendations", [])

        return jsonify({'recommendations': recommended_songs})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
