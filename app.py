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
        # Step 1: Geminiで感情・ジャンル・雰囲気を抽出
        prompt_for_extraction = f"""
        以下のユーザーの会話から、ユーザーの感情、求めているジャンル、そして歌詞の雰囲気を抽出してください。
        もしジャンルや歌詞の雰囲気が明確でない場合は、「不明」と記述してください。
        出力はJSON形式でお願いします。
        例: {{"emotion": "リラックス", "genre": "ジャズ", "lyric_vibe": "心が落ち着く"}}

        会話: "{user_text}"
        """
        response_extraction = model.generate_content(prompt_for_extraction)
        extracted_info_str = response_extraction.text.strip().replace('```json\n', '').replace('\n```', '')
        extracted_info = json.loads(extracted_info_str)

        emotion = extracted_info.get("emotion", "不明")
        genre = extracted_info.get("genre", "不明")
        lyric_vibe = extracted_info.get("lyric_vibe", "不明")

        # Step 2: 楽曲を提案
        prompt_for_recommendation = f"""
        ユーザーは「{user_text}」と話しました。
        会話から、感情は「{emotion}」、求めているジャンルは「{genre}」、歌詞の雰囲気は「{lyric_vibe}」と推測されます。

        これらの情報に基づいて、歌詞の内容がユーザーの気分や状況に合いそうな楽曲を3曲提案してください。
        各曲について「title」「artist」「reason」の3項目で出力してください。
        出力はJSON形式でお願いします。
        例: [
            {{"title": "曲名A", "artist": "アーティストX", "reason": "理由A"}},
            {{"title": "曲名B", "artist": "アーティストY", "reason": "理由B"}},
            {{"title": "曲名C", "artist": "アーティストZ", "reason": "理由C"}}
        ]
        """
        response_recommendation = model.generate_content(prompt_for_recommendation)
        recommended_songs_str = response_recommendation.text.strip().replace('```json\n', '').replace('\n```', '')
        recommended_songs = json.loads(recommended_songs_str)

        return jsonify({'recommendations': recommended_songs})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
