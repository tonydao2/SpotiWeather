previous playlists

CREATE DATABASE IF NOT EXISTS spotiweather;

CREATE TABLE playlists {
    playlist_id int AUTOINCREMENT,
    date
    PRIMARY KEY (id)
    };

CREATE TABLE playlist_songs {
    song_id int AUTOINCREMENT,
    playlist_id int,
    name varchar(255),
    PRIMARY KEY (song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    };

CREATE TABLE playlist_artists {
    artist_id int AUTOINCREMENT,
    playlist_id int,
    name varchar(255),
    PRIMARY KEY (artist_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    };