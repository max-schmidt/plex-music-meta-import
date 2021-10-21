import datetime
import re
from objects.ArtistObj import ArtistObj
# import wikipedia package
try:
    import wikipedia
except ImportError:
    print("No python module named 'wikipedia' found.")
# import fuzzywuzzy package for better results (recommended to use fuzzywuzzy[speedup])
try:
    from fuzzywuzzy import fuzz
except ImportError:
    print("No python module named 'fuzzywuzzy' found.")

def WikipediaArtistAgent(current_artist: ArtistObj):
    # skip if text is available from apple or last.fm
    if (current_artist.apple_text and str(current_artist.apple_text)!="None" and str(current_artist.apple_text)!="") or (current_artist.lastfm_text and str(current_artist.lastfm_text)!="None" and str(current_artist.lastfm_text)!=""):
        return 0
    
    wikipedia.set_lang("de")
    try:
        page_title = wikipedia.search(current_artist.plex_artist)[0]
    except:
        return 0
    
    # remove brackets for comparison
    p = re.compile(r'(\s)?(\(|\[).*(\)|\])', flags=re.IGNORECASE)
    page_title_compare = p.sub("",page_title)

    if fuzz.ratio(current_artist.plex_artist.lower(), page_title_compare.lower())>=65 and fuzz.partial_ratio(current_artist.plex_artist.lower(), page_title_compare.lower())>=85:
        try:
            current_artist.wiki_text = wikipedia.summary(page_title)
            # timestamp for text update
            current_artist.text_date = datetime.datetime.now()
            return 1
        except:
            return 0
    else:
        return 0
