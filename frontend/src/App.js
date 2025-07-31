import React, { useState, useEffect, useRef } from 'react';
import './style.css';

function App() {
  const [recognitionResult, setRecognitionResult] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setRecognitionResult('お使いのブラウザは音声認識に対応していません。');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'ja-JP';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = (event) => {
      const last = event.results.length - 1;
      const text = event.results[last][0].transcript;
      setRecognitionResult(`認識結果: ${text}`);
      sendTextToBackend(text);
      setIsRecording(false);
    };

    recognition.onerror = (event) => {
      setRecognitionResult(`音声認識エラー: ${event.error}`);
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
  }, []);

  const startRecognition = () => {
    if (recognitionRef.current) {
      setRecognitionResult('話してください...');
      setRecommendations([]);
      setIsRecording(true);
      recognitionRef.current.start();
    }
  };

  const stopRecognition = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  async function sendTextToBackend(text) {
    try {
      const response = await fetch('http://localhost:5500/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('楽曲推薦の取得に失敗しました:', error);
      setRecommendations([]);
    }
  }

  return (
    <>
      <header>
        <div className="header-left">
          <span className="material-symbols-outlined">music_cast</span>
          <h1><a href="/">MusicReco</a></h1>
        </div>
        <nav>
          <a href="/about">About</a>
        </nav>
      </header>

      <div id="controls">
        <button onClick={startRecognition} disabled={isRecording}>録音開始</button>
        <button onClick={stopRecognition} disabled={!isRecording}>録音停止</button>
      </div>

      <h2>あなたの会話:</h2>
      <div id="recognition-result">{recognitionResult}</div>

      <hr />

      <h2>おすすめの楽曲:</h2>
      <div id="recommendations">
        {recommendations.length === 0 ? (
          <p>ここに楽曲が推薦されます。</p>
        ) : (
          recommendations.map((song, i) => {
            const trackId = song.spotify_link ? song.spotify_link.split('/track/')[1] : null;
            return (
              <div key={i} className="song-item">
                <h3>{song.title} - {song.artist}</h3>
                <p>理由: {song.reason}</p>
                {trackId ? (
                  <iframe
                    src={`https://open.spotify.com/embed/track/${trackId}`}
                    width="300"
                    height="80"
                    frameBorder="0"
                    allowTransparency="true"
                    allow="encrypted-media"
                    title={`spotify-${trackId}`}
                  />
                ) : (
                  <p>Spotifyリンクなし</p>
                )}
              </div>
            );
          })
        )}
      </div>
    </>
  );
}

export default App;

