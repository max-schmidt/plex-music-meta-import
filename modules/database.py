import sqlite3
from pathlib import Path
from objects.DatabaseObj import DatabaseObj

def ConnectDatabase(db_path: Path):
    try:
        conn = sqlite3.connect(db_path)
    except Exception:
        print("Can not connect to database file.") 
        raise   
    cursor_1 = conn.cursor()
    cursor_2 = conn.cursor()
    cursor_1.execute('''CREATE TABLE IF NOT EXISTS artists (
                    uid int PRIMARY KEY,
                    plex_artist text,
                    plex_text text,
                    search_result_1 text,
                    search_result_2 text,
                    custom_url text,
                    apple_artist_1 text,
                    apple_artist_2 text,
                    apple_text text,
                    select_result int,
                    lastfm_artist text,
                    lastfm_text text,
                    wiki_text text,
					own_text text,
                    text_date text,
                    apple_image text,
                    lastfm_image text,
                    pushed_poster text,
                    apple_image_changed boolean DEFAULT 0,
                    ignore_wiki boolean DEFAULT 0,
					search_date text,
                    ignore boolean DEFAULT 0
                )''')
    cursor_1.execute('''CREATE TABLE IF NOT EXISTS albums (
                    uid int PRIMARY KEY,
                    plex_artist text,
					plex_album text,
                    plex_year int,
                    plex_text text,
                    search_result_1 text,
                    search_result_2 text,
                    custom_url text,
                    apple_artist_1 text,
                    apple_artist_2 text,
					apple_album_1 text,
                    apple_album_2 text,
                    apple_release_date_1 text,
                    apple_release_date_2 text,
                    apple_text text,
                    select_result int,
                    own_text text,
                    text_date text,
					search_date text,
                    ignore boolean DEFAULT 0
                )''')
    return DatabaseObj(conn, cursor_1, cursor_2)

def DisconnectDatabase(db: DatabaseObj):
    db.conn.commit()
    db.conn.close()
