import React from 'react';

function SongItem({ song }) {
  const trackId = song.spotify_link ? song.spotify_link.split('/track/')[1] : null;

  return (
    <div className="song-item">
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
}

export default SongItem;
