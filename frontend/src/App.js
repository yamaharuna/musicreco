import React, { useState } from 'react';
import './style.css';
import Header from './components/Header';
import SpeechControl from './components/SpeechControl';
import RecommendationList from './components/RecommendationList';

function App() {
  const [recognitionResult, setRecognitionResult] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  return (
    <>
      <Header />
      <SpeechControl
        recognitionResult={recognitionResult}
        setRecognitionResult={setRecognitionResult}
        setRecommendations={setRecommendations}
      />
      <RecommendationList recommendations={recommendations} />
    </>
  );
}

export default App;
