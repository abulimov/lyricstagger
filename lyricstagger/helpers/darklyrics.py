"""
Helper to download lyrics from darklyrics.com
"""
from __future__ import unicode_literals
import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
import lyricstagger.log as log


class DarkLyrics:
    """Lyrics Downloader for darklyrics.com"""
    url = "http://www.darklyrics.com"

    def __init__(self):
        pass

    @staticmethod
    def parse(text, song):
        """Parse lyrics from html"""
        # parse the result
        soup = BeautifulSoup(text, "html.parser")
        lyrics_div = soup.find('div', "lyrics")
        if lyrics_div is None:
            log.debug("BeautifulSoup failed to find 'lyrics' div")
            return None

        for element in lyrics_div(text=lambda text: isinstance(text, Comment)):
            element.extract()

        lyrics = ''
        song_found = False
        for content in lyrics_div.contents:
            if content.name == "h3":
                if content.string and re.match(r"^\d+\.\s+%s$" % song, content.string):
                    song_found = True
                    continue
                else:
                    if song_found:
                        break
                    song_found = False
            if song_found:
                if isinstance(content, NavigableString):
                    lyrics += content.strip()
                elif isinstance(content, Tag):
                    if (content.string and content.name == "i" and
                            content.string.startswith("[Instrumental]")):
                        return '{{Instrumental}}'
                    elif content.name == "br":
                        lyrics += '\n'
                    if content.name not in ['script'] and content.string:
                        lyrics += content.string.strip()
        return lyrics.strip()

    @staticmethod
    def parse_artist_link(data):
        """"""

        soup = BeautifulSoup(data, "html.parser")
        cont_div = soup.find('div', "cont")
        if not cont_div:
            log.debug("BeautifulSoup failed to find 'cont' div")
            return None

        link = ""

        artists_found = False
        for content in cont_div:
            if content.name == "h3":
                if content.string and content.string == "Artists:":
                    artists_found = True
                    continue
                else:
                    if artists_found:
                        break
                    artists_found = False
            if artists_found:
                if content.name == 'a':
                    link_a = content
                else:
                    link_a = content.find('a')
                if isinstance(link_a, Tag):
                    return link_a['href']

        return link

    @staticmethod
    def parse_album_link(data, album):
        """"""

        soup = BeautifulSoup(data, "html.parser")
        album_divs = soup.find_all('div', "album")
        if not album_divs:
            log.debug("BeautifulSoup failed to find 'album' divs")
            return None

        link = ""

        album_found = False
        for div in album_divs:
            for content in div:
                if content.name == "h2":
                    if content.string:
                        possible_album = content
                    else:
                        possible_album = content.find("strong")
                    if possible_album and re.match(r'"?%s"?' % album, possible_album.string):
                        album_found = True
                        continue
                    else:
                        if album_found:
                            break
                        album_found = False
                if album_found:
                    if content.name == 'a':
                        link_a = content
                    else:
                        link_a = content.find('a')
                    if isinstance(link_a, Tag):
                        replaced = re.sub(r"#\d+|\.\.", "", link_a['href'])
                        return DarkLyrics.url + replaced

        return link

    @staticmethod
    def get_link_content(link):
        log.debug("Fetching %s" % link)
        result = requests.get(link)
        if result.status_code != 200:
            log.debug("Got code %d" % result.status_code)
            return None
        return result.text

    @staticmethod
    def fetch(artist, song, album):
        """Fetch lyrics from remote url"""
        search_page = DarkLyrics.get_link_content(DarkLyrics.url + "/search?q=" + artist)
        artist_link = DarkLyrics.parse_artist_link(search_page)
        if not artist_link:
            log.debug("Failed to find artist link")
            return None
        artist_page = DarkLyrics.get_link_content(artist_link)
        album_link = DarkLyrics.parse_album_link(artist_page, album)
        if not album_link:
            log.debug("Failed to find album link")
            return None
        album_page = DarkLyrics.get_link_content(album_link)
        if album_page:
            return DarkLyrics.parse(album_page, song)
        log.debug("Failed to parse lyrics")
        return None
