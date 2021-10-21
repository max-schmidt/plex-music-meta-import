from objects.DatabaseObj import DatabaseObj
from objects.PlexObj import PlexObj
# import plexapi package for plex connection
try:
    from plexapi.myplex import MyPlexAccount
except ImportError:
    print("No python module named 'plexapi' found.")

def ConnectPlex(plexServer: PlexObj):
    print("\nConnecting to Plex server...\n")
    account = MyPlexAccount(plexServer.plex_username, plexServer.plex_password)
    try:
        plexServer.plex_connection = account.resource(plexServer.plex_servername).connect()
        return 1
    except Exception:
        print("Can not connect to Plex server.")  
        raise

def GetPlexData(plexServer: PlexObj, db: DatabaseObj):
    print("\nScanning Plex server...\n")
    music_lib = plexServer.plex_connection.library.section(plexServer.plex_libraryname)
    for plexartist in music_lib.searchArtists():
        db.cursor_1.execute("INSERT OR IGNORE INTO artists(uid, plex_artist, plex_text) VALUES (?,?,?)", (plexartist.ratingKey, plexartist.title, plexartist.summary))
        db.cursor_1.execute("UPDATE artists SET plex_artist=?, plex_text=? WHERE uid=?", (plexartist.title, plexartist.summary, plexartist.ratingKey))
    db.conn.commit()
    for plexalbum in music_lib.searchAlbums():
        db.cursor_1.execute("INSERT OR IGNORE INTO albums(uid, plex_artist, plex_album, plex_year, plex_text) VALUES (?,?,?,?,?)", (plexalbum.ratingKey, plexalbum.parentTitle, plexalbum.title, plexalbum.year, plexalbum.summary))
        db.cursor_1.execute("UPDATE albums SET plex_artist=?, plex_album=?, plex_year=?, plex_text=? WHERE uid=?", (plexalbum.parentTitle, plexalbum.title, plexalbum.year, plexalbum.summary, plexalbum.ratingKey))
    db.conn.commit()

def PushPlexData(plexServer: PlexObj, db: DatabaseObj):
    print("\nPushing data to Plex server...\n")
    music_lib = plexServer.plex_connection.library.section(plexServer.plex_libraryname)

    for plexartist in music_lib.searchArtists():
        plex_text, apple_text, own_text, lastfm_text, wiki_text, apple_image, lastfm_image, apple_image_changed, pushed_poster = db.cursor_1.execute("SELECT plex_text, apple_text, own_text, lastfm_text, wiki_text, apple_image, lastfm_image, apple_image_changed, pushed_poster FROM artists WHERE uid=?", (plexartist.ratingKey,)).fetchone()        
        # prio 1: use own text
        if own_text and str(own_text)!="None" and str(own_text)!="":
            if plex_text!=own_text:
                args = {
                    'summary.value': own_text,
                    'summary.locked': 1,
                    }
                print("Updating Text (Own): " + plexartist.title)
                plexartist.edit(**args)            
        # prio 2: use new apple text
        elif apple_text and str(apple_text)!="None" and str(apple_text)!="":
            if plex_text!=apple_text:
                args = {
                    'summary.value': apple_text,
                    'summary.locked': 1,
                    }
                print("Updating Text (Apple): " + plexartist.title)
                plexartist.edit(**args)
        # prio 3: use new last.fm text
        elif lastfm_text and str(lastfm_text)!="None" and str(lastfm_text)!="":
            if plex_text!=lastfm_text:
                args = {
                    'summary.value': lastfm_text,
                    'summary.locked': 1,
                    }
                print("Updating Text (Last.fm): " + plexartist.title)
                plexartist.edit(**args)
        # prio 4: use new wikipedia text
        elif wiki_text and str(wiki_text)!="None" and str(wiki_text)!="":
            if plex_text!=wiki_text:
                args = {
                    'summary.value': wiki_text,
                    'summary.locked': 1,
                    }
                print("Updating Text (Wikipedia): " + plexartist.title)
                plexartist.edit(**args)
       
        # get current active image in plex
        image_uploaded = False
        current_poster = False
        posters = plexartist.posters()
        for poster in posters:
            if int(poster.selected):
                current_poster = poster.ratingKey
        # update artist image, if there is a new one
        if apple_image_changed and apple_image:
            print("Updating Poster (Apple): " + plexartist.title)
            plexartist.uploadPoster(url=apple_image)
            image_uploaded = True
        # push Last.fm image only once (because they change all the time)
        elif lastfm_image and not apple_image and (not current_poster or "com.plexapp.agents.lastfm" in current_poster):
            print("Updating Poster (Last.fm): " + plexartist.title)
            plexartist.uploadPoster(url=lastfm_image)
            image_uploaded = True
        # remember the new uploaded poster
        if image_uploaded:
            posters = plexartist.posters()
            for poster in posters:
                if int(poster.selected):
                    db.cursor_1.execute("UPDATE artists SET pushed_poster=? WHERE uid=?", (poster.ratingKey, plexartist.ratingKey,))
        db.cursor_1.execute("UPDATE artists SET apple_image_changed=False WHERE uid=?", (plexartist.ratingKey,))

    for plexalbum in music_lib.searchAlbums():
        plex_text, apple_text, own_text = db.cursor_1.execute("SELECT plex_text, apple_text, own_text FROM albums WHERE uid=?", (plexalbum.ratingKey,)).fetchone()    
        # prio 1: use own text
        if own_text and str(own_text)!="None" and str(own_text)!="":
            if plex_text!=own_text:
                args = {
                    'summary.value': own_text,
                    'summary.locked': 1,
                    }
                print("Updating Text (Own): " + plexalbum.parentTitle + " - " + plexalbum.title)
                plexalbum.edit(**args)            
        # prio 2: use new apple text
        elif apple_text and str(apple_text)!="None" and str(apple_text)!="":
            if plex_text!=apple_text:
                args = {
                    'summary.value': apple_text,
                    'summary.locked': 1,
                    }
                print("Updating Text (Apple): " + plexalbum.parentTitle + " - " + plexalbum.title)
                plexalbum.edit(**args)             
