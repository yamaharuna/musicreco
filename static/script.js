const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const recognitionResult = document.getElementById('recognition-result');
const recommendationsDiv = document.getElementById('recommendations');

let recognition; // Web Speech API の SpeechRecognition オブジェクト

// SpeechRecognition オブジェクトの初期化
if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ja-JP'; // 日本語を設定英語にする場合は選べるようにする
    recognition.interimResults = false; // 中間結果は不要
    recognition.continuous = false; // 一回話したら停止
} else {
    recognitionResult.textContent = 'お使いのブラウザは音声認識に対応していません。';
    startButton.disabled = true;
    stopButton.disabled = true;
}

// 録音開始ボタン
startButton.addEventListener('click', () => {
    recognitionResult.textContent = '話してください...';
    recommendationsDiv.innerHTML = '<p>ここに楽曲が推薦されます。</p>'; // 以前の結果をクリア
    startButton.disabled = true;
    stopButton.disabled = false;
    recognition.start();
});

// 録音停止ボタン（主に連続モードの場合に使うが、今回は一回停止なので使わないかも）
stopButton.addEventListener('click', () => {
    recognition.stop();
    startButton.disabled = false;
    stopButton.disabled = true;
});



// 音声認識結果が得られた時
recognition.addEventListener('result', (event) => {
    const last = event.results.length - 1;
    const text = event.results[last][0].transcript;
    recognitionResult.textContent = `認識結果: ${text}`;
    sendTextToBackend(text); // バックエンドにテキストを送信
});

// 音声認識エラーが発生した時
recognition.addEventListener('error', (event) => {
    recognitionResult.textContent = `音声認識エラー: ${event.error}`;
    startButton.disabled = false;
    stopButton.disabled = true;
});

// バックエンドにテキストを送信し、楽曲推薦を受け取る関数
async function sendTextToBackend(text) {
    try {
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayRecommendations(data.recommendations);

    } catch (error) {
        console.error('楽曲推薦の取得に失敗しました:', error);
        recommendationsDiv.innerHTML = '<p>楽曲推薦の取得中にエラーが発生しました。</p>';
    }
}

function displayRecommendations(songs) {
    recommendationsDiv.innerHTML = ''; // クリア
    if (songs && songs.length > 0) {
        songs.forEach(song => {
            const songItem = document.createElement('div');
            songItem.classList.add('song-item');

            const trackId = song.spotify_link ? song.spotify_link.split('/track/')[1] : null;

            songItem.innerHTML = `
                <h3>${song.title} - ${song.artist}</h3>
                <p>理由: ${song.reason}</p>
                ${trackId ? `
                <iframe 
                  src="https://open.spotify.com/embed/track/${trackId}" 
                  width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>` 
                  : '<p>Spotifyリンクなし</p>'}
            `;
            recommendationsDiv.appendChild(songItem);
        });
    } else {
        recommendationsDiv.innerHTML = '<p>条件に合う楽曲は見つかりませんでした。</p>';
    }
}
