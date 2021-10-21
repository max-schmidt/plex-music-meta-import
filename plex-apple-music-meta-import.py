# Apple Music metadata (biography, album editors note, artist image) agent/ import tool for Plex

import datetime
import re
import urllib.parse
import requests
from pathlib import Path
# Local
from objects.MusicObj import MusicObj
from objects.ArtistObj import ArtistObj
from objects.AlbumObj import AlbumObj
from objects.PlexObj import PlexObj
from modules.database import ConnectDatabase, DisconnectDatabase
from modules.plex import ConnectPlex, GetPlexData, PushPlexData
from modules.lastfm_artist_agent import LastfmArtistAgent
from modules.wikipedia_artist_agent import WikipediaArtistAgent
from modules.apple_js_search import InitWebdriver, AppleArtistSearchJS, AppleAlbumSearchJS
# import beautifulsoup4 package for html parsing
try: 
    from bs4 import BeautifulSoup 
except ImportError:  
    print("No python module named 'beautifulsoup4' found.")
# import fuzzywuzzy package for better results (recommended to use fuzzywuzzy[speedup])
try:
    from fuzzywuzzy import fuzz
    #from fuzzywuzzy import process
except ImportError:
    print("No python module named 'fuzzywuzzy' found.")
# import yaml package
try:
    from ruamel.yaml import YAML
except:
    print("No python module named 'ruamel' found.")

def AgentHandler(artist_lookup_limit: int, album_lookup_limit: int):
    print("\nStart Search Agent:\n")
    # Artist Handler
    db.cursor_1.execute("SELECT uid, plex_artist, plex_text, search_result_1, search_result_2, custom_url, apple_artist_1, apple_artist_2, apple_text, select_result, lastfm_artist, lastfm_text, wiki_text, own_text, text_date, apple_image, lastfm_image, pushed_poster, apple_image_changed, ignore_wiki, search_date, ignore FROM artists ORDER BY search_date")
    for row in db.cursor_1:
        current_artist = ArtistObj(*row)
        if not current_artist.ignore:
            if current_artist.custom_url:
                GetCustomApplePage(current_artist)
            else:
                AppleArtistAgent(current_artist)

            LastfmArtistAgent(current_artist, lastfm_api_key, lastfm_api_secret,)
            if not current_artist.ignore_wiki:
                WikipediaArtistAgent(current_artist)
            
            CleanText(current_artist)

            current_artist.search_date = datetime.datetime.now()

            db.cursor_2.execute("UPDATE artists SET plex_artist=?, plex_text=?, search_result_1=?, search_result_2=?, custom_url=?, apple_artist_1=?, apple_artist_2=?, apple_text=?, select_result=?, lastfm_artist=?, lastfm_text=?, wiki_text=?, own_text=?, text_date=?, apple_image=?, lastfm_image=?, pushed_poster=?, apple_image_changed=?, ignore_wiki=?, search_date=?, ignore=? WHERE uid=?", (current_artist.plex_artist, current_artist.plex_text, current_artist.search_result_1, current_artist.search_result_2, current_artist.custom_url, current_artist.apple_artist_1, current_artist.apple_artist_2, current_artist.apple_text, current_artist.select_result, current_artist.lastfm_artist, current_artist.lastfm_text, current_artist.wiki_text, current_artist.own_text, current_artist.text_date, current_artist.apple_image, current_artist.lastfm_image, current_artist.pushed_poster, current_artist.apple_image_changed, current_artist.ignore_wiki, current_artist.search_date, current_artist.ignore, current_artist.uid))

            db.conn.commit()

        artist_lookup_limit-=1
        if artist_lookup_limit == 0:
            break

    # Album Handler
    db.cursor_1.execute("SELECT uid, plex_artist, plex_album, plex_year, plex_text, search_result_1, search_result_2, custom_url, apple_artist_1, apple_artist_2, apple_album_1, apple_album_2, apple_release_date_1, apple_release_date_2, apple_text, select_result, own_text, text_date, search_date, ignore FROM albums ORDER BY search_date")
    for row in db.cursor_1:
        current_album = AlbumObj(*row)
        if not current_album.ignore:
            if current_album.custom_url:
                GetCustomApplePage(current_album)
            else:
                AppleAlbumAgent(current_album)
            
            CleanText(current_album)

            current_album.search_date = datetime.datetime.now()

            db.cursor_2.execute("UPDATE albums SET plex_artist=?, plex_album=?, plex_year=?, plex_text=?, search_result_1=?, search_result_2=?, custom_url=?, apple_artist_1=?, apple_artist_2=?, apple_album_1=?, apple_album_2=?, apple_release_date_1=?, apple_release_date_2=?, apple_text=?, select_result=?, own_text=?, text_date=?, search_date=?, ignore=? WHERE uid=?", (current_album.plex_artist, current_album.plex_album, current_album.plex_year, current_album.plex_text, current_album.search_result_1, current_album.search_result_2, current_album.custom_url, current_album.apple_artist_1, current_album.apple_artist_2, current_album.apple_album_1, current_album.apple_album_2, current_album.apple_release_date_1, current_album.apple_release_date_2, current_album.apple_text, current_album.select_result, current_album.own_text, current_album.text_date, current_album.search_date, current_album.ignore, current_album.uid))
            
            db.conn.commit()

        album_lookup_limit-=1
        if album_lookup_limit == 0:
            break

def AppleArtistSearch(current_artist: ArtistObj, query: str):
    search_term = urllib.parse.quote_plus(query, safe="")
    apple_url = "https://itunes.apple.com/search?term=" + search_term + "&media=music&entity=musicArtist&attribute=artistTerm&country=de&lang=de_de&limit=2"
    apple_json_file = requests.get(apple_url)
    apple_json = apple_json_file.json()

    if not apple_json["resultCount"]:
        if AppleArtistSearchJS(current_artist, query, driver):
            return 1
        else:
            return 0

    try:
        current_artist.apple_artist_1 = apple_json["results"][0]["artistName"]
        current_artist.search_result_1 = apple_json["results"][0]["artistLinkUrl"]
    except:
        pass

    try:
        current_artist.apple_artist_2 = apple_json["results"][1]["artistName"]
        current_artist.search_result_2 = apple_json["results"][1]["artistLinkUrl"]
    except:
        pass

    return 1

def AppleAlbumSearch(current_album: AlbumObj, query: str):
    search_term = urllib.parse.quote_plus(query, safe="")
    apple_url = "https://itunes.apple.com/search?term=" + search_term + "&media=music&entity=album&country=de&lang=de_de&limit=2"
    apple_json_file = requests.get(apple_url)
    apple_json = apple_json_file.json()

    if not apple_json["resultCount"]:
        if AppleAlbumSearchJS(current_album, query, driver):
            return 1
        else:
            return 0

    try:
        current_album.apple_artist_1 = apple_json["results"][0]["artistName"]
        current_album.apple_album_1 = apple_json["results"][0]["collectionName"]
        current_album.search_result_1 = apple_json["results"][0]["collectionViewUrl"]
        current_album.apple_release_date_1 = apple_json["results"][0]["releaseDate"]
    except:
        pass

    try:
        current_album.apple_artist_2 = apple_json["results"][1]["artistName"]
        current_album.apple_album_2 = apple_json["results"][1]["collectionName"]
        current_album.search_result_2 = apple_json["results"][1]["collectionViewUrl"]
        current_album.apple_release_date_2 = apple_json["results"][1]["releaseDate"]
    except:
        pass

    return 1

def GetAppleArtistPage(current_artist: ArtistObj , apple_url: str, artist_id: int):
    
    if not apple_url:
        return 0
    
    try:
        apple_page = requests.get(apple_url)
    except:
        return 0
    soup = BeautifulSoup(apple_page.text, "html.parser")

    # get artist
    html = soup.find("h1", class_="artist-header__product-title-product-name")
    apple_artist = html.get_text(strip=True)
    # print("Artist: " + str(apple_artist))
    
    if artist_id==1:
        current_artist.apple_artist_1 = apple_artist
    elif artist_id==2:
        current_artist.apple_artist_2 = apple_artist

    return soup

def GetAppleAlbumPage(current_album: AlbumObj, apple_url: str, album_id: int):
    
    if not apple_url:
        return 0

    try:
        apple_page = requests.get(apple_url)
    except:
        return 0
    soup = BeautifulSoup(apple_page.text, "html.parser")
    
    # get album   
    try:
        html = soup.find("h1", class_="product-name")
        apple_album = html.get_text(strip=True)
        # print(apple_album)
    except:
        # print("Apple Page: no Album Name found.")
        return 0
    
    # get artist    
    try: 
        html = soup.find("div", class_="product-creator")
        html = html.find("a")
        apple_artist = html.get_text(strip=True)
        #print(apple_artist)
    except:
        print("Apple Page: no Album Artist found.")
        pass

    # get release date
    try:
        html = soup.find("p", class_="song-released-container")
        apple_relase_date = html.get_text(strip=True)
        # print(apple_relase_date)
    except:
        # print("Apple Page: no Release Date found.")
        pass

    if album_id==1:
        current_album.apple_album_1 = apple_album
        try:
            current_album.apple_artist_1 = apple_artist
            current_album.apple_release_date_1 = apple_relase_date
        except:
            pass
    elif album_id==2:
        current_album.apple_album_2 = apple_album
        try:
            current_album.apple_artist_2 = apple_artist
            current_album.apple_release_date_2 = apple_relase_date
        except:
            pass

    return soup

def AppleArtistAgent(current_artist: ArtistObj):
    print("Searching for " + current_artist.plex_artist)

    query = current_artist.plex_artist
    
    if not AppleArtistSearch(current_artist, query):
        return 0

    apple_soup_1 = GetAppleArtistPage(current_artist, current_artist.search_result_1, 1)
    apple_soup_2 = GetAppleArtistPage(current_artist, current_artist.search_result_2, 2)
    
    # catch rarely apple pages without any image (and text)
    if not (apple_soup_1 or apple_soup_2):
        return 0

    # decide for result
    # catch empty strings
    if not current_artist.apple_artist_1: 
        current_artist.apple_artist_1 = ""
    if not current_artist.apple_artist_2: 
        current_artist.apple_artist_2 = ""

    fuzzy1 = fuzz.ratio(current_artist.plex_artist.lower(), current_artist.apple_artist_1.lower())
    fuzzy2 = fuzz.ratio(current_artist.plex_artist.lower(), current_artist.apple_artist_2.lower())
    fuzzyp1 = fuzz.partial_ratio(current_artist.plex_artist.lower(), current_artist.apple_artist_1.lower())
    fuzzyp2 = fuzz.partial_ratio(current_artist.plex_artist.lower(), current_artist.apple_artist_2.lower())
    # choose the better result and check minimum matching
    if fuzzy1>=65 and fuzzyp1>=85:
        if fuzzy2>=65 and fuzzyp2>=85:
            if fuzzy1>=fuzzy2:
                current_artist.select_result = 1
                soup = apple_soup_1
            else:
                current_artist.select_result = 2
                soup = apple_soup_2
        else:
            current_artist.select_result = 1
            soup = apple_soup_1
    elif fuzzy2>=65 and fuzzyp2>=85:
        current_artist.select_result = 2
        soup = apple_soup_2
    else:
        return 0

    # get artist image
    GetAppleArtistImage(current_artist, soup)

    # get apple text
    if GetAppleText(current_artist, soup):
        return 1
    else:
        return 0

def AppleAlbumAgent(current_album: AlbumObj):
    print("Searching for " + current_album.plex_artist + " - " + current_album.plex_album)

    # remove some album version text for better results
    p = re.compile(r'(\s)(\(|\[).*(Deluxe|Special|Limited|Premium|Version|Edition|Japan\sDeluxe|Japan\sSpecial|Target\sDeluxe|Best\sBuy|Beatport|Extended|Expanded|Exclusive|Super|Bonus\sTrack).*(\)|\])', flags=re.IGNORECASE)
    plex_album_string = p.sub("",current_album.plex_album)

    # remove Various Artists for better results
    if current_album.plex_artist=="Various Artists":
        query = plex_album_string
    else:
        query = current_album.plex_artist + " " + plex_album_string

    if not AppleAlbumSearch(current_album, query):
        return 0

    apple_soup_1 = GetAppleAlbumPage(current_album, current_album.search_result_1, 1)
    apple_soup_2 = GetAppleAlbumPage(current_album, current_album.search_result_2, 2)

    # decide for result
    # catch empty strings
    if not current_album.apple_album_1: 
        current_album.apple_album_1 = ""
    if not current_album.apple_album_2: 
        current_album.apple_album_2 = ""

    # remove some album version text for better results
    apple_album_1_string = p.sub("_",current_album.apple_album_1)
    apple_album_2_string = p.sub("_",current_album.apple_album_2)
    p = re.compile(r'\s\(.*feat\..*\)|\s\[.*feat\..*\]|\s-\sSingle|\s-\sEP', flags=re.IGNORECASE)
    plex_album_string = p.sub("_",plex_album_string)
    apple_album_1_string = p.sub("_",apple_album_1_string)
    apple_album_2_string = p.sub("_",apple_album_2_string)

    # check numbers (importent for volume x albums etc.) (remove feat. artists before number check)
    for i in range(10):
        if (str(i) in plex_album_string and str(i) not in apple_album_1_string) or (str(i) not in plex_album_string and str(i) in apple_album_1_string):
            apple_album_1_string = ""
        if (str(i) in plex_album_string and str(i) not in apple_album_2_string) or (str(i) not in plex_album_string and str(i) in apple_album_2_string):
            apple_album_2_string = ""
    
    # stop if both candites are empty
    if apple_album_1_string == "" and apple_album_2_string == "":
        return 0

    fuzzy1 = fuzz.ratio(plex_album_string.lower(), apple_album_1_string.lower())
    fuzzy2 = fuzz.ratio(plex_album_string.lower(), apple_album_2_string.lower())
    fuzzyp1 = fuzz.partial_ratio(plex_album_string.lower(), apple_album_1_string.lower())
    fuzzyp2 = fuzz.partial_ratio(plex_album_string.lower(), apple_album_2_string.lower())
    soup_alt = 0
    # choose the better result and check minimum matching
    if fuzzy1>=65 and fuzzyp1>=85:
        if fuzzy2>=65 and fuzzyp2>=85:
            if fuzzy1>=fuzzy2:
                current_album.select_result = 1
                soup = apple_soup_1
                soup_alt = apple_soup_2
            else:
                current_album.select_result = 2
                soup = apple_soup_2
                soup_alt = apple_soup_1
        else:
            current_album.select_result = 1
            soup = apple_soup_1
    elif fuzzy2>=65 and fuzzyp2>=85:
        current_album.select_result = 2
        soup = apple_soup_2
    else:
        return 0

    # get apple text        
    if soup and GetAppleText(current_album, soup):
        return 1
    # try the other result if the first one fails
    elif soup_alt and GetAppleText(current_album, soup_alt):
        if current_album.select_result==1:
            current_album.select_result = 2
        elif current_album.select_result==2:
            current_album.select_result = 1
        return 1
    else:
        return 0

def GetCustomApplePage(current_object: MusicObj):

    if isinstance(current_object, ArtistObj):
        soup = GetAppleArtistPage(current_object, current_object.custom_url, 1)
    elif isinstance(current_object, AlbumObj):
        soup = GetAppleAlbumPage(current_object, current_object.custom_url, 1)
    else:
        return 0

    if not soup:
        return 0

    if isinstance(current_object, ArtistObj):
        GetAppleArtistImage(current_object, soup)

    if not GetAppleText(current_object, soup):
        return 0
    
    return 1

def GetAppleText(current_object: MusicObj, soup: BeautifulSoup):
    apple_text_temp = soup.find("div", class_="truncated-content-container")
    try: 
        p = re.compile(r'<(\/)?br(\s)?(\/)?>', flags=re.IGNORECASE)
        apple_text_temp = p.sub("\n",str(apple_text_temp))
        p = re.compile(r'\n{3,}', flags=re.IGNORECASE)
        apple_text_temp = p.sub("\n\n",str(apple_text_temp))
        p = re.compile(r'<(\/)?(b|i)>', flags=re.IGNORECASE)
        apple_text_temp = p.sub("",str(apple_text_temp))
        p = re.compile(r'<span.+</span>(\s)?', flags=re.IGNORECASE)
        apple_text_temp = p.sub("",str(apple_text_temp))
        soup2 = BeautifulSoup(str(apple_text_temp), "html.parser")
        apple_text_temp = soup2.find("p").string
        if apple_text_temp:
            current_object.apple_text = apple_text_temp
            # timestamp for text update
            current_object.text_date = datetime.datetime.now()
        return 1
    except:
        return 0

def GetAppleArtistImage(current_artist: ArtistObj, soup: BeautifulSoup):
    
    apple_image_found = False
    
    try:

        try:
            html = soup.find("div", class_="media-artwork-v2 media-artwork-v2--aspect-ratio circular-artwork__artwork media-artwork-v2--no-border media-artwork-v2--round")
            html = html.find("picture")
            html = html.find("source")
            apple_image_temp = html["srcset"]
            # Apple sometimes uses album covers as artist images. Images with an "/thumb/features" in the URL (nearly) always seem to be real artist images. While images with "/thumb/music" in the URL are sometimes album covers.
            if "/thumb/features" in apple_image_temp.lower():
                p = re.compile(r'\s190w,.*', flags=re.IGNORECASE)
                apple_image_temp = p.sub("",str(apple_image_temp))
                p = re.compile(r'190x190cc-60\.jpg|190x190cc\.webp', flags=re.IGNORECASE)
                apple_image_temp = p.sub("1500x1500cc-99.jpg",str(apple_image_temp))   
                apple_image_found = True    
        except:
            pass

        try:
            if not apple_image_found:
                # It looks like Apple is slowly switching to background images. These images always seem to be fine.
                html = soup.find("div", class_="artist-header--fixed")
                apple_image_temp = html["style"]
                p = re.compile(r'--background-image:\surl\(|\)\;.*', flags=re.IGNORECASE|re.DOTALL)
                apple_image_temp = p.sub("",str(apple_image_temp))
                p = re.compile(r'2400x933vf-60\.jpg|2400x933vf\.webp', flags=re.IGNORECASE)
                apple_image_temp = p.sub("1500x1500-99.jpg",str(apple_image_temp))
                apple_image_found = True
        except:
            pass

        if apple_image_found and apple_image_temp!=current_artist.apple_image:
            current_artist.apple_image = apple_image_temp
            current_artist.apple_image_changed = True
    except:
        pass

def CleanText(current_object: MusicObj):
    # print("\nCleaning text strings...\n")
    p = re.compile(r'(\s)?<a\shref.*Read\smore\son\sLast\.fm<\/a>\.|(\s)?Read\smore\son\sLast\.fm\.|(\s)?User-contributed\stext\sis\savailable\sunder\sthe\sCreative\sCommons\sBy-SA\sLicense\;\sadditional\sterms\smay\sapply(\.)?|(\s)?~\s.+|\[\d\]|\[\d\d\]', flags=re.IGNORECASE)
    
    if current_object.apple_text:
        clean_apple_text = p.sub('',str(current_object.apple_text))
        if clean_apple_text!=str(current_object.apple_text):
            current_object.apple_text = clean_apple_text
    if (isinstance(current_object,ArtistObj) and current_object.lastfm_text):
        clean_lastfm_text = p.sub('',str(current_object.lastfm_text))
        if clean_lastfm_text!=str(current_object.lastfm_text):
            current_object.lastfm_text = clean_lastfm_text

# main
print("---------------------------\nApple Music Agent for Plex.\n---------------------------")

# load yaml config
yaml = YAML(typ="safe")
yaml.default_flow_style = False
with open("config.yaml", "r") as config_file:
    config_yaml = yaml.load(config_file)
album_lookup_limit = int(config_yaml["settings"]["album_lookup_limit"])
artist_lookup_limit = int(config_yaml["settings"]["artist_lookup_limit"])
chrome_path = Path(config_yaml["settings"]["chrome_path"])
chromedriver_path = Path(config_yaml["settings"]["chromedriver_path"])
db_path = Path(config_yaml["database"]["path"])
Path(db_path.parent).mkdir(parents=True, exist_ok=True)
lastfm_api_key = str(config_yaml["lastfmAPI"]["lastfm_api_key"])
lastfm_api_secret = str(config_yaml["lastfmAPI"]["lastfm_api_secret"])
plexServer = PlexObj(config_yaml["plexAPI"]["plex_username"], config_yaml["plexAPI"]["plex_password"], config_yaml["plexAPI"]["plex_servername"], config_yaml["plexAPI"]["plex_libraryname"])

db = ConnectDatabase(db_path)
ConnectPlex(plexServer)
GetPlexData(plexServer, db)
driver = InitWebdriver(chrome_path, chromedriver_path)
AgentHandler(artist_lookup_limit, album_lookup_limit)
driver.quit()
PushPlexData(plexServer, db)
DisconnectDatabase(db)

print("\nDone!")