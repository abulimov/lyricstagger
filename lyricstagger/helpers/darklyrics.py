"""
Helper to download lyrics from darklyrics.com
"""
from __future__ import unicode_literals
from threading import Lock
import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
import lyricstagger.log as log


class Cache(object):
    """Simple thread-safe cache based on dict"""
    def __init__(self):
        self.dict = {}
        self.lock = Lock()

    def __getitem__(self, key):
        with self.lock:
            return self.dict[key]

    def __setitem__(self, key, value):
        with self.lock:
            self.dict[key] = value

    def __delitem__(self, key):
        with self.lock:
            del self.dict[key]

    def __contains__(self, item):
        with self.lock:
            return item in self.dict

    def set_artist_page(self, artist: str, page: str):
        if artist in self:
            self[artist]["page"] = page
        else:
            self[artist] = dict(page=page, album_pages=dict())

    def get_artist_page(self, artist: str) -> str:
        if artist in self:
            return self[artist]["page"]
        else:
            return ""

    def has_artist(self, artist: str) -> bool:
        return artist in self

    def get_album_page(self, artist: str, album: str) -> str:
        if artist in self:
            if album in self[artist]["album_pages"]:
                return self[artist]["album_pages"][album]

        return None

    def set_album_page(self, artist: str, album: str, page: str):
        if artist in self:
            self[artist]["album_pages"][album] = page
        else:
            self[artist] = dict(page="", album_pages=dict(album=page))

    def has_album_page(self, artist, album):
        if artist in self:
            if album in self[artist]["album_pages"]:
                return True
        return False


class DarkLyrics(object):
    """Lyrics Downloader for darklyrics.com"""
    url = "http://www.darklyrics.com"

    def __init__(self):
        self.cache = Cache()

    @staticmethod
    def parse(text: str, song: str) -> str:
        """Parse lyrics from html"""
        # parse the result
        soup = BeautifulSoup(text, "html.parser")
        lyrics_div = soup.find('div', "lyrics")
        if lyrics_div is None:
            log.debug("BeautifulSoup failed to find 'lyrics' div")
            return None

        for element in lyrics_div(text=lambda txt: isinstance(txt, Comment)):
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
    def parse_artist_link(data: str) -> str:
        """Parse search page and return link to artist page"""

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
    def parse_album_link(data: str, album: str) -> str:
        """Parse artist page and return link to album page"""

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
    def get_link_content(link: str) -> str:
        """Perform request and return response text or None"""
        log.debug("Fetching %s" % link)
        result = requests.get(link)
        if result.status_code != 200:
            log.debug("Got code %d" % result.status_code)
            return None
        return result.text

    def _get_artist_page(self, artist: str) -> str:
        if self.cache.has_artist(artist):
            page = self.cache.get_artist_page(artist)
            if page:
                log.debug("Found artist '%s' page in cache" % artist)
                return page
            else:
                log.debug("Skipping artist '%s' because we know it's missing on website" % artist)
                return None
        else:
            search_page = self.get_link_content(DarkLyrics.url + "/search?q=" + artist)
            artist_link = self.parse_artist_link(search_page)
            if not artist_link:
                log.debug("Failed to find artist link")
                # mark this artist in cache as unavailable
                self.cache.set_artist_page(artist, "")
                return None
            artist_page = self.get_link_content(artist_link)
            log.debug("Adding artist '%s' page to cache" % artist)
            self.cache.set_artist_page(artist, artist_page)
            return artist_page

    def _get_album_page(self, artist: str, album: str) -> str:
        if self.cache.has_album_page(artist, album):
            album_page = self.cache.get_album_page(artist, album)
            if album_page:
                log.debug("Found album '%s' page in cache" % album)
                return album_page
            else:
                log.debug("Skipping album '%s' because we know it's missing on website" % artist)
                return None
        else:
            artist_page = self._get_artist_page(artist)
            if artist_page:
                album_link = self.parse_album_link(artist_page, album)
                if not album_link:
                    log.debug("Failed to find album link")
                    # mark this album in cache as unavailable
                    self.cache.set_album_page(artist, album, "")
                    return None
                album_page = self.get_link_content(album_link)
                log.debug("Adding album '%s' page to cache" % album)
                self.cache.set_album_page(artist, album, album_page)
                return album_page
            else:
                return None

    def fetch(self, artist: str, song: str, album: str) -> str:
        """Fetch lyrics from remote url"""

        album_page = self._get_album_page(artist, album)
        if album_page:
            log.debug("Parsing lyrics for '{0}' - '{1}'".format(artist, song))
            return DarkLyrics.parse(album_page, song)
        log.debug("Failed to parse lyrics")
        return None
