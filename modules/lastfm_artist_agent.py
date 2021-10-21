import datetime
import re
import requests
from objects.ArtistObj import ArtistObj
# import pylast package for Last.fm search
try:
    import pylast
except ImportError:
    print("No python module named 'pylast' found.")
# import fuzzywuzzy package for better results (recommended to use fuzzywuzzy[speedup])
try:
    from fuzzywuzzy import fuzz
except ImportError:
    print("No python module named 'fuzzywuzzy' found.")
# import beautifulsoup4 package for html parsing
try: 
    from bs4 import BeautifulSoup 
except ImportError:  
    print("No python module named 'beautifulsoup4' found.")

def LastfmArtistAgent(current_artist: ArtistObj, lastfm_api_key: str, lastfm_api_secret: str):
    # skip if text and image is available from apple
    if current_artist.apple_image and current_artist.apple_text and str(current_artist.apple_text)!="None" and str(current_artist.apple_text)!="":
        return 0

    lastfm = pylast.LastFMNetwork(api_key=lastfm_api_key, api_secret=lastfm_api_secret)
    try:
        artist_obj = lastfm.get_artist(current_artist.plex_artist)
        lastfm_artist_temp = artist_obj.get_name()
    except:
        return 0
  
    if fuzz.ratio(current_artist.plex_artist.lower(), lastfm_artist_temp.lower())>=65 and fuzz.partial_ratio(current_artist.plex_artist.lower(), lastfm_artist_temp.lower())>=85:
        current_artist.lastfm_artist = lastfm_artist_temp
        try:
            # get text
            lastfm_text_temp = artist_obj.get_bio_content(language="de")
            # remove credits text
            p = re.compile(r'(\s)?<a\shref.*Read\smore\son\sLast\.fm<\/a>\.|(\s)?Read\smore\son\sLast\.fm\.|(\s)?User-contributed\stext\sis\savailable\sunder\sthe\sCreative\sCommons\sBy-SA\sLicense\;\sadditional\sterms\smay\sapply\.|(\s)?~\s.+|\[\d\]|\[\d\d\]', flags=re.IGNORECASE)
            current_artist.lastfm_text = p.sub("",lastfm_text_temp)
            # timestamp for text update
            current_artist.text_date = datetime.datetime.now()

            # get image
            lastfm_url=artist_obj.get_url()
            p = re.compile(r'\/\/www\.last\.fm\/music\/', flags=re.IGNORECASE)
            lastfm_url = p.sub("//www.last.fm/music/+noredirect/",lastfm_url)
            try:
                lastfm_page = requests.get(lastfm_url)
                soup = BeautifulSoup(lastfm_page.text, "html.parser")
                current_artist.lastfm_image = soup.find(class_="header-new-background-image").get("content")
            except:
                pass

            return 1
        except:
            return 0
    else:
        return 0
