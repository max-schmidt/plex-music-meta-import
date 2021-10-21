import urllib.parse
from pathlib import Path
from objects.ArtistObj import ArtistObj
from objects.AlbumObj import AlbumObj
# import selenium package for dynamic website parsing
try: 
    from selenium import webdriver
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.common.by import By
except ImportError:  
    print("No python module named 'selenium' found.")
# import beautifulsoup4 package for html parsing
try: 
    from bs4 import BeautifulSoup 
except ImportError:  
    print("No python module named 'beautifulsoup4' found.")

def InitWebdriver(chrome_path: Path, chromedriver_path: Path):
    print("\nInitialize Webdriver...\n")
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    # Supress console log output
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.binary_location = str(chrome_path)
    driver = webdriver.Chrome(options=options, executable_path = str(chromedriver_path))
    return driver

def AppleArtistSearchJS(current_artist: ArtistObj, query: str, driver: WebDriver):

    search_term = urllib.parse.quote_plus(query, safe="")
    apple_url = "https://music.apple.com/de/search?term=" + search_term
    print("[slow web app search]")

    try:
        driver.get(apple_url)
        WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "dt-shelf--search-artist")))
    except:
        return 0
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    html_1 = soup.select("div.dt-shelf--search-artist ul.shelf-grid__list > li:nth-of-type(1)")
    html_2 = soup.select("div.dt-shelf--search-artist ul.shelf-grid__list > li:nth-of-type(2)")

    try:
        soup_1 = BeautifulSoup(str(html_1), "html.parser")
        html_1 = soup_1.find("a", class_="lockup__name")
        current_artist.apple_artist_1 = html_1.get_text(strip=True)
        current_artist.search_result_1 = html_1.get("href")
    except:
        pass

    try:
        soup_2 = BeautifulSoup(str(html_2), "html.parser")
        html_2 = soup_2.find("a", class_="lockup__name")
        current_artist.apple_artist_2 = html_2.get_text(strip=True)
        current_artist.search_result_2 = html_2.get("href")
    except:
        pass

    return 1

def AppleAlbumSearchJS(current_album: AlbumObj, query: str, driver: WebDriver):

    search_term = urllib.parse.quote_plus(query, safe="")
    apple_url = "https://music.apple.com/de/search?term=" + search_term
    print("[slow web app search]")

    try:
        driver.get(apple_url)
        WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "dt-shelf--search-album")))
    except:
        return 0

    soup = BeautifulSoup(driver.page_source, "html.parser")
    html_1 = soup.select("div.dt-shelf--search-album ul.shelf-grid__list > li:nth-of-type(1)")
    html_2 = soup.select("div.dt-shelf--search-album ul.shelf-grid__list > li:nth-of-type(2)")

    try:
        soup_1 = BeautifulSoup(str(html_1), "html.parser")
        html_1 = soup_1.find("a", class_="lockup__name")
        current_album.apple_album_1 = html_1.get_text(strip=True)
        print(current_album.apple_album_1)
        current_album.search_result_1 = html_1.get("href")
        html_1 = soup_1.find("a", class_="dt-link-to linkable")
        current_album.apple_artist_1 = html_1.get_text(strip=True)
    except:
        pass

    try:
        soup_2 = BeautifulSoup(str(html_2), "html.parser")
        html_2 = soup_2.find("a", class_="lockup__name")
        current_album.apple_album_2 = html_2.get_text(strip=True)
        current_album.search_result_2 = html_2.get("href")
        html_2 = soup_2.find("a", class_="dt-link-to linkable")
        current_album.apple_artist_2 = html_2.get_text(strip=True)
    except:
        pass

    return 1