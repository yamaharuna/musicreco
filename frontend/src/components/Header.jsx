import React from 'react';

function Header() {
  return (
    <header>
      <div className="header-left">
        <span className="material-symbols-outlined">music_cast</span>
        <h1><a href="/">MusicReco</a></h1>
      </div>
      <nav>
        <a href="/about">About</a>
      </nav>
    </header>
  );
}

export default Header;
