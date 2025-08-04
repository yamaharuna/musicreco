import React from 'react';
import SongItem from './SongItem';

function RecommendationList({ recommendations }) {
  return (
    <>
      <h2>おすすめの楽曲:</h2>
      <div id="recommendations">
        {recommendations.length === 0 ? (
          <p>ここに楽曲が推薦されます。</p>
        ) : (
          recommendations.map((song, i) => (
            <SongItem key={i} song={song} />
          ))
        )}
      </div>
    </>
  );
}

export default RecommendationList;
