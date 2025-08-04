import React, { useEffect, useRef, useState } from 'react';

function SpeechControl({ recognitionResult, setRecognitionResult, setRecommendations }) {
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
  }, [setRecognitionResult, setRecommendations]);

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

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('楽曲推薦の取得に失敗しました:', error);
      setRecommendations([]);
    }
  }

  return (
    <>
      <div id="controls">
        <button onClick={startRecognition} disabled={isRecording}>録音開始</button>
        <button onClick={stopRecognition} disabled={!isRecording}>録音停止</button>
      </div>

      <h2>あなたの会話:</h2>
      <div id="recognition-result">{recognitionResult}</div>
      <hr />
    </>
  );
}

export default SpeechControl;
